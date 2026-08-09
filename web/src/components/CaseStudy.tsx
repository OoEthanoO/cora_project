const stats = [
  { value: "1.5 m", label: "Sea level rise modelled" },
  { value: "1,853", label: "People inside the flood extent" },
  { value: "1.1%", label: "Of the study area's population" },
  { value: "30 m", label: "Copernicus elevation resolution" },
];

export function CaseStudy() {
  return (
    <section className="border-t border-line/60 bg-deep/50 py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col gap-10 lg:flex-row lg:items-center lg:gap-16">
          <div className="lg:w-2/5">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl text-balance">
              A worked example, in about a minute
            </h2>
            <p className="mt-4 text-muted text-pretty">
              The run shown above covers a 0.2° box over South Miami-Dade,
              Florida. CORA resolved the connected flood extent, then overlaid
              WorldPop data to count who lives inside it — the same numbers that
              go straight into the exported PDF report.
            </p>
          </div>

          <dl className="grid flex-1 grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="flex flex-col-reverse bg-abyss px-5 py-7 text-center"
              >
                <dt className="mt-2 text-xs leading-snug text-faint text-pretty">
                  {stat.label}
                </dt>
                <dd className="text-2xl font-semibold tracking-tight text-tide-bright sm:text-3xl">
                  {stat.value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
