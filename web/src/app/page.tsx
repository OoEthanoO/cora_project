import { Awards } from "@/components/Awards";
import { CaseStudy } from "@/components/CaseStudy";
import { Download } from "@/components/Download";
import { Features } from "@/components/Features";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { Nav } from "@/components/Nav";
import { Workflow } from "@/components/Workflow";

export default function Page() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <CaseStudy />
        <Awards />
        <Features />
        <Workflow />
        <Download />
      </main>
      <Footer />
    </>
  );
}
