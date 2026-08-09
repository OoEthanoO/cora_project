import Image from "next/image";
import { release, repoUrl } from "@/lib/release";

const sources = [
  { label: "Copernicus DEM via OpenTopography", href: "https://opentopography.org" },
  { label: "OpenStreetMap", href: "https://www.openstreetmap.org" },
  { label: "NOAA Tides & Currents", href: "https://tidesandcurrents.noaa.gov" },
  { label: "WorldPop", href: "https://www.worldpop.org" },
];

export function Footer() {
  return (
    <footer className="mt-auto border-t border-line/60 py-14">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col gap-10 sm:flex-row sm:justify-between">
          <div className="max-w-sm">
            <div className="flex items-center gap-2.5">
              <Image
                src="/img/cora-icon.png"
                alt=""
                width={28}
                height={28}
                className="rounded-lg"
              />
              <span className="font-semibold tracking-tight">CORA</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-faint text-pretty">
              Coastal Risk Analyzer — an open source tool for modelling sea
              level rise, flood exposure and coastal adaptation.
            </p>
          </div>

          <div className="flex gap-14">
            <div>
              <h3 className="text-xs font-medium tracking-wide text-muted uppercase">
                Project
              </h3>
              <ul className="mt-4 space-y-2.5 text-sm">
                <li>
                  <a href={repoUrl} className="text-faint transition-colors hover:text-ink">
                    Source code
                  </a>
                </li>
                <li>
                  <a
                    href={`${repoUrl}/issues`}
                    className="text-faint transition-colors hover:text-ink"
                  >
                    Report an issue
                  </a>
                </li>
                <li>
                  <a href="#download" className="text-faint transition-colors hover:text-ink">
                    Download v{release.version}
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xs font-medium tracking-wide text-muted uppercase">
                Data sources
              </h3>
              <ul className="mt-4 space-y-2.5 text-sm">
                {sources.map((source) => (
                  <li key={source.href}>
                    <a
                      href={source.href}
                      className="text-faint transition-colors hover:text-ink"
                    >
                      {source.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-12 border-t border-line pt-6 text-xs text-faint">
          <p className="text-pretty">
            CORA produces screening-level estimates from public elevation and
            demographic data. It is not a substitute for a site-specific
            engineering or hydrodynamic study.
          </p>
        </div>
      </div>
    </footer>
  );
}
