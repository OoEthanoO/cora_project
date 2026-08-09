import { MedalIcon } from "./icons";

const awards = [
  {
    placement: "First place",
    name: "Canadian Meteorological and Oceanographic Society Award",
    tone: "gold" as const,
  },
  {
    placement: "Silver medal",
    name: "York Region Science and Technology Fair",
    tone: "silver" as const,
  },
  {
    placement: "Silver medal",
    name: "IgniteCS Expo — Senior Division, Data Science",
    tone: "silver" as const,
  },
];

const tones = {
  gold: {
    icon: "border-gold/30 bg-gold/10 text-gold",
    placement: "text-gold",
  },
  silver: {
    icon: "border-silver/25 bg-silver/10 text-silver",
    placement: "text-silver",
  },
};

export function Awards() {
  return (
    <section id="recognition" className="border-t border-line/60 py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Recognition
          </h2>
          <p className="mt-4 text-lg text-muted text-pretty">
            CORA has been judged by scientists and engineers at three
            competitions.
          </p>
        </div>

        <ul className="mt-12 grid gap-5 sm:grid-cols-3">
          {awards.map((award) => {
            const tone = tones[award.tone];
            return (
              <li
                key={award.name}
                className="rounded-2xl border border-line bg-deep p-7 transition-colors hover:border-line/80 hover:bg-surface"
              >
                <div
                  className={`flex size-11 items-center justify-center rounded-xl border ${tone.icon}`}
                >
                  <MedalIcon className="size-5.5" />
                </div>
                <p
                  className={`mt-5 text-xs font-medium tracking-wide uppercase ${tone.placement}`}
                >
                  {award.placement}
                </p>
                <h3 className="mt-2 leading-snug font-semibold tracking-tight text-pretty">
                  {award.name}
                </h3>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
