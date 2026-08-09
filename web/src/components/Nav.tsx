import Image from "next/image";
import { repoUrl } from "@/lib/release";

const links = [
  { href: "#recognition", label: "Recognition" },
  { href: "#features", label: "Features" },
  { href: "#workflow", label: "How it works" },
  { href: "#download", label: "Download" },
];

export function Nav() {
  return (
    <header className="sticky top-0 z-50 border-b border-line/70 bg-abyss/80 backdrop-blur-md">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <a href="#top" className="flex items-center gap-2.5">
          <Image
            src="/img/cora-icon.png"
            alt=""
            width={32}
            height={32}
            className="rounded-lg"
          />
          <span className="text-[15px] font-semibold tracking-tight">CORA</span>
        </a>

        <div className="flex items-center gap-1 sm:gap-2">
          <ul className="hidden items-center gap-1 sm:flex">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="rounded-md px-3 py-2 text-sm text-muted transition-colors hover:text-ink"
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
          <a
            href={repoUrl}
            className="rounded-md px-3 py-2 text-sm text-muted transition-colors hover:text-ink"
          >
            GitHub
          </a>
          <a
            href="#download"
            className="ml-1 rounded-lg bg-tide px-3.5 py-2 text-sm font-medium text-abyss transition-colors hover:bg-tide-bright"
          >
            Download
          </a>
        </div>
      </nav>
    </header>
  );
}
