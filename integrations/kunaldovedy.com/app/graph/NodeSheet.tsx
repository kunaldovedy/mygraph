"use client";

import { useCallback, useRef, useState } from "react";
import { glyphPath } from "./geometry";
import { BRAND, markColour } from "./palette";
import type { GraphData, GraphNode, NodeType, PlacedEdge } from "./types";

const PEEK = 148; // how much of the sheet stays on screen at rest, in pixels

type Props = {
  node: GraphNode | null;
  type: NodeType | undefined;
  typeByName: Map<string, NodeType>;
  outward: PlacedEdge[];
  inward: PlacedEdge[];
  sources: GraphData["sources"];
  onSelect: (id: string | null) => void;
  onClose: () => void;
  /** "sheet" drags up from the bottom on a phone; "card" sits in the layout. */
  variant: "sheet" | "card";
};

export default function NodeSheet({
  node,
  type,
  typeByName,
  outward,
  inward,
  sources,
  onSelect,
  onClose,
  variant,
}: Props) {
  const sheetRef = useRef<HTMLDivElement>(null);
  // null means the sheet is at its resting half-open position, which CSS
  // handles. A drag converts it to a pixel offset from fully open.
  const [offset, setOffset] = useState<number | null>(null);
  const [dragging, setDragging] = useState(false);
  const drag = useRef<{ y: number; start: number; time: number } | null>(null);

  const snapPoints = useCallback(() => {
    const height = sheetRef.current?.offsetHeight ?? 520;
    return { full: 0, half: Math.round(height * 0.46), peek: Math.max(0, height - PEEK), height };
  }, []);

  const onPointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (variant !== "sheet") return;
    const start = offset ?? snapPoints().half;
    drag.current = { y: event.clientY, start, time: performance.now() };
    setDragging(true);
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drag.current) return;
    const next = drag.current.start + (event.clientY - drag.current.y);
    setOffset(Math.max(-20, next));
  };

  const onPointerUp = (event: React.PointerEvent<HTMLDivElement>) => {
    if (!drag.current) return;
    const { full, half, peek, height } = snapPoints();
    const current = offset ?? half;
    const travelled = event.clientY - drag.current.y;
    const elapsed = Math.max(1, performance.now() - drag.current.time);
    const velocity = travelled / elapsed; // pixels per millisecond, down is positive

    let target: number;
    if (velocity > 0.7) {
      target = current > half ? height : peek; // a fast flick down
    } else if (velocity < -0.7) {
      target = current > half ? half : full; // a fast flick up
    } else {
      target = [full, half, peek, height].reduce((best, point) =>
        Math.abs(point - current) < Math.abs(best - current) ? point : best,
      );
    }
    drag.current = null;
    setDragging(false);
    if (target >= height - 8) {
      setOffset(height);
      window.setTimeout(onClose, 180);
    } else {
      setOffset(target);
    }
  };

  if (!node) return null;

  const body = (
    <NodeBody
      node={node}
      typeByName={typeByName}
      outward={outward}
      inward={inward}
      sources={sources}
      onSelect={onSelect}
    />
  );

  if (variant === "card") {
    return (
      <div className="flex h-full flex-col rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="flex shrink-0 items-start justify-between gap-3 border-b border-gray-100 p-5">
          <Heading node={node} type={type} />
          <button
            type="button"
            onClick={onClose}
            className="-m-1 shrink-0 rounded-full p-2 text-gray-400 transition hover:bg-gray-50 hover:text-coral"
            aria-label="Close"
          >
            <CloseIcon />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto p-5">{body}</div>
      </div>
    );
  }

  return (
    <div
      ref={sheetRef}
      className="fixed inset-x-0 bottom-0 z-50 flex h-[86dvh] flex-col rounded-t-3xl border-t border-gray-200 bg-white shadow-[0_-8px_40px_rgba(26,26,46,0.18)] lg:hidden"
      style={{
        transform: offset === null ? "translateY(46%)" : `translateY(${offset}px)`,
        transition: dragging ? "none" : "transform 320ms cubic-bezier(0.22, 1, 0.36, 1)",
      }}
      role="dialog"
      aria-label={`${node.label} details`}
    >
      {/* The grab area. Everything here is pointer-driven, so the page
          underneath never scrolls by accident while the sheet is moving. */}
      <div
        className="shrink-0 cursor-grab touch-none px-5 pb-3 pt-3 active:cursor-grabbing"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        <div className="mx-auto mb-3 h-1.5 w-11 rounded-full bg-gray-300" />
        <div className="flex items-start justify-between gap-3">
          <Heading node={node} type={type} />
          <button
            type="button"
            onClick={onClose}
            className="-m-1 shrink-0 rounded-full p-2 text-gray-400 active:bg-gray-100"
            aria-label="Close"
          >
            <CloseIcon />
          </button>
        </div>
      </div>
      <div
        className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 pt-1"
        style={{ paddingBottom: "calc(2rem + env(safe-area-inset-bottom, 0px))" }}
      >
        {body}
      </div>
    </div>
  );
}

function Heading({ node, type }: { node: GraphNode; type: NodeType | undefined }) {
  return (
    <div className="min-w-0">
      <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
        <Glyph type={type} size={13} />
        <span className="truncate">
          {type?.label ?? node.type} &middot; stage {node.stage}
        </span>
      </div>
      <h2 className="mt-1 font-[family-name:var(--font-poppins)] text-xl font-bold leading-tight text-dark">
        {node.label}
      </h2>
      {node.subtitle && <p className="mt-0.5 text-sm italic text-gray-500">{node.subtitle}</p>}
    </div>
  );
}

function NodeBody({
  node,
  typeByName,
  outward,
  inward,
  sources,
  onSelect,
}: Omit<Props, "onClose" | "variant" | "type"> & { node: GraphNode }) {
  const unsure = node.source === "inferred" || node.confidence === "low";
  return (
    <div className="space-y-5">
      <p className="text-[15px] leading-relaxed text-gray-700">{node.summary}</p>

      <div className="flex flex-wrap gap-2">
        <span
          title={sources[node.source]}
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            unsure
              ? "border border-dashed border-amber-400 text-amber-700"
              : "bg-gray-100 text-gray-600"
          }`}
        >
          {node.source.replace("-", " ")}
        </span>
        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
          {node.confidence} confidence
        </span>
      </div>

      <dl className="grid grid-cols-3 gap-2 text-center">
        <Figure label="Audiences" value={node.audiences_reached} />
        <Figure label="Outcomes" value={node.outcomes_produced} />
        <Figure label="Links" value={Math.round(node.degree * 10) / 10} />
      </dl>

      {node.props && Object.keys(node.props).length > 0 && (
        <dl className="space-y-1.5 rounded-xl bg-light p-4 text-sm">
          {Object.entries(node.props).map(([key, value]) => (
            <div key={key} className="flex gap-3">
              <dt className="shrink-0 text-xs uppercase tracking-wide text-gray-400">
                {key.replace(/_/g, " ")}
              </dt>
              <dd className="text-gray-700">{String(value)}</dd>
            </div>
          ))}
        </dl>
      )}

      <Connections
        title="Outward"
        edges={outward}
        side="dst"
        typeByName={typeByName}
        onSelect={onSelect}
      />
      <Connections
        title="Inward"
        edges={inward}
        side="src"
        typeByName={typeByName}
        onSelect={onSelect}
      />

      {node.refs && node.refs.length > 0 && (
        <div>
          <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
            Sources
          </h3>
          <ul className="space-y-1">
            {node.refs.map((ref) => (
              <li key={ref}>
                <a
                  href={ref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="break-all text-sm text-coral underline underline-offset-2"
                >
                  {ref.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "")}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Connections({
  title,
  edges,
  side,
  typeByName,
  onSelect,
}: {
  title: string;
  edges: PlacedEdge[];
  side: "src" | "dst";
  typeByName: Map<string, NodeType>;
  onSelect: (id: string | null) => void;
}) {
  if (edges.length === 0) return null;
  return (
    <div>
      <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-gray-400">
        {title} &middot; {edges.length}
      </h3>
      <ul className="-mx-2 divide-y divide-gray-100">
        {[...edges]
          .sort((a, b) => b.weight - a.weight)
          .map((edge) => {
            const other = side === "dst" ? edge.b : edge.a;
            return (
              <li key={`${edge.src}|${edge.rel}|${edge.dst}`}>
                <button
                  type="button"
                  onClick={() => onSelect(other.id)}
                  className="flex min-h-[48px] w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left transition active:bg-gray-50"
                >
                  <Glyph type={typeByName.get(other.type)} size={12} />
                  <span className="min-w-0 flex-1">
                    <span className="block text-[11px] uppercase tracking-wide text-gray-400">
                      {side === "dst" ? edge.rel_label : `${edge.rel_label} this`}
                    </span>
                    <span className="block text-[15px] leading-snug text-dark">{other.label}</span>
                    {edge.note && (
                      <span className="block text-xs text-gray-500">{edge.note}</span>
                    )}
                  </span>
                  <ChevronIcon />
                </button>
              </li>
            );
          })}
      </ul>
    </div>
  );
}

function Figure({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl bg-light py-3">
      <dt className="text-[10px] uppercase tracking-wider text-gray-400">{label}</dt>
      <dd className="font-[family-name:var(--font-poppins)] text-xl font-bold tabular-nums text-dark">
        {value}
      </dd>
    </div>
  );
}

export function Glyph({ type, size = 14 }: { type: NodeType | undefined; size?: number }) {
  const r = size / 2;
  const path = type ? glyphPath(type.glyph, r) : null;
  const colour = type ? markColour(type.palette) : BRAND.dark;
  return (
    <svg
      width={size}
      height={size}
      viewBox={`${-r - 1} ${-r - 1} ${size + 2} ${size + 2}`}
      aria-hidden="true"
      className="shrink-0 overflow-visible"
    >
      {path ? <path d={path} fill={colour} /> : <circle r={r} fill={colour} />}
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ChevronIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true" className="shrink-0 text-gray-300">
      <path d="M6 3l5 5-5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
