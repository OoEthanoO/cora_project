const steps = [
  {
    n: "01",
    title: "Load elevation data",
    body: "Open a local GeoTIFF, or download Copernicus 30 m elevation for any bounding box straight from OpenTopography with a free API key.",
  },
  {
    n: "02",
    title: "Set the scenario",
    body: "Pick a location and buffer, then dial in sea level rise from 0 to 2 metres — or choose a preset scenario — with an optional tidal gauge baseline.",
  },
  {
    n: "03",
    title: "Pull in what's at stake",
    body: "Fetch buildings and roads from OpenStreetMap for the area. Results are cached locally, so re-running the same coastline is fast.",
  },
  {
    n: "04",
    title: "Test an intervention",
    body: "Draw a sea wall or a wetland restoration polygon, re-run the analysis, and compare the flooded area, damage and exposure against the do-nothing case.",
  },
];

export function Workflow() {
  return (
    <section
      id="workflow"
      className="border-t border-line/60 bg-deep/50 py-20 sm:py-28"
    >
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            From raster to recommendation
          </h2>
          <p className="mt-4 text-lg text-muted text-pretty">
            Four steps, all on your own machine. No account, no cloud
            processing, no per-analysis billing.
          </p>
        </div>

        <ol className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => (
            <li key={step.n} className="relative border-t border-line pt-6">
              <span className="font-mono text-sm text-tide">{step.n}</span>
              <h3 className="mt-3 font-semibold tracking-tight">{step.title}</h3>
              <p className="mt-2.5 text-[15px] leading-relaxed text-muted text-pretty">
                {step.body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
