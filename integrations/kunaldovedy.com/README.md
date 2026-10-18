# The service graph on kunaldovedy.com

A mobile-first `/graph` route for the Next.js site, built against the real
repository: Next 16 App Router, React 19, Tailwind v4, Poppins and Nunito,
coral and dark. It type-checks, lints and builds clean, and `/graph`
prerenders as static.

## Install

From the root of `kunaldovedy.com`:

```bash
cp -r path/to/mygraph/integrations/kunaldovedy.com/app/graph src/app/graph
cat path/to/mygraph/integrations/kunaldovedy.com/globals.css.append >> src/app/globals.css
npm run build
```

Optionally add it to the nav in `src/app/layout.tsx`, beside Projects and
About:

```tsx
<Link href="/graph" className="hover:text-coral transition">
  Graph
</Link>
```

Nothing else in the site is touched. The route owns its own files and the two
CSS blocks are scoped to class names only it uses.

## What the reader gets on a phone

The hard part of putting a 61-node network on a 390-pixel screen is that
shrinking it does not work. This does not shrink it. It changes the
interaction instead.

- **The scroll drives the camera.** The drawing is sticky at the top of the
  screen while eight stage sections scroll beneath it. As each section comes
  into view the camera travels outward to that ring, the ring lights up in
  coral, and only that ring is named. You read the graph by scrolling, the way
  a ball bearing falls through a compressor.
- **The list is the legend.** Where a ring is too far out for a label to fit,
  the drawing stays unlabelled and the list immediately below it carries the
  full names, at full size. Neither surface repeats the other.
- **Gestures never fight the page.** The sticky drawing is tap-only and sets
  `touch-action: pan-y`, so a drag over it scrolls the page as expected. Pinch,
  pan and double-tap-to-recentre live in a full-screen **Explore** mode behind
  one button, where `touch-action: none` is correct.
- **A real bottom sheet.** Tapping a node opens a sheet with three snap points,
  drag and velocity-aware flicks, a grab handle, and safe-area padding for the
  home indicator. Connections inside it are rows you tap to walk the graph, and
  the drawing follows you.
- **Touch targets.** Every node carries an invisible hit circle of at least 44
  CSS pixels whatever the zoom, and every row in every list is at least 48.
- **Type stays put.** Labels, strokes and hit areas are sized in screen pixels
  and divided back out by the camera scale, so zooming never produces
  seven-pixel text.
- **It respects the reader.** No hover is required anywhere. Page zoom is not
  disabled. `prefers-reduced-motion` turns off the camera easing and the pulse.
  Focus is a ring, not a square box, and nodes are reachable by keyboard.

## Weight

Measured on an emulated iPhone 13 against the production build:

| Measure | Value |
|---|---|
| Transferred | 292 KB |
| Uncompressed | 894 KB |
| First contentful paint | 200 ms |
| DOM interactive | 90 ms |

Most of that is the React and Next runtime the rest of the site already loads.
The graph's own data is 46 KB of JSON, imported into the client chunk rather
than passed as a prop, so it is cached as a file instead of being re-sent
inside the HTML on every visit.

## The files

| File | What it does |
|---|---|
| `page.tsx` | Server component: metadata, `viewportFit: "cover"`, JSON-LD |
| `ServiceGraph.tsx` | The scroll-driven shell, stage sections, index, search |
| `GraphCanvas.tsx` | The SVG drawing, camera, gestures, labels |
| `NodeSheet.tsx` | Bottom sheet on a phone, card on a wide screen |
| `geometry.ts` | Pure layout maths: rings, glyph paths, camera |
| `palette.ts` | Colour, and why coral is never a node's identity |
| `types.ts` | The shape of the data |
| `graph-data.json` | Generated. Do not edit by hand. |

`geometry.ts` is deliberately not called `layout.ts`: in the App Router that
filename is a reserved route file and the build will reject it.

## Keeping the data current

The JSON is generated from the graph in `mygraph/`. After editing any YAML
there:

```bash
cd path/to/mygraph
make site-data SITE=/path/to/kunaldovedy.com
```

That writes `src/app/graph/graph-data.json`. Rebuild the site and the page
changes with it.
