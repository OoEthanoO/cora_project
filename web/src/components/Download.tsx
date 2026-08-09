import { release, repoUrl } from "@/lib/release";
import { AppleIcon, ArrowIcon, CheckIcon, LockIcon } from "./icons";

const requirements = [
  "macOS 11 (Big Sur) or later",
  "Apple Silicon Mac (M1 or newer)",
  "About 350 MB of free disk space",
  "Internet access for OpenStreetMap, tidal and population data",
];

export function Download() {
  return (
    <section id="download" className="border-t border-line/60 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Download CORA
          </h2>
          <p className="mt-4 text-lg text-muted text-pretty">
            One disk image, no installer wizard, no dependencies to resolve.
            Python and every geospatial library it needs are already inside the
            app.
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-5">
          <div className="rounded-2xl border border-tide/30 bg-gradient-to-b from-surface to-deep p-8 lg:col-span-3">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="text-xl font-semibold tracking-tight">
                  CORA {release.version} for macOS
                </h3>
                <p className="mt-1 text-sm text-faint">
                  {release.filename} · {release.sizeLabel} · released{" "}
                  {release.releasedAt}
                </p>
              </div>
              <span className="rounded-full border border-shoal/30 bg-shoal/10 px-3 py-1 text-xs font-medium text-shoal">
                Latest
              </span>
            </div>

            <a
              href={release.downloadUrl}
              className="group mt-7 inline-flex w-full items-center justify-center gap-2.5 rounded-xl bg-tide px-6 py-4 font-medium text-abyss shadow-lg shadow-tide/20 transition-colors hover:bg-tide-bright"
            >
              <AppleIcon className="size-5" />
              Download the disk image
              <ArrowIcon className="size-4 transition-transform group-hover:translate-x-0.5" />
            </a>

            <div className="mt-7">
              <p className="text-xs font-medium tracking-wide text-faint uppercase">
                SHA-256 checksum
              </p>
              <code className="mt-2 block overflow-x-auto rounded-lg border border-line bg-abyss/70 px-3.5 py-3 font-mono text-xs break-all text-muted">
                {release.sha256}
              </code>
              <p className="mt-2 text-xs text-faint">
                Verify with{" "}
                <code className="font-mono text-muted">
                  shasum -a 256 {release.filename}
                </code>
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-line bg-deep p-8 lg:col-span-2">
            <h3 className="font-semibold tracking-tight">Requirements</h3>
            <ul className="mt-5 space-y-3">
              {requirements.map((item) => (
                <li key={item} className="flex gap-3 text-[15px] text-muted">
                  <CheckIcon className="mt-0.5 size-4 shrink-0 text-shoal" />
                  <span className="text-pretty">{item}</span>
                </li>
              ))}
            </ul>
            <p className="mt-6 border-t border-line pt-5 text-sm text-faint text-pretty">
              On an Intel Mac, Windows or Linux, run CORA from source instead —
              see the{" "}
              <a
                href={repoUrl}
                className="text-tide underline-offset-4 hover:underline"
              >
                repository
              </a>{" "}
              for the four-line setup.
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-warn/25 bg-warn/[0.06] p-7">
          <div className="flex gap-4">
            <LockIcon className="mt-0.5 size-5 shrink-0 text-warn" />
            <div>
              <h3 className="font-semibold tracking-tight text-warn">
                First launch: macOS will block the app
              </h3>
              <p className="mt-2 max-w-3xl text-[15px] leading-relaxed text-muted text-pretty">
                CORA is not signed with a paid Apple Developer ID, so Gatekeeper
                refuses to open it on the first try and offers only a{" "}
                <span className="text-ink">Move to Trash</span> button. This is
                expected for independent software and does not mean anything is
                wrong with the download — verify the checksum above if you want
                certainty. To open it:
              </p>
              <ol className="mt-4 space-y-2 text-[15px] text-muted">
                {[
                  "Drag CORA.app into your Applications folder.",
                  "Right-click (or Control-click) the app and choose Open.",
                  "Click Open again in the dialog that appears.",
                ].map((step, i) => (
                  <li key={step} className="flex gap-3">
                    <span className="font-mono text-sm text-warn">{i + 1}.</span>
                    <span className="text-pretty">{step}</span>
                  </li>
                ))}
              </ol>
              <p className="mt-4 text-sm text-faint">
                You only need to do this once. Settings, downloaded elevation
                tiles and caches are stored in{" "}
                <code className="font-mono text-muted">
                  ~/Library/Application Support/CORA
                </code>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
