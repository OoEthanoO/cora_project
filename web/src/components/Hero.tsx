import Image from "next/image";
import { release, repoUrl } from "@/lib/release";
import { AppleIcon, ArrowIcon } from "./icons";

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden">
      <div className="contours absolute inset-0 -z-20" />
      <div className="grid-lines absolute inset-0 -z-10" />

      <div className="mx-auto max-w-6xl px-6 pt-20 pb-16 sm:pt-28">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-line bg-surface/60 px-3 py-1 text-xs font-medium text-muted">
            <span className="size-1.5 rounded-full bg-shoal" />
            Version {release.version} — now available for macOS
          </span>

          <h1 className="mt-6 text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
            See which coastlines go under —{" "}
            <span className="text-tide-bright">before they do.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted text-pretty">
            CORA is a desktop coastal risk analyzer. Load elevation data for any
            shoreline, run sea level rise scenarios, and measure what floods —
            buildings, hospitals, roads and people — then test whether a sea wall
            or restored wetland actually helps.
          </p>

          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <a
              href={release.downloadUrl}
              className="group inline-flex w-full items-center justify-center gap-2.5 rounded-xl bg-tide px-6 py-3.5 font-medium text-abyss shadow-lg shadow-tide/20 transition-colors hover:bg-tide-bright sm:w-auto"
            >
              <AppleIcon className="size-5" />
              Download for macOS
              <ArrowIcon className="size-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href={repoUrl}
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-line bg-surface/60 px-6 py-3.5 font-medium text-ink transition-colors hover:border-tide/50 hover:bg-surface sm:w-auto"
            >
              View source
            </a>
          </div>

          <p className="mt-4 text-sm text-faint">
            {release.sizeLabel} · Apple Silicon · macOS 11 or later · free and
            open source
          </p>
        </div>

        <figure className="mt-16 sm:mt-20">
          <div className="rounded-xl border border-line bg-surface/40 p-1.5 shadow-2xl shadow-black/60">
            <div className="flex items-center gap-1.5 px-3 py-2">
              <span className="size-2.5 rounded-full bg-[#ff5f57]" />
              <span className="size-2.5 rounded-full bg-[#febc2e]" />
              <span className="size-2.5 rounded-full bg-[#28c840]" />
              <span className="ml-3 text-xs text-faint">
                CORA — Coastal Risk Analyzer
              </span>
            </div>
            <Image
              src="/img/cora-screenshot.png"
              alt="The CORA desktop application showing a flood inundation map of South Miami-Dade under a 1.5 metre sea level rise scenario, with a control panel listing impact metrics."
              width={1500}
              height={950}
              priority
              className="w-full rounded-lg border border-line/60"
            />
          </div>
          <figcaption className="mt-4 text-center text-sm text-faint">
            An actual CORA run: South Miami-Dade, Florida at 1.5 m sea level
            rise, using Copernicus 30 m elevation data.
          </figcaption>
        </figure>
      </div>
    </section>
  );
}
