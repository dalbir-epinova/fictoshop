import fs from "node:fs";
import path from "node:path";

function findRepositoryRoot(): string {
  let candidate = process.cwd();
  while (true) {
    if (fs.existsSync(path.join(candidate, "manage.py"))) {
      return candidate;
    }
    const parent = path.dirname(candidate);
    if (parent === candidate) {
      throw new Error("Could not locate the Fictoshop repository root containing manage.py.");
    }
    candidate = parent;
  }
}

const root = findRepositoryRoot();

export const projectPaths = {
  root,
  python: path.join(root, ".venv", "bin", "python"),
  managePy: path.join(root, "manage.py")
};
