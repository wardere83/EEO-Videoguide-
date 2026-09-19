// Support the repository's existing branch-based GitHub Pages hosting as well
// as the Actions dist deployment. Only generated public paths are overwritten.
import { cpSync, mkdirSync, rmSync } from 'node:fs';
import { resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
for (const dir of ['assets', 'brand', 'fonts', 'media']) {
  rmSync(resolve(root, dir), { recursive: true, force: true });
  mkdirSync(resolve(root, dir), { recursive: true });
  cpSync(resolve(root, 'dist', dir), resolve(root, dir), { recursive: true });
}
for (const file of ['index.html', '404.html', 'CNAME']) {
  cpSync(resolve(root, 'dist', file), resolve(root, file));
}
