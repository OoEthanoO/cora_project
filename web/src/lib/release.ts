import manifest from "./release.json";

/**
 * Where the installer is served from. Point NEXT_PUBLIC_DOWNLOAD_URL at a
 * GitHub release asset when deploying, so the 120 MB binary doesn't have to
 * live in the repository. Falls back to the copy staged into public/.
 */
const hostedUrl = process.env.NEXT_PUBLIC_DOWNLOAD_URL;

export const release = {
  ...manifest,
  downloadUrl: hostedUrl || `/downloads/${manifest.filename}`,
  sizeLabel: `${Math.round(manifest.sizeBytes / 1024 ** 2)} MB`,
};

export const repoUrl = "https://github.com/OoEthanoO/cora_project";
