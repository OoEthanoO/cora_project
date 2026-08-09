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

The page is fully static (`next build` prerenders it), so any static host
works.

Because the installer is too large to commit, host it separately — a GitHub
release asset is the simplest option — and point the site at it:

```bash
NEXT_PUBLIC_SITE_URL=https://your-domain.example
NEXT_PUBLIC_DOWNLOAD_URL=https://github.com/OoEthanoO/cora_project/releases/download/v0.5.0/CORA-0.5.0.dmg
```

`NEXT_PUBLIC_DOWNLOAD_URL` overrides the local `public/downloads/` path used in
development. `NEXT_PUBLIC_SITE_URL` sets the canonical origin used for Open
Graph image URLs.

## Updating the screenshot

`public/img/cora-screenshot.png` is a real CORA run over South Miami-Dade at
1.5 m sea level rise. If you regenerate it, update the figures in
`src/components/CaseStudy.tsx` to match the new run — they are presented as
measured output, not illustration.
