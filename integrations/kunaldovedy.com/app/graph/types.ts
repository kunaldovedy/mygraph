export type GlyphName =
  | "core" | "diamond" | "circle" | "triangle"
  | "square" | "hexagon" | "pentagon" | "cross";

export type NodeType = {
  name: string;
  label: string;
  plural: string;
  stage: number;
  glyph: GlyphName;
  palette: string;
  question: string;
  count: number;
};

export type GraphNode = {
  id: string;
  type: string;
  label: string;
  subtitle?: string;
  summary: string;
  source: string;
  confidence: "high" | "medium" | "low";
  refs?: string[];
  props?: Record<string, string | number>;
  stage: number;
  degree: number;
  pagerank: number;
  audiences_reached: number;
  outcomes_produced: number;
};

export type GraphEdge = {
  src: string;
  dst: string;
  rel: string;
  rel_label: string;
  kind: "forward" | "return";
  weight: number;
  note?: string;
  source: string;
};

export type GraphData = {
  meta: {
    name: string;
    subject: string;
    stage_count: number;
    node_count: number;
    edge_count: number;
  };
  node_types: NodeType[];
  edge_types: { name: string; label: string; kind: string }[];
  sources: Record<string, string>;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

/** A node once the radial layout has given it a place. */
export type PlacedNode = GraphNode & { x: number; y: number; angle: number };

export type PlacedEdge = GraphEdge & {
  a: PlacedNode;
  b: PlacedNode;
  d: string;
};
