import {
  BuildingIcon,
  GaugeIcon,
  PeopleIcon,
  ReportIcon,
  WallIcon,
  WavesIcon,
} from "./icons";

const features = [
  {
    icon: WavesIcon,
    title: "Connected flood modelling",
    body: "Goes beyond a naive bathtub fill: only water with an actual path from the sea counts as flooded, so inland depressions aren't wrongly drowned.",
  },
  {
    icon: GaugeIcon,
    title: "Real tidal baselines",
    body: "Pulls mean sea level from the nearest NOAA tidal gauge instead of assuming zero elevation, anchoring each scenario to locally measured water levels.",
  },
  {
    icon: PeopleIcon,
    title: "Population exposure",
    body: "Overlays WorldPop demographic rasters to estimate how many people sit inside the flood extent, as a count and as a share of the study area.",
  },
  {
    icon: BuildingIcon,
    title: "Infrastructure impact",
    body: "Pulls buildings and roads from OpenStreetMap, flags critical sites like hospitals, schools and fire stations, and reports what each scenario takes out.",
  },
  {
    icon: WallIcon,
    title: "Adaptation strategies",
    body: "Draw a sea wall at a chosen height, or sketch a wetland restoration area with an evidence-based reduction factor, then re-run to see what it buys you.",
  },
  {
    icon: ReportIcon,
    title: "Publication-ready reports",
    body: "Export a PDF with parameters, methodology, impact and economic damage tables, and a high-resolution inundation map — ready to hand to a planning board.",
  },
];

export function Features() {
  return (
    <section id="features" className="border-t border-line/60 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Everything you need to make the case
          </h2>
          <p className="mt-4 text-lg text-muted text-pretty">
            CORA turns raw elevation rasters into the numbers a coastal
            adaptation argument actually rests on.
          </p>
        </div>

        <ul className="mt-14 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, body }) => (
            <li key={title} className="group bg-deep p-7 transition-colors hover:bg-surface">
              <div className="flex size-11 items-center justify-center rounded-xl border border-tide/25 bg-tide/10 text-tide-bright transition-colors group-hover:border-tide/50">
                <Icon className="size-5.5" />
              </div>
              <h3 className="mt-5 font-semibold tracking-tight">{title}</h3>
              <p className="mt-2.5 text-[15px] leading-relaxed text-muted text-pretty">
                {body}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
