import type { Metadata, Viewport } from "next";
import ServiceGraph from "./ServiceGraph";
import data from "./graph-data.json";
import type { GraphData } from "./types";

const title = "How I Serve the World — Kunal Dovedy";
const description =
  "A service graph: eight stages from what must stay true, through what gets made, to the people on the other end. Built from public sources and honest about which parts are inferred.";

export const metadata: Metadata = {
  title,
  description,
  alternates: { canonical: "/graph" },
  openGraph: {
    title,
    description,
    url: "/graph",
    images: [
      { url: "/images/hero-bg.jpg", width: 1920, height: 1174, alt: "The Turbinophone at sunset" },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: ["/images/hero-bg.jpg"],
  },
};

export const viewport: Viewport = {
  // The drawing runs edge to edge on a phone, so the page has to know about
  // the notch and the home indicator.
  viewportFit: "cover",
  themeColor: "#ffffff",
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Dataset",
  name: "Kunal Dovedy — service graph",
  description,
  url: "https://kunaldovedy.com/graph",
  creator: { "@type": "Person", name: "Kunal Dovedy", url: "https://kunaldovedy.com" },
  license: "https://kunaldovedy.com/graph",
  variableMeasured: (data as GraphData).node_types.map((t) => t.plural),
};

export default function GraphPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <ServiceGraph />
    </>
  );
}
