"use client";

import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import {
  BOX,
  CENTRE,
  cameraTransform,
  glyphPath,
  nodeRadius,
  ringRadius,
  scaleForStage,
} from "./geometry";
import { BRAND, markColour } from "./palette";
import type { NodeType, PlacedEdge, PlacedNode } from "./types";

/** The smallest comfortable touch target, in CSS pixels. */
const TAP_TARGET = 44;

type Props = {
  nodes: PlacedNode[];
  edges: PlacedEdge[];
  nodeTypes: NodeType[];
  maxRank: number;
  activeStage: number;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  /** Full gestures: pinch, pan, double-tap. Off while the page scrolls past. */
  interactive?: boolean;
  className?: string;
};

type Camera = { k: number; x: number; y: number };

export default function GraphCanvas({
  nodes,
  edges,
  nodeTypes,
  maxRank,
  activeStage,
  selectedId,
  onSelect,
  interactive = false,
  className = "",
}: Props) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [size, setSize] = useState({ w: 390, h: 390 });
  // The camera follows the scroll until the reader takes hold of it. Holding
  // that as "null means follow the scroll" keeps it derived, so there is no
  // effect writing state back on every stage change.
  const [held, setHeld] = useState<Camera | null>(null);
  const camera: Camera = held ?? { k: scaleForStage(activeStage), x: 0, y: 0 };
  const reduced = usePrefersReducedMotion();

  const typeBySlot = useMemo(
    () => new Map(nodeTypes.map((t) => [t.name, t])),
    [nodeTypes],
  );

  /* --------------------------------------------------------------- sizing */
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const observer = new ResizeObserver((entries) => {
      const box = entries[0]?.contentRect;
      if (box?.width && box?.height) setSize({ w: box.width, h: box.height });
    });
    observer.observe(svg);
    return () => observer.disconnect();
  }, []);

  /** User units per CSS pixel, so type and hit targets stay a constant size. */
  const unitsPerPx = BOX / Math.max(1, Math.min(size.w, size.h));
  /** Half the shorter side: how far a label can run before it leaves the frame. */
  const halfFrame = Math.min(size.w, size.h) / 2;
  const px = useCallback(
    (cssPixels: number) => (cssPixels * unitsPerPx) / camera.k,
    [unitsPerPx, camera.k],
  );

  /* --------------------------------------------------------------- camera */
  const reset = useCallback(() => setHeld(null), []);

  /* ------------------------------------------------------------- gestures */
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const gesture = useRef<{ dist: number; k: number; x: number; y: number } | null>(null);
  const panStart = useRef<{ x: number; y: number; cx: number; cy: number } | null>(null);
  const moved = useRef(false);

  const onPointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!interactive) return;
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    moved.current = false;
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      gesture.current = {
        dist: Math.hypot(a.x - b.x, a.y - b.y),
        k: camera.k,
        x: camera.x,
        y: camera.y,
      };
      setHeld(camera);
      panStart.current = null;
    } else if (pointers.current.size === 1) {
      panStart.current = { x: event.clientX, y: event.clientY, cx: camera.x, cy: camera.y };
    }
    (event.target as Element).setPointerCapture?.(event.pointerId);
  };

  const onPointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!interactive || !pointers.current.has(event.pointerId)) return;
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });

    if (pointers.current.size === 2 && gesture.current) {
      const [a, b] = [...pointers.current.values()];
      const dist = Math.hypot(a.x - b.x, a.y - b.y);
      const ratio = dist / (gesture.current.dist || 1);
      const k = clamp(gesture.current.k * ratio, 0.75, 7);
      moved.current = true;
      setHeld((current) => ({ ...(current ?? camera), k }));
      return;
    }
    if (panStart.current) {
      const dx = (event.clientX - panStart.current.x) * unitsPerPx;
      const dy = (event.clientY - panStart.current.y) * unitsPerPx;
      if (Math.abs(dx) + Math.abs(dy) > 6) {
        moved.current = true;
        setHeld((current) => ({
          ...(current ?? camera),
          x: panStart.current!.cx + dx,
          y: panStart.current!.cy + dy,
        }));
      }
    }
  };

  const endPointer = (event: React.PointerEvent<SVGSVGElement>) => {
    pointers.current.delete(event.pointerId);
    if (pointers.current.size < 2) gesture.current = null;
    if (pointers.current.size === 0) panStart.current = null;
  };

  const onWheel = (event: React.WheelEvent<SVGSVGElement>) => {
    if (!interactive) return;
    event.preventDefault();
    const factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
    setHeld((current) => {
      const base = current ?? camera;
      return { ...base, k: clamp(base.k * factor, 0.75, 7) };
    });
  };

  // A wheel listener has to be non-passive to call preventDefault.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg || !interactive) return;
    const stop = (e: Event) => e.preventDefault();
    svg.addEventListener("wheel", stop, { passive: false });
    return () => svg.removeEventListener("wheel", stop);
  }, [interactive]);

  /* ----------------------------------------------------------- selection */
  const pick = (id: string) => {
    if (moved.current) return; // that was a drag, not a tap
    onSelect(id === selectedId ? null : id);
    if (typeof navigator !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate?.(8);
      } catch {
        /* vibration is a nicety, never a requirement */
      }
    }
  };

  const litEdges = useMemo(() => {
    if (!selectedId) return new Set<string>();
    const set = new Set<string>();
    edges.forEach((e, i) => {
      if (e.src === selectedId || e.dst === selectedId) set.add(String(i));
    });
    return set;
  }, [edges, selectedId]);

  const neighbours = useMemo(() => {
    if (!selectedId) return null;
    const set = new Set<string>([selectedId]);
    for (const e of edges) {
      if (e.src === selectedId) set.add(e.dst);
      if (e.dst === selectedId) set.add(e.src);
    }
    return set;
  }, [edges, selectedId]);

  const transition = reduced ? "none" : "transform 620ms cubic-bezier(0.22, 1, 0.36, 1)";

  return (
    <div className={`relative ${className}`}>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${BOX} ${BOX}`}
        className="block h-full w-full select-none"
        style={{ touchAction: interactive ? "none" : "pan-y" }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endPointer}
        onPointerCancel={endPointer}
        onWheel={onWheel}
        onDoubleClick={reset}
        role="img"
        aria-label="Radial diagram of a service graph. The index below the diagram carries the same information as text."
      >
        <g
          style={{
            transform: cameraTransform(camera.k, camera.x, camera.y),
            transformOrigin: "0 0",
            transition,
          }}
        >
          {/* rings */}
          {RING_STAGES.map((stage) => {
            const active = stage === activeStage;
            return (
              <circle
                key={stage}
                cx={CENTRE}
                cy={CENTRE}
                r={ringRadius(stage)}
                fill="none"
                stroke={active ? BRAND.coral : BRAND.rule}
                strokeWidth={px(active ? 1.5 : 1)}
                strokeOpacity={active ? 0.9 : 0.8}
                style={{ transition: reduced ? "none" : "stroke 400ms linear" }}
              />
            );
          })}

          {/* edges */}
          {edges.map((edge, i) => {
            const lit = litEdges.has(String(i));
            const onActiveRing = edge.a.stage === activeStage || edge.b.stage === activeStage;
            // Nothing recedes in the opening frame: stage 0 is the whole machine.
            const dim = selectedId ? !lit : activeStage !== 0 && !onActiveRing;
            return (
              <path
                key={`${edge.src}|${edge.rel}|${edge.dst}`}
                d={edge.d}
                fill="none"
                stroke={edge.kind === "return" ? "#8d84c4" : lit ? BRAND.coralInk : BRAND.faint}
                strokeWidth={px(lit ? 2 : 1)}
                strokeOpacity={dim ? 0.12 : lit ? 1 : 0.45}
                strokeDasharray={edge.kind === "return" ? `${px(3)} ${px(4)}` : undefined}
                markerEnd={lit ? "url(#graph-tip)" : undefined}
              />
            );
          })}

          {/* nodes */}
          {nodes.map((node) => {
            const type = typeBySlot.get(node.type);
            const r = nodeRadius(node, maxRank);
            const colour = node.type === "person" ? BRAND.dark : markColour(type?.palette ?? "blue");
            const path = glyphPath(type?.glyph ?? "circle", r);
            const selected = node.id === selectedId;
            const onActiveRing = node.stage === activeStage;
            const near = !neighbours || neighbours.has(node.id);
            const dim = selectedId
              ? !near
              : activeStage !== 0 && !onActiveRing && node.stage !== 0;
            const unsure = node.source === "inferred" || node.confidence === "low";
            // Named when its ring is in view, when it is selected, or when it
            // sits next to the selection. Naming all sixty at once is noise.
            const named = selected || (neighbours ? near : onActiveRing || node.stage === 0);

            return (
              <g
                key={node.id}
                transform={`translate(${node.x.toFixed(1)} ${node.y.toFixed(1)})`}
                opacity={dim ? 0.18 : 1}
                style={{ transition: reduced ? "none" : "opacity 400ms linear" }}
              >
                {/* a tap target that is always at least 44 CSS pixels across */}
                <circle
                  r={Math.max(r + px(6), px(TAP_TARGET) / 2)}
                  fill="transparent"
                  className="graph-hit cursor-pointer"
                  onPointerUp={() => pick(node.id)}
                  tabIndex={0}
                  role="button"
                  aria-label={`${node.label}, ${type?.label ?? node.type}`}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onSelect(node.id === selectedId ? null : node.id);
                    }
                  }}
                />
                {selected && (
                  <circle
                    r={r + px(9)}
                    fill="none"
                    stroke={BRAND.coral}
                    strokeWidth={px(2.5)}
                    className={reduced ? undefined : "graph-pulse"}
                  />
                )}
                {node.type === "person" && (
                  <circle r={r + 7} fill="none" stroke={BRAND.dark} strokeWidth={px(1.5)} />
                )}
                {path ? (
                  <path
                    d={path}
                    fill={colour}
                    fillOpacity={unsure ? 0.4 : 1}
                    stroke="#ffffff"
                    strokeWidth={px(1.2)}
                    strokeDasharray={unsure ? `${px(2)} ${px(2)}` : undefined}
                    pointerEvents="none"
                  />
                ) : (
                  <circle
                    r={r}
                    fill={colour}
                    fillOpacity={unsure ? 0.4 : 1}
                    stroke="#ffffff"
                    strokeWidth={px(1.2)}
                    pointerEvents="none"
                  />
                )}
                {named && (
                  <NodeLabel
                    node={node}
                    r={r}
                    fontSize={px(node.type === "person" ? 14 : 11)}
                    gap={px(7)}
                    roomOutPx={
                      halfFrame -
                      (Math.hypot(node.x - CENTRE, node.y - CENTRE) * camera.k) / unitsPerPx -
                      10
                    }
                    roomInPx={
                      (Math.hypot(node.x - CENTRE, node.y - CENTRE) * camera.k) / unitsPerPx - 18
                    }
                    emphasis={selected}
                  />
                )}
              </g>
            );
          })}
        </g>

        <defs>
          <marker
            id="graph-tip"
            viewBox="0 0 8 8"
            refX="7"
            refY="4"
            markerWidth="5"
            markerHeight="5"
            orient="auto-start-reverse"
          >
            <path d="M0 0.6 L8 4 L0 7.4 Z" fill={BRAND.coralInk} />
          </marker>
        </defs>
      </svg>

      {interactive && (
        <button
          type="button"
          onClick={reset}
          className="absolute bottom-3 right-3 rounded-full border border-gray-200 bg-white/90 px-3 py-2 text-xs font-medium text-gray-600 shadow-sm backdrop-blur active:scale-95"
        >
          Re-centre
        </button>
      )}
    </div>
  );
}

const RING_STAGES = [1, 2, 3, 4, 5, 6, 7];

function NodeLabel({
  node,
  r,
  fontSize,
  gap,
  roomOutPx,
  roomInPx,
  emphasis,
}: {
  node: PlacedNode;
  r: number;
  fontSize: number;
  gap: number;
  roomOutPx: number;
  roomInPx: number;
  emphasis: boolean;
}) {
  // Labels read outward, the way the drawing does. On a narrow screen the outer
  // rings run out of room before a name fits, and half a word names nothing, so
  // the label is dropped: the list beside the drawing already says it in full.
  // The one exception is the node the reader has chosen. That name is worth the
  // space, so it turns and reads inward across the middle, which is empty by
  // then because everything else has dimmed.
  const flip = emphasis && roomOutPx < 72 && roomInPx > roomOutPx;
  const room = flip ? roomInPx : roomOutPx;
  if (node.type !== "person" && room < 72) return null;
  const limit = Math.max(10, Math.min(32, Math.floor(room / 6.2)));
  const text =
    node.label.length > limit ? `${node.label.slice(0, limit - 1).trimEnd()}…` : node.label;
  const common = {
    fontSize,
    fill: BRAND.dark,
    stroke: "#ffffff",
    strokeWidth: fontSize * 0.34,
    paintOrder: "stroke" as const,
    strokeLinejoin: "round" as const,
    pointerEvents: "none" as const,
    fontWeight: node.type === "person" ? 700 : 600,
  };

  if (node.type === "person") {
    return (
      <text {...common} x={0} y={r + gap + fontSize} textAnchor="middle">
        {text}
      </text>
    );
  }
  const left = Math.cos(node.angle) < 0;
  const degrees = (node.angle * 180) / Math.PI + (left ? 180 : 0);
  // "left" keeps the type upright on the left-hand side of the circle;
  // the flip decides which side of the node the name sits on.
  const away = flip ? left : !left;
  return (
    <text
      {...common}
      x={away ? r + gap : -(r + gap)}
      y={fontSize * 0.34}
      textAnchor={away ? "start" : "end"}
      transform={`rotate(${degrees.toFixed(1)})`}
    >
      {text}
    </text>
  );
}

function clamp(value: number, low: number, high: number): number {
  return Math.min(high, Math.max(low, value));
}

function usePrefersReducedMotion(): boolean {
  return useSyncExternalStore(
    (notify) => {
      const query = window.matchMedia("(prefers-reduced-motion: reduce)");
      query.addEventListener("change", notify);
      return () => query.removeEventListener("change", notify);
    },
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    () => false,
  );
}
