/**
 * Copies the built installer into public/downloads and records its metadata
 * (version, size, checksum) so the site can display accurate download details.
 *
 * Usage: npm run stage-release
 */
import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { copyFile, mkdir, readdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const projectRoot = path.resolve(webRoot, "..");
const distDir = path.join(projectRoot, "dist");
const publicDownloads = path.join(webRoot, "public", "downloads");
const manifestPath = path.join(webRoot, "src", "lib", "release.json");

function sha256(file) {
  return new Promise((resolve, reject) => {
    const hash = createHash("sha256");
    createReadStream(file)
      .on("error", reject)
      .on("data", (chunk) => hash.update(chunk))
      .on("end", () => resolve(hash.digest("hex")));
  });
}

const entries = await readdir(distDir).catch(() => {
  throw new Error(`No dist/ directory at ${distDir}. Run ./build_macos.sh first.`);
});

const dmg = entries.filter((f) => f.endsWith(".dmg")).sort().pop();
if (!dmg) {
  throw new Error("No .dmg found in dist/. Run ./build_macos.sh first.");
}

const source = path.join(distDir, dmg);
const { size } = await stat(source);
const checksum = await sha256(source);
const version = dmg.match(/CORA-(.+)\.dmg$/)?.[1] ?? "unknown";

await mkdir(publicDownloads, { recursive: true });
await copyFile(source, path.join(publicDownloads, dmg));

const manifest = {
  version,
  filename: dmg,
  sizeBytes: size,
  sha256: checksum,
  releasedAt: new Date().toISOString().slice(0, 10),
};

await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

console.log(`Staged ${dmg} (${(size / 1024 ** 2).toFixed(0)} MB)`);
console.log(`sha256 ${checksum}`);
console.log(`Manifest written to ${path.relative(webRoot, manifestPath)}`);
