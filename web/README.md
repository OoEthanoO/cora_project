# CORA website

Marketing and download site for the Coastal Risk Analyzer, built with Next.js
(App Router) and Tailwind CSS.

## Development

```bash
npm install
npm run dev
```

## Keeping the download in sync

The site reads the installer's version, size and checksum from
`src/lib/release.json`, which is generated from the built disk image. After
running `./build_macos.sh` in the project root:

```bash
npm run stage-release
```

This copies `dist/CORA-<version>.dmg` into `public/downloads/` and rewrites the
manifest, so the version badge, file size and SHA-256 shown on the page always
describe the file people actually receive.

The staged `.dmg` is git-ignored — a 120 MB binary does not belong in the
repository.

## Deploying

Production is [cora.ethanyanxu.com](https://cora.ethanyanxu.com), served by the
existing Caddy service on the Windows home server `finprint-host`. Next.js
exports static files to `out/`; no Node.js process runs on the server.
Images are served directly from `public/`. `next start` does not support this
export mode; use `npm run dev` for local development.

From this `web/` directory on a Windows PC with Node.js, Git, OpenSSH and
access to the `finprint-host` SSH alias:

```powershell
npm run deploy
# Restore the preceding deployed release:
npm run deploy -- -Rollback
```

Commit changes first. Deployment installs the lockfile dependencies, checks
the GitHub installer's size/checksum against `src/lib/release.json`, lints,
builds, checks the export, and uploads a SHA-256-verified archive. It sets
`NEXT_PUBLIC_SITE_URL` to the production origin and `NEXT_PUBLIC_DOWNLOAD_URL`
to the matching GitHub release asset. The installer remains on GitHub;
the server receives only the website's static files.

Releases and deployment state live under `C:\ProgramData\CORA`. Activation
validates the shared Caddy configuration before reloading it, checks a
loopback-only endpoint on port 4186, and verifies the commit through HTTPS
with certificate validation. Configuration is restored if activation fails.
The final deployment check requires public `/version.txt` to match the active
commit and `X-CORA-Host: finprint-host`. Old releases are retained for rollback.
Caddy's existing SYSTEM startup task also starts CORA after a reboot.

For the initial Vercel migration only, use `npm run deploy -- -MigrateDns`.
After the local preflight passes, this adds a DNS-only Cloudflare CNAME from
`cora.ethanyanxu.com` to `finprint.ethanyanxu.com`, following the existing home
IP updater. The shared Cloudflare credential stays protected on the host.
The previous wildcard and the new record ID are saved in
`C:\ProgramData\CORA\dns-migration.json`. A failed initial HTTPS check removes
the newly added DNS override and restores Caddy. Normal deployments and
`-Rollback` do not modify DNS.

Logs are in `C:\ProgramData\CORA\logs`. If public verification fails after
successful activation, check DNS propagation before retrying. To undo only
the migration's DNS override, run `C:\ProgramData\CORA\dns.ps1 -Rollback`
in elevated PowerShell on the host; it refuses to remove a changed record.

## Updating the screenshot

`public/img/cora-screenshot.png` is a real CORA run over South Miami-Dade at
1.5 m sea level rise. If you regenerate it, update the figures in
`src/components/CaseStudy.tsx` to match the new run — they are presented as
measured output, not illustration.
