import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";

if (existsSync("odoo/odoo-bin")) {
  console.log("Odoo source already exists in ./odoo; leaving it unchanged.");
  process.exit(0);
}

const result = spawnSync("git", [
  "clone",
  "--branch", "19.0",
  "--single-branch",
  "https://github.com/odoo/odoo.git",
  "odoo",
], { stdio: "inherit", shell: false });

if (result.error) {
  console.error(`Unable to clone Odoo Community: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
