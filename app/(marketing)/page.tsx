import LenisProvider from "@/components/LenisProvider";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Scrolly from "@/components/Scrolly";
import Bento from "@/components/Bento";
import Languages from "@/components/Languages";
import CtaStats from "@/components/CtaStats";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <LenisProvider>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <Scrolly />
        <Bento />
        <Languages />
        <CtaStats />
      </main>
      <Footer />
    </LenisProvider>
  );
}
