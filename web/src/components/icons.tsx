type IconProps = { className?: string };

const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  viewBox: "0 0 24 24",
  "aria-hidden": true,
};

export function AppleIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className={className}>
      <path d="M16.36 12.66c.02-2.28 1.86-3.38 1.94-3.43-1.06-1.55-2.7-1.76-3.29-1.79-1.4-.14-2.73.82-3.44.82-.71 0-1.8-.8-2.96-.78-1.52.02-2.93.88-3.71 2.24-1.58 2.74-.4 6.8 1.14 9.02.75 1.09 1.65 2.31 2.82 2.27 1.13-.05 1.56-.73 2.93-.73s1.75.73 2.95.71c1.22-.02 1.99-1.11 2.74-2.2.86-1.26 1.22-2.48 1.24-2.55-.03-.01-2.38-.91-2.36-3.58ZM14.1 5.98c.62-.76 1.04-1.8.93-2.85-.9.04-1.99.6-2.63 1.35-.57.67-1.08 1.74-.94 2.76 1 .08 2.02-.51 2.64-1.26Z" />
    </svg>
  );
}

export function ArrowIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function WavesIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M2 6c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2M2 12c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2M2 18c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2" />
    </svg>
  );
}

export function PeopleIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M16 20v-1.5a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4V20M9 10.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM22 20v-1.5a4 4 0 0 0-3-3.87M16 3.63a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

export function GaugeIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M12 14.5 16 9M3.5 19a9 9 0 1 1 17 0" />
      <circle cx="12" cy="14.5" r="1.6" />
    </svg>
  );
}

export function WallIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M3 21V8l9-5 9 5v13M3 12h18M3 16.5h18M8.5 8v13M15.5 8v13" />
    </svg>
  );
}

export function BuildingIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M15 21V11h4a2 2 0 0 1 2 2v8M9 7h2M9 11h2M9 15h2" />
    </svg>
  );
}

export function ReportIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z" />
      <path d="M14 3v5h5M9 13h6M9 17h4" />
    </svg>
  );
}

export function MedalIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="M8.5 3H5l3.5 6M15.5 3H19l-3.5 6" />
      <circle cx="12" cy="15" r="6" />
      <path d="m12 12.2 1 2.05 2.25.33-1.62 1.58.38 2.24L12 17.34l-2.01 1.06.38-2.24-1.62-1.58 2.25-.33L12 12.2Z" />
    </svg>
  );
}

export function CheckIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <path d="m5 12.5 4.5 4.5L19 7" />
    </svg>
  );
}

export function LockIcon({ className }: IconProps) {
  return (
    <svg {...base} className={className}>
      <rect x="4" y="10.5" width="16" height="10.5" rx="2" />
      <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
    </svg>
  );
}
