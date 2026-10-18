/**
 * The drawing is a compressor face: eight concentric stages, read outward.
 *
 * Nothing in this file touches the DOM, so the same maths runs on the server
 * for the first paint and in the browser for the camera.
 */

import type { GlyphName, GraphData, GraphNode, PlacedEdge, PlacedNode } from "./types";

/** The square the drawing lives in. */
export const BOX = 1360;
export const CENTRE = BOX / 2;

/** Ring radius per stage. Stage 0 is the centre. */
export const RADII = [0, 92, 152, 206, 256, 302, 348, 392];

export function ringRadius(stage: number): number {
  return RADII[Math.min(stage, RADII.length - 1)];
}

/* ------------------------------------------------------------------ glyphs */
/* Shape carries identity as well as colour, so the diagram still reads for
   anyone who cannot separate two hues, and at a glance on a small screen. */

function polygon(sides: number, r: number, offset: number): string {
  let d = "";
  for (let i = 0; i < sides; i++) {
    const a = offset + (i * 2 * Math.PI) / sides;
    d += (i ? "L" : "M") + (Math.cos(a) * r).toFixed(2) + " " + (Math.sin(a) * r).toFixed(2);
  }
  return d + "Z";
}

export function glyphPath(glyph: GlyphName, r: number): string | null {
  switch (glyph) {
    case "diamond":
      return polygon(4, r * 1.24, -Math.PI / 2);
    case "triangle":
      return polygon(3, r * 1.34, -Math.PI / 2);
    case "square":
      return polygon(4, r * 1.18, -Math.PI / 4);
    case "pentagon":
      return polygon(5, r * 1.2, -Math.PI / 2);
    case "hexagon":
      return polygon(6, r * 1.14, 0);
    case "cross": {
      const a = r * 0.42;
      const b = r * 1.3;
      return `M${-a} ${-b}H${a}V${-a}H${b}V${a}H${a}V${b}H${-a}V${a}H${-b}V${-a}H${-a}Z`;
    }
    default:
      return null; // circle and core are drawn as circles
  }
}

/* ------------------------------------------------------------------ layout */

function meanAngle(angles: number[]): number {
  let sx = 0;
  let sy = 0;
  for (const a of angles) {
    sx += Math.cos(a);
    sy += Math.sin(a);
  }
  return Math.atan2(sy, sx);
}

/**
 * Place every node on its ring.
 *
 * Within a ring, nodes are ordered by the mean angle of the neighbours they
 * already have on the inside. Related things end up next to each other and the
 * lines cross less than they otherwise would.
 */
export function layoutNodes(data: GraphData): PlacedNode[] {
  const placed: PlacedNode[] = data.nodes.map((n) => ({ ...n, x: CENTRE, y: CENTRE, angle: 0 }));
  const byId = new Map(placed.map((n) => [n.id, n]));
  const stages: PlacedNode[][] = [];
  for (const node of placed) {
    (stages[node.stage] ||= []).push(node);
  }

  stages.forEach((group, stage) => {
    if (stage === 0) {
      for (const n of group) {
        n.x = CENTRE;
        n.y = CENTRE;
      }
      return;
    }
    if (stage > 1) {
      const order = new Map<string, number>();
      for (const n of group) {
        const inner = data.edges
          .filter((e) => e.dst === n.id)
          .map((e) => byId.get(e.src))
          .filter((s): s is PlacedNode => Boolean(s) && s!.stage < n.stage)
          .map((s) => s.angle);
        order.set(n.id, inner.length ? meanAngle(inner) : Math.PI);
      }
      group.sort((a, b) => (order.get(a.id)! - order.get(b.id)!) || a.label.localeCompare(b.label));
    }
    const r = ringRadius(stage);
    const step = (2 * Math.PI) / group.length;
    group.forEach((n, i) => {
      // Nothing sits at twelve o'clock: that is where the ring name goes.
      n.angle = -Math.PI / 2 + step * 0.42 + i * step + (stage % 2 ? step / 2 : 0);
      n.x = CENTRE + Math.cos(n.angle) * r;
      n.y = CENTRE + Math.sin(n.angle) * r;
    });
  });

  return placed;
}

export function layoutEdges(data: GraphData, nodes: PlacedNode[]): PlacedEdge[] {
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const out: PlacedEdge[] = [];
  for (const edge of data.edges) {
    const a = byId.get(edge.src);
    const b = byId.get(edge.dst);
    if (!a || !b) continue;
    out.push({ ...edge, a, b, d: edgePath(a, b, edge.kind) });
  }
  return out;
}

export function edgePath(a: PlacedNode, b: PlacedNode, kind: "forward" | "return"): string {
  if (kind === "return") {
    // Feedback bows toward the middle. That is the loop, drawn.
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const cx = mx + (CENTRE - mx) * 0.72;
    const cy = my + (CENTRE - my) * 0.72;
    return `M${a.x.toFixed(1)} ${a.y.toFixed(1)}Q${cx.toFixed(1)} ${cy.toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
  }
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  const cx = mx - dy * 0.11;
  const cy = my + dx * 0.11;
  return `M${a.x.toFixed(1)} ${a.y.toFixed(1)}Q${cx.toFixed(1)} ${cy.toFixed(1)} ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
}

/** Node size, with a floor so every target stays tappable. */
export function nodeRadius(node: GraphNode, maxRank: number): number {
  if (node.type === "person") return 19;
  const scale = maxRank ? node.pagerank / maxRank : 0;
  return 6 + Math.sqrt(scale) * 9.5;
}

/* ------------------------------------------------------------------ camera */

/**
 * How far to zoom so a given ring fills the frame, leaving room for the
 * labels that radiate off it.
 */
export function scaleForStage(stage: number): number {
  // Stage 0 is the opening frame: the whole machine at once, before the
  // reader starts travelling outward through it.
  if (stage === 0) return 0.95;
  const r = ringRadius(stage);
  const framed = r + 250;
  return Math.min(2.4, Math.max(0.92, CENTRE / framed));
}

/** Zoom always happens about the centre of the drawing. */
export function cameraTransform(k: number, panX = 0, panY = 0): string {
  const offset = CENTRE * (1 - k);
  return `translate(${(offset + panX).toFixed(2)}px, ${(offset + panY).toFixed(2)}px) scale(${k.toFixed(4)})`;
}

/** Build an adjacency map once, for neighbour lookups. */
export function adjacency(data: GraphData): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>();
  for (const node of data.nodes) map.set(node.id, new Set());
  for (const edge of data.edges) {
    map.get(edge.src)?.add(edge.dst);
    map.get(edge.dst)?.add(edge.src);
  }
  return map;
}
