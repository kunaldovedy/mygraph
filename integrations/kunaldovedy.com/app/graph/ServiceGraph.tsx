"use client";

import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import GraphCanvas from "./GraphCanvas";
import NodeSheet, { Glyph } from "./NodeSheet";
import { layoutEdges, layoutNodes } from "./geometry";
import { markColour } from "./palette";
import graphData from "./graph-data.json";
import type { GraphData, GraphNode, NodeType } from "./types";

// The graph never changes once it is built, so the layout is worked out once
// when this module loads rather than on every mount. The maths is pure, so the
// server and the browser arrive at the same positions.
const data = graphData as GraphData;
const nodes = layoutNodes(data);
const edges = layoutEdges(data, nodes);
const byId = new Map(nodes.map((n) => [n.id, n]));
const typeByName = new Map(data.node_types.map((t) => [t.name, t]));
const maxRank = Math.max(...data.nodes.map((n) => n.pagerank));
const subject = byId.get(data.meta.subject);
const inferredCount = data.nodes.filter((n) => n.source === "inferred").length;

export default function ServiceGraph() {

  const [activeStage, setActiveStage] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [exploring, setExploring] = useState(false);
  const isDesktop = useMediaQuery("(min-width: 1024px)");

  const selectedNode = selected ? byId.get(selected) ?? null : null;
  const outward = useMemo(
    () => (selected ? edges.filter((e) => e.src === selected) : []),
    [selected],
  );
  const inward = useMemo(
    () => (selected ? edges.filter((e) => e.dst === selected) : []),
    [selected],
  );

  /* ------------------------------------------- the scroll drives the camera */
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  useEffect(() => {
    const sections = sectionRefs.current.filter(Boolean) as HTMLElement[];
    if (sections.length === 0) return;
    const observer = new IntersectionObserver(
      (entries) => {
        let best: IntersectionObserverEntry | null = null;
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          if (!best || entry.intersectionRatio > best.intersectionRatio) best = entry;
        }
        if (best) {
          const stage = Number((best.target as HTMLElement).dataset.stage);
          if (!Number.isNaN(stage)) setActiveStage(stage);
        }
      },
      {
        threshold: [0.1, 0.35, 0.6],
        rootMargin: isDesktop ? "-25% 0px -45% 0px" : "-56% 0px -18% 0px",
      },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [isDesktop]);

  // Pick a node from a list and the drawing follows it.
  const choose = (id: string | null) => {
    setSelected(id);
    if (id) {
      const node = byId.get(id);
      if (node) setActiveStage(node.stage);
    }
  };

  const activeType = data.node_types.find((t) => t.stage === activeStage);

  return (
    <>
      {/* ------------------------------------------------------------ hero */}
      <section className="mx-auto max-w-6xl px-6 pb-5 pt-8 sm:pb-8 sm:pt-16">
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400">
          Service graph &middot; eight stages
        </p>
        <h1 className="mt-3 font-[family-name:var(--font-poppins)] text-4xl font-bold leading-[1.05] tracking-tight text-dark sm:text-6xl">
          How I serve
          <br />
          the world
        </h1>
        <p className="mt-5 max-w-xl text-[17px] leading-relaxed text-gray-600 sm:text-lg">
          A jet engine compressor rings like a tuning fork when you drop a ball bearing into it. A
          practice works the same way. Something goes in at the centre and the sound comes out at
          the edge.
        </p>
      </section>

      {/* -------------------------------------------- the instrument + stages */}
      <div className="mx-auto max-w-6xl px-6 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,27rem)] lg:gap-12">
        {/* sticky drawing */}
        <div className="sticky top-14 z-20 -mx-6 bg-white/95 px-6 pb-3 pt-3 backdrop-blur lg:top-20 lg:mx-0 lg:flex lg:h-[calc(100vh-7rem)] lg:flex-col lg:gap-4 lg:self-start lg:px-0 lg:pb-0">
          {/* content slides under the drawing, so it fades rather than cuts */}
          <div className="pointer-events-none absolute inset-x-0 top-full h-7 bg-gradient-to-b from-white to-transparent lg:hidden" />
          <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white lg:min-h-0 lg:flex-1">
            <GraphCanvas
              nodes={nodes}
              edges={edges}
              nodeTypes={data.node_types}
              maxRank={maxRank}
              activeStage={activeStage}
              selectedId={selected}
              onSelect={choose}
              className="h-[min(92vw,44vh)] w-full lg:h-full"
            />

            {/* what ring am I looking at */}
            <div className="pointer-events-none absolute inset-x-0 top-0 flex items-center gap-2 p-3">
              <span className="rounded-full bg-dark/90 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
                Stage {activeStage}
              </span>
              <span className="flex items-center gap-1.5 rounded-full bg-white/90 px-2.5 py-1 text-[11px] font-semibold text-dark shadow-sm">
                <Glyph type={activeType} size={11} />
                {activeType?.plural}
              </span>
            </div>

            <button
              type="button"
              onClick={() => setExploring(true)}
              className="absolute bottom-3 right-3 flex min-h-[40px] items-center gap-1.5 rounded-full border border-gray-200 bg-white/95 px-3.5 text-xs font-semibold text-dark shadow-sm backdrop-blur active:scale-95"
            >
              <ExpandIcon />
              Explore
            </button>

            {/* travel indicator */}
            <div className="absolute inset-x-0 bottom-0 h-1 bg-gray-100">
              <div
                className="h-full bg-coral transition-[width] duration-500 ease-out"
                style={{ width: `${((activeStage + 1) / data.meta.stage_count) * 100}%` }}
              />
            </div>
          </div>

          {/* On a wide screen the detail sits under the drawing, in the space
              the drawing does not need, rather than over the list. */}
          {isDesktop && selectedNode && (
            <div className="hidden min-h-0 shrink-0 lg:block lg:max-h-[46%]">
              <NodeSheet
                node={selectedNode}
                type={typeByName.get(selectedNode.type)}
                typeByName={typeByName}
                outward={outward}
                inward={inward}
                sources={data.sources}
                onSelect={choose}
                onClose={() => setSelected(null)}
                variant="card"
              />
            </div>
          )}
        </div>

        {/* the stages, scrolling beneath */}
        <div className="pb-8 pt-5 lg:pt-0">
          <p className="text-[15px] leading-relaxed text-gray-500">
            Scroll to travel outward, ring by ring. Tap anything to see where it came from.
          </p>
          {data.node_types.map((type, index) => (
            <section
              key={type.name}
              data-stage={type.stage}
              ref={(el) => {
                sectionRefs.current[index] = el;
              }}
              className="min-h-[58vh] scroll-mt-28 py-8 lg:min-h-[70vh]"
            >
              <div className="flex items-baseline gap-3">
                <span className="font-[family-name:var(--font-poppins)] text-sm font-bold tabular-nums text-gray-300">
                  {String(type.stage).padStart(2, "0")}
                </span>
                <h2 className="flex items-center gap-2 font-[family-name:var(--font-poppins)] text-2xl font-bold tracking-tight text-dark">
                  <Glyph type={type} size={15} />
                  {type.plural}
                </h2>
              </div>
              <p className="mt-2 text-[17px] italic leading-relaxed text-gray-500">
                {type.question}
              </p>
              <p className="mt-4 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
                {type.count} in the graph
              </p>
              <ul className="mt-3 space-y-2">
                {data.nodes
                  .filter((n) => n.type === type.name)
                  .map((node) => (
                    <li key={node.id}>
                      <NodeRow
                        node={node}
                        type={type}
                        active={node.id === selected}
                        onSelect={choose}
                      />
                    </li>
                  ))}
              </ul>
              {type.stage === 7 && <LoopNote />}
            </section>
          ))}
        </div>
      </div>

      {/* ----------------------------------------------------------- index */}
      <Index data={data} typeByName={typeByName} onSelect={choose} />

      {/* ----------------------------------------------- the figures, in full */}
      <section className="mx-auto max-w-6xl px-6">
        <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl bg-gray-200 sm:grid-cols-4">
          <Figure label="Nodes" value={data.meta.node_count} />
          <Figure label="Connections" value={data.meta.edge_count} />
          <Figure label="Audiences served" value={subject?.audiences_reached ?? 0} />
          <Figure label="Still to confirm" value={inferredCount} />
        </dl>
      </section>

      {/* --------------------------------------------------- detail surface */}
      {!isDesktop && (
        <NodeSheet
          node={selectedNode}
          type={selectedNode ? typeByName.get(selectedNode.type) : undefined}
          typeByName={typeByName}
          outward={outward}
          inward={inward}
          sources={data.sources}
          onSelect={choose}
          onClose={() => setSelected(null)}
          variant="sheet"
        />
      )}

      {/* ------------------------------------------------- full-screen explore */}
      {exploring && (
        <div className="fixed inset-0 z-[60] flex flex-col bg-white">
          <div
            className="flex items-center justify-between border-b border-gray-100 px-4 py-3"
            style={{ paddingTop: "calc(0.75rem + env(safe-area-inset-top, 0px))" }}
          >
            <div>
              <p className="font-[family-name:var(--font-poppins)] text-base font-bold text-dark">
                The whole machine
              </p>
              <p className="text-xs text-gray-500">Pinch to zoom, drag to move, tap to open</p>
            </div>
            <button
              type="button"
              onClick={() => setExploring(false)}
              className="min-h-[44px] rounded-full bg-dark px-4 text-sm font-semibold text-white active:scale-95"
            >
              Done
            </button>
          </div>
          {/* With the sheet open the drawing gives up the lower half of the
              screen, so the selection never hides behind it. */}
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            nodeTypes={data.node_types}
            maxRank={maxRank}
            activeStage={activeStage}
            selectedId={selected}
            onSelect={choose}
            interactive
            className={selectedNode ? "h-[46vh] shrink-0" : "min-h-0 flex-1"}
          />
          {selectedNode && !isDesktop && (
            <NodeSheet
              node={selectedNode}
              type={typeByName.get(selectedNode.type)}
              typeByName={typeByName}
              outward={outward}
              inward={inward}
              sources={data.sources}
              onSelect={choose}
              onClose={() => setSelected(null)}
              variant="sheet"
            />
          )}
        </div>
      )}
    </>
  );
}

/* ------------------------------------------------------------------ pieces */

function NodeRow({
  node,
  type,
  active,
  onSelect,
}: {
  node: GraphNode;
  type: NodeType;
  active: boolean;
  onSelect: (id: string) => void;
}) {
  const unsure = node.source === "inferred" || node.confidence === "low";
  return (
    <button
      type="button"
      onClick={() => onSelect(node.id)}
      aria-pressed={active}
      className={`flex min-h-[56px] w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition active:scale-[0.99] ${
        active
          ? "border-coral bg-coral/5"
          : "border-gray-200 bg-white hover:border-gray-300"
      }`}
    >
      <span
        className="h-9 w-1 shrink-0 rounded-full"
        style={{ background: markColour(type.palette), opacity: unsure ? 0.4 : 1 }}
      />
      <span className="min-w-0 flex-1">
        <span className="block text-[15px] font-semibold leading-snug text-dark">{node.label}</span>
        {node.subtitle && (
          <span className="mt-0.5 block text-[13px] leading-snug text-gray-500">
            {node.subtitle}
          </span>
        )}
      </span>
      {unsure && (
        <span className="shrink-0 rounded-full border border-dashed border-amber-400 px-2 py-0.5 text-[10px] font-medium text-amber-700">
          to confirm
        </span>
      )}
    </button>
  );
}

function LoopNote() {
  return (
    <div className="mt-8 rounded-2xl border border-dashed border-gray-300 bg-light p-5">
      <h3 className="font-[family-name:var(--font-poppins)] text-base font-bold text-dark">
        And then it comes back
      </h3>
      <p className="mt-2 text-[15px] leading-relaxed text-gray-600">
        Outcomes point back at the values that started them, and the people served hand something
        back to the practice. Those are the dashed lines bowing through the middle of the drawing.
        Without them this is a pipeline. With them it is a practice.
      </p>
    </div>
  );
}

function Index({
  data,
  typeByName,
  onSelect,
}: {
  data: GraphData;
  typeByName: Map<string, NodeType>;
  onSelect: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const needle = query.trim().toLowerCase();
  const rows = data.nodes.filter(
    (n) =>
      !needle ||
      `${n.label} ${n.subtitle ?? ""} ${n.summary} ${n.id}`.toLowerCase().includes(needle),
  );

  return (
    <section className="mx-auto max-w-6xl px-6 py-16">
      <h2 className="font-[family-name:var(--font-poppins)] text-2xl font-bold tracking-tight text-dark">
        Every node, as text
      </h2>
      <p className="mt-2 max-w-2xl text-[15px] leading-relaxed text-gray-600">
        The same graph without the picture, for anyone the drawing does not serve.
        <strong className="font-semibold text-dark"> To confirm</strong> marks what was read between
        the lines of the public record rather than sourced.
      </p>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search the graph"
        aria-label="Search the graph"
        className="mt-5 min-h-[48px] w-full rounded-xl border border-gray-200 px-4 text-[16px] text-dark outline-none transition placeholder:text-gray-400 focus:border-coral sm:max-w-sm"
      />

      <ul className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {rows.map((node) => {
          const type = typeByName.get(node.type);
          return (
            <li key={node.id}>
              <button
                type="button"
                onClick={() => {
                  onSelect(node.id);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                className="flex min-h-[56px] w-full items-start gap-3 rounded-xl border border-gray-200 px-4 py-3 text-left transition hover:border-gray-300 active:scale-[0.99]"
              >
                <span className="pt-1">
                  <Glyph type={type} size={12} />
                </span>
                <span className="min-w-0">
                  <span className="block text-[10px] uppercase tracking-wider text-gray-400">
                    {type?.label} &middot; {node.audiences_reached} audiences
                  </span>
                  <span className="block text-[15px] font-medium leading-snug text-dark">
                    {node.label}
                  </span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
      {rows.length === 0 && (
        <p className="mt-6 text-gray-500">Nothing matches &ldquo;{query}&rdquo;.</p>
      )}
    </section>
  );
}

function Figure({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white px-4 py-4">
      <dt className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">{label}</dt>
      <dd className="mt-0.5 font-[family-name:var(--font-poppins)] text-2xl font-bold tabular-nums text-dark">
        {value}
      </dd>
    </div>
  );
}

function ExpandIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M6 1.5H1.5V6M10 14.5H14.5V10M14.5 6V1.5H10M1.5 10v4.5H6"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function useMediaQuery(query: string): boolean {
  // Subscribing rather than writing state inside an effect keeps the first
  // client render in step with the server's, which assumes a phone.
  return useSyncExternalStore(
    (notify) => {
      const list = window.matchMedia(query);
      list.addEventListener("change", notify);
      return () => list.removeEventListener("change", notify);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}
