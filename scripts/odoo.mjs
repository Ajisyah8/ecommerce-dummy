import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import process from "node:process";

const command = process.argv[2] || "help";
const requestedModules = process.argv[3] || "ecommerce_custom";
const initialModules = process.env.ODOO_INIT_MODULES ||
  "base,web,website_sale,payment_custom,ecommerce_custom";

function runDocker(args, env = {}) {
  if (!existsSync(".env")) {
    console.error("Missing .env. Run: npm run setup-env");
    process.exit(1);
  }

  const result = spawnSync("docker", ["compose", ...args], {
    stdio: "inherit",
    env: { ...process.env, ...env },
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to run Docker: ${result.error.message}`);
    console.error("Install Docker Desktop and ensure docker compose is available.");
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function ensureEnv() {
  if (!existsSync(".env")) {
    console.error("Missing .env. Copy .env.example to .env and set local passwords first.");
    process.exit(1);
  }
}

function readEnvFile() {
  ensureEnv();
  const values = {};
  for (const line of readFileSync(".env", "utf8").split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (match) values[match[1]] = match[2].replace(/^['"]|['"]$/g, "");
  }
  return values;
}

function nativeConfig() {
  const fileEnv = readEnvFile();
  const env = { ...fileEnv, ...process.env };
  const root = resolve(".");
  const runtime = join(root, ".odoo-runtime");
  mkdirSync(join(runtime, "data"), { recursive: true });
  const configPath = join(runtime, "odoo.conf");
  const config = `[options]\n` +
    `admin_passwd = ${env.ODOO_ADMIN_PASSWORD || ""}\n` +
    `db_host = ${env.POSTGRES_HOST || "localhost"}\n` +
    `db_port = ${env.POSTGRES_PORT || "5432"}\n` +
    `db_user = ${env.POSTGRES_USER || "odoo"}\n` +
    `db_password = ${env.POSTGRES_PASSWORD || ""}\n` +
    `db_name = ${env.POSTGRES_DB || "odoo"}\n` +
    `addons_path = ${join(root, "odoo", "odoo", "addons")},${join(root, "odoo", "addons")},${join(root, "custom_addons")}\n` +
    `http_port = ${env.ODOO_HTTP_PORT || "8077"}\n` +
    `http_interface = 127.0.0.1\n` +
    `dbfilter = ^${env.POSTGRES_DB || "odoo"}$\n` +
    `data_dir = ${join(runtime, "data")}\n` +
    `list_db = True\nlog_level = info\n`;
  writeFileSync(configPath, config, "utf8");
  const localPython = process.platform === "win32"
    ? join(root, ".venv", "Scripts", "python.exe")
    : join(root, ".venv", "bin", "python");
  return {
    env,
    configPath,
    database: env.POSTGRES_DB || "odoo",
    python: env.ODOO_PYTHON || (existsSync(localPython) ? localPython : (process.platform === "win32" ? "python" : "python3")),
  };
}

function runNative(extraArgs = []) {
  const settings = nativeConfig();
  const result = spawnSync(settings.python, [join("odoo", "odoo-bin"), `--config=${settings.configPath}`, ...extraArgs], {
    stdio: "inherit",
    env: { ...process.env, ...settings.env, PYTHONUTF8: "1" },
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to run local Odoo: ${result.error.message}`);
    console.error("Install Python, PostgreSQL, and Odoo requirements first.");
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function selectTheme(themeName) {
  const settings = nativeConfig();
  const result = spawnSync(settings.python, [
    join("scripts", "select_theme.py"),
    settings.database,
    themeName,
    settings.configPath,
  ], {
    stdio: "inherit",
    env: { ...process.env, ...settings.env, PYTHONUTF8: "1" },
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to select theme: ${result.error.message}`);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function seedStock() {
  const settings = nativeConfig();
  const result = spawnSync(settings.python, [
    join("scripts", "seed_stock.py"),
    settings.database,
    settings.configPath,
  ], {
    stdio: "inherit",
    env: { ...process.env, ...settings.env, PYTHONUTF8: "1" },
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to seed stock: ${result.error.message}`);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function seedImages() {
  const settings = nativeConfig();
  const result = spawnSync(settings.python, [
    join("scripts", "seed_images.py"),
    settings.database,
    settings.configPath,
  ], {
    stdio: "inherit",
    env: { ...process.env, ...settings.env, PYTHONUTF8: "1" },
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to seed product images: ${result.error.message}`);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

switch (command) {
  case "setup-env":
    if (existsSync(".env")) {
      console.log(".env already exists; leaving it unchanged.");
    } else {
      copyFileSync(".env.example", ".env");
      console.log("Created .env from .env.example. Review local passwords before starting.");
    }
    break;
  case "build":
    ensureEnv();
    runDocker(["build"]);
    break;
  case "bootstrap":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo", "--stop-after-init", "--init", initialModules]);
    runNative();
    console.log("Odoo is available at http://localhost:8077");
    break;
  case "dev":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo"]);
    console.log("Odoo is available at http://localhost:8077");
    break;
  case "odoo":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo"]);
    console.log("Odoo is available at http://localhost:8077");
    break;
  case "start":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo"]);
    break;
  case "migrate":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo", "--stop-after-init", "--update", requestedModules]);
    break;
  case "init":
    runNative(["-d", readEnvFile().POSTGRES_DB || "odoo", "--stop-after-init", "--init", requestedModules]);
    break;
  case "theme":
    selectTheme(requestedModules);
    break;
  case "seed":
    seedStock();
    break;
  case "images":
    seedImages();
    break;
  case "logs":
    ensureEnv();
    runDocker(["logs", "-f", "odoo"]);
    break;
  case "stop":
    ensureEnv();
    runDocker(["down"]);
    break;
  case "restart":
    ensureEnv();
    runDocker(["restart", "odoo"]);
    break;
  case "validate":
    nativeConfig();
    console.log("Native Odoo configuration generated successfully.");
    break;
  default:
    console.log(`
Odoo Community local workflow:

  npm run bootstrap                  Initialize database and start Odoo
  npm run odoo                       Start Odoo natively on port 8077
  npm run dev                        Start Odoo natively
  npm run migrate                    Update ecommerce_custom
  npm run migrate -- website_sale    Update selected modules
  npm run init -- base,web,...       Install selected modules
  npm run theme -- theme_ecommerce_modern  Select a Community theme
  npm run seed                       Seed demo product inventory
  npm run images                     Attach local product photos
  npm run validate                   Generate native Odoo configuration

URL: http://localhost:8077
`);
}
