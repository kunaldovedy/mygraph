/**
 * Colour.
 *
 * Coral is the site's accent and stays the accent here: it marks what is
 * interactive and what is selected, and it is never a node's identity.
 *
 * Node identity uses a categorical set whose adjacent pairs clear a
 * colour-vision-deficiency separation of Delta E >= 8 (OKLab x100). A network
 * diagram is an all-pairs case, and no eight-hue set clears the all-pairs
 * floor, so colour never carries identity alone: every kind also has its own
 * glyph, the legend is always on screen, and the index at the foot of the page
 * carries the same data as text.
 */

export const BRAND = {
  coral: "#ff6b7e",
  coralInk: "#e13d56", // coral stepped down for text and thin marks on white
  teal: "#37c9df",
  dark: "#1a1a2e",
  ink: "#333333",
  muted: "#6b7280",
  faint: "#9ca3af",
  rule: "#e5e7eb",
  wash: "#f8f9fa",
} as const;

/** Slot name (from the ontology) to mark colour. */
export const MARK: Record<string, string> = {
  ink: BRAND.dark,
  violet: "#4a3aa7",
  blue: "#2a78d6",
  green: "#008300",
  orange: "#eb6834",
  magenta: "#d2498a",
  aqua: "#1baf7a",
  yellow: "#c57f00",
};

export function markColour(paletteSlot: string): string {
  return MARK[paletteSlot] ?? BRAND.dark;
}

/** A pale wash of the mark colour, for chips and section headers. */
export function markWash(paletteSlot: string): string {
  return `color-mix(in srgb, ${markColour(paletteSlot)} 12%, white)`;
}
