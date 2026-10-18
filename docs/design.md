# Why it looks the way it does

## The subject sets the form

The Turbinophone is a J79 turbojet compressor that you play by dropping steel
ball bearings into the top. The bearing strikes each stage of blades on the way
down, and because the blades get shorter, the pitch rises as it falls.

A compressor is a set of concentric stages seen end-on. So is this graph. The
bearing goes in at the centre and the sound comes out at the rim, and the
diagram is a compressor face: eight rings, read outward.

That is the whole visual thesis. The rings are not decoration; ring number is
stage number, and stage number is a real property of every node.

## Colour

Eight node kinds draw from a categorical set of hues validated for
colour-vision deficiency: each adjacent pair clears a separation of
Delta E >= 8 (OKLab x100) in both light and dark mode, and the normal-vision
floor of 15.

A network diagram is an all-pairs case, though. Every kind is on screen at
once, and no eight-hue set clears the all-pairs floor. So colour never carries
identity alone here:

- **every kind has its own glyph** — the centre is a ringed disc, values are
  diamonds, practices circles, capabilities triangles, works squares, vehicles
  hexagons, audiences pentagons, outcomes crosses;
- **the legend is always present**, with the glyph beside each name;
- **a sortable table** below the diagram carries the same data as text.

The person at the centre is painted in ink rather than a series colour. They
are not one category among eight; they are the thing the categories describe.

Both themes are selected rather than flipped. The dark column is the same eight
hues re-stepped for a dark surface and validated against it.

## Neutrals

A cool graphite with a slight blue bias, matching the accent, rather than a
neutral grey or a warm cream. Steel, not paper.

## Type

| Role | Face | Why |
|---|---|---|
| Display | Archivo 700/800, tight tracking | An industrial grotesque. It reads as a placard on a machine. |
| Body | Spectral | A serif, because the summaries are prose and deserve to be read as prose. |
| Data | IBM Plex Mono | Labels, ids, measurements, anything that lines up in a column. |

## What the drawing shows and what it withholds

Naming all sixty-one nodes at once buries the picture. At rest the diagram
labels the centre, the values, the practices, the audiences and the outcomes —
which is to say, the whole sentence of *how I serve the world*. Stages three to
five are the machinery, and they speak when you hover, focus or select them.

Direction is the same idea. Arrowheads on a hundred and forty-two edges is
noise, so arrowheads appear on the edges you light up.

## Honest drawing

A node whose source is `inferred`, or whose confidence is `low`, is drawn
hollow with a dashed edge. The header counts them under **Still to confirm**.
Someone reading the picture can see, without clicking anything, which parts of
this account are sourced and which are a reasonable guess.

## Motion

One settling animation in the free layout, and nothing else. Under
`prefers-reduced-motion` the simulation runs to completion in a single frame
and the page draws the result. Nothing important is revealed on scroll: the
first still frame carries the argument.
