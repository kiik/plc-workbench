# cabinet

CLI for the mounting plates in a machine's electrical spec: checks rail fill, plate height and
power loss, and draws a front view. Reads the Devices and Layout sections of
`customers/<customer>/<machine>/<machine>.electrical.md` and the [parts library](../../library/parts/)
files their Part columns link to. Python 3.11+, standard library only.

```sh
tools/cabinet/cabinet.py check  customers/naidis-metall/magazine-swivel/magazine-swivel.electrical.md
tools/cabinet/cabinet.py check  <spec> --json
tools/cabinet/cabinet.py render <spec>                 # build/cabinet/<location>.svg next to the spec
tools/cabinet/cabinet.py render <spec> -o <dir>
python3 -m unittest discover -s tools/cabinet/tests    # tests, on fictional fixtures
```

The format of the Layout section and the parts files is in the
[electrical guide](../../docs/electrical-guide.md). Sections are found by heading text (`Devices`,
`Layout`) and tables by their header row, so numbering and column order do not matter. Part links
are resolved relative to the spec.

## check

Per enclosure location:

| Figure | Sum | Limit |
|---|---|---|
| Rail fill, one per rail | Widths of the rail's devices | Plate width |
| Height | Row heights: a duct's given height, a rail's tallest device (at least 35 mm, TS35) | Plate height |
| Power loss | Power loss of the devices on the plate's rails | Enclosure Max power loss |

Then every value it had to assume, and warnings: a device on no rail in its cabinet, a value in a
part file without a source (treated as `?`), a broken part link.

| Exit | When |
|---|---|
| 0 | Nothing over its limit, or over only with assumed values ("may overflow") |
| 1 | A definite overflow: the known values alone exceed a known limit |
| 2 | An error: file not readable, no Devices or Layout section or table |

`--json` prints one JSON object: `enclosures` with `rows`, devices and `x`/`y` placements,
`height`, `power` and `unknowns`, plus `warnings` and `overflow`. An error prints `{"error": …}`.

## render

One SVG per enclosure location, `<dir>/<location without +>.svg` (`+CAB1` → `CAB1.svg`), default
`build/cabinet/` next to the spec (gitignored). Front view to scale: 1 mm = 1 SVG unit, viewBox in
mm. A planning aid, not a manufacturing drawing.

| Drawn | As |
|---|---|
| Plate | Outline; dashed when its size is unknown |
| Rail | Thin grey bar across the plate, rows top to bottom |
| Device | Rectangle centred on its rail, with designation and Label; dashed with `?` when a dimension is unknown; red when its width is known and it runs past the plate |
| Duct | Hatched band; dashed with `?` when its height is unknown |

## Assumed values

Unknown values are never guessed silently: each is listed by `check` and drawn dashed.

| Unknown | Assumed |
|---|---|
| Device width × height | 45 × 90 mm |
| Duct height | 60 mm |
| Plate width × height | 600 × 800 mm |
| Device power loss | Not counted |
| Enclosure Max power loss | Power not checked |

Heat is a sum of power loss against the enclosure's Max power loss; a full IEC/TR 60890
temperature-rise calculation is out of scope.
