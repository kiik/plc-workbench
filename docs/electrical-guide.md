# Electrical guide

How to write a machine's electrical spec: one Markdown file per machine,
`customers/<customer>/<machine>/<machine>.electrical.md`, next to the machine spec. The machine spec
says what each signal means and which PLC terminal it uses ([spec guide](spec-guide.md)); the
electrical spec says how the cabinet and field wiring carry it: devices, supply, protection, the
safety circuit, cables, every connection and the cabinet layout. Electricians build and check the
cabinet from the connection list; schematics are drawn from this spec ([Drawings](#drawings)).
Example: [`magazine-swivel`](../customers/naidis-metall/magazine-swivel/magazine-swivel.electrical.md).

## Rules

1. Never invent a part, rating or connection. Take them from labels, datasheets or drawings;
   unknowns are `?` with an open question, as in the machine spec.
2. Each fact lives in one place. The machine spec's I/O list owns tag → PLC terminal and is not
   repeated here; the connection list owns every conductor; every I/O list address is the end of
   exactly one connection.
3. Every device has one reference designation. The device table is the only place that maps a
   PLC tag (`1S1`) to a designation (`=MAG+ST1-BG1`).
4. Safety functions act in hardware. Section 4 says what each emergency stop cuts; the machine
   spec's I/O list description says the same (spec safety rule 8).
5. Change a value only on evidence. A wire changed on site comes back as a marked-up photo in
   `sources/`, and the commit names it.
6. Agents do not switch power or work on live equipment ([spec rule 4](spec-guide.md#rules)).
7. Dimensions and ratings of a part live in the [parts library](#parts-library), once per part,
   not in the spec. The spec links the part and keeps only its own choices, such as a fuse's
   rating in section 3.

## Reference designations (IEC 81346)

`=<function>+<location>-<product>:<terminal>`, for example `=MAG+ST1-BG1:4`.

| Aspect | Sign | Here | Example |
|---|---|---|---|
| Function | `=` | The machine module (spec section 1) the device serves | `=MAG` |
| Location | `+` | Where it is mounted: cabinet, operator panel, station plate | `+CAB1`, `+ST1` |
| Product | `-` | Letter code, then a number per code within the function, in channel order | `-BG1` |
| Terminal | `:` | Exactly as labeled on the device | `:I1`, `:4` |

Equipment shared by all modules (PLC, supply, protection, distribution terminals) has no function
aspect: `+CAB1-KE1`. A device that already carries a label (`XMA2`, `PNL2`) keeps it, in the device
table's Label column.

### Letter codes

Two-letter subclasses of IEC 81346-2:2019. Sources: [W] the
[Wikipedia table](https://en.wikipedia.org/wiki/IEC_81346), [L] the
[fisekon letter-code lookup](https://fisekon.com/en/calculators/letter-codes/). Codes marked
"verify" are not confirmed by both; check every code against the standard before the first cabinet
is labeled, and record the result here.

| Code | Class | Used for | Source |
|---|---|---|---|
| `BG` | Sensing position, distance and dimensions | Cylinder switches, part-present sensors, IR receivers | L; verify |
| `BP` | Sensing pressure | Vacuum and pressure switches | verify |
| `FC` | Protection against overcurrent | Fuses, miniature circuit breakers | W, L |
| `KE` | Control unit, program-controlled processing | PLC | W, L |
| `KF` | Passing on electrical signals | Interface relays, safety relay | L; verify |
| `MB` | Electromagnetic linear drive | Valve solenoid coils | L; verify |
| `MM` | Fluid power drive | Cylinders, swivels (field, not wired) | L; verify |
| `PF` | Visual indication of states | Indicator lamps | W, L |
| `QA` | Switching electric current | Contactors, circuit breakers used as switches | W, L |
| `QM` | Shutting off media in closed lines | Valve islands, shut-off valves | L; verify |
| `SJ` | Operation by finger | Push buttons, key switches, emergency stop | W, L; verify for emergency stop |
| `TC` | Power supply with AC or DC input | 24 V DC power supplies | W, L |
| `WD` | Conductors for low voltage | Power cables | W, L |
| `WG` | Lines for electrical signals | Sensor, control and I/O cables | W, L |
| `XD` | Low-voltage connections | Terminal strips | W, L |
| `XG` | Connections for electrical signals | I/O connectors and terminal blocks | L; verify |

Conductor colours follow EN 60204-1, 13.2.4: black for AC and DC power circuits, red for AC
control, blue for DC control, orange for circuits fed from outside the machine, green-yellow for
protective earth only.

A designation names a device; a PLC tag (`1S1`, `3Y1A`, [spec guide](spec-guide.md#tags)) names
a signal. They are different schemes, joined only in the device table (rule 3).

### Older drawings

Drawings made before IEC 81346-2, and many EPLAN projects, use one-letter codes (IEC 60750,
DIN 40719-2): `-S1`, `-K1`. Read them with this table, and write this guide's codes in the spec;
keep the drawing's designation in the device table's Label column. Source: IEC 60750; verify.

| Old | Class | Here |
|---|---|---|
| `B` | Transducers, sensors | `BG`, `BP` |
| `F` | Protective devices | `FC` |
| `G` | Generators, power supplies | `TC` |
| `H` | Signalling devices | `PF` |
| `K` | Relays, contactors, PLC | `KF`, `QA`, `KE` |
| `Q` | Power switching | `QA` |
| `S` | Switches, push buttons | `SJ` |
| `W` | Cables | `WD`, `WG` |
| `X` | Terminals, plugs | `XD`, `XG` |
| `Y` | Electrically operated mechanical devices, valve coils | `MB` |

### Terminal markings

The terminal after `:` is what the device's label reads (aspect table above). These are the
markings labels usually carry; use them to check a label, never to fill a `:?` without one.

| Device | Terminals | Source |
|---|---|---|
| Coil: relay, contactor | `A1`, `A2` | IEC 60947-1 Annex L; verify |
| Contactor main poles | `1`-`2`, `3`-`4`, `5`-`6` | IEC 60947-1 Annex L; verify |
| Auxiliary contact | Two digits: first is the contact's position on the device, second its function: `1`-`2` NC, `3`-`4` NO, `1`-`2`-`4` changeover (`11`-`12`, `13`-`14`) | IEC 60947-1 Annex L; verify |
| Indicator lamp | `X1`, `X2` | IEC 60947-1 Annex L; verify |
| M12 sensor, 4 pins | `1` brown L+, `2` white, `3` blue 0 V, `4` black output | IEC 60947-5-2; verify |

A push button's NC block is therefore `=PNL+OP1-SJ2:11` and `:12` when its label reads so.

## Spec sections

| # | Section | Contents |
|---|---|---|
| 1 | Locations | `\| Location \| Name \| Notes \|` |
| 2 | Devices | `\| Designation \| Label \| Tag \| Name \| Part \|`: every device, with its PLC tag where it has one; Part links a `library/parts/` file, or is `?` |
| 3 | Supply and protection | `\| Designation \| Feeds \| Rating \|`: incoming supply, power supplies, protection |
| 4 | Safety circuit | Each safety function: devices, what it cuts, stop category |
| 5 | Cables | `\| Cable \| Type \| From \| To \| Cores \|` |
| 6 | Connections | `\| From \| To \| Via \| Size \| Colour \|`: one row per conductor, ends as `<designation>:<terminal>`, Via the cable and core |
| 7 | Layout | Enclosures `\| Location \| Part \| Notes \|`: one row per enclosure location, Part a parts-library link or `?`. Rows `\| Location \| Row \| Kind \| Height \| Contents \|`: rails and ducts on its mounting plate |
| 8 | Open questions | `- [ ] **?n** …`, numbered per file |

Title: `# <Station name>: electrical`, then a status line as in the machine spec.

The Layout section puts its two tables under the subheadings `### Enclosures` and `### Rows`.

Layout rows run top to bottom, numbered 1, 2, … per location:

| Column | Rail | Duct |
|---|---|---|
| Kind | `rail`: TS35 DIN rail, as long as the plate is wide | `duct`: wiring duct |
| Height | Empty: as tall as its tallest device | In mm (`60`), or `?` |
| Contents | Designations from the device table, left to right as mounted, comma-separated, each in backticks | Empty |

## Parts library

One file per part, `library/parts/<maker>-<order-number>.md` (lowercase, spaces and slashes as
`-`), shared by every machine. It holds the part's dimensions, mounting, power loss and datasheet;
an enclosure adds its plate size and the power loss it can dissipate. Every value names its source
(datasheet page, label photo in `sources/`); a value without one is not written. Format:
[`library/parts/README.md`](../library/parts/README.md).

## Drawings

The repo is the master for devices, connections and layout order. Drawings are made from it, never
the other way round.

| Drawing | Made with | Kept |
|---|---|---|
| Cabinet front view (SVG) | [`tools/cabinet`](../tools/cabinet/) | Not committed; rebuilt |
| Terminal plans, wire labels | From the connection list (later) | Not committed; rebuilt |
| Cable diagrams (optional) | WireViz, from YAML | Not committed; rebuilt |
| Schematics (IEC 61082) | ECAD tool: QElectroTech, or EPLAN when the customer requires it | Exported PDFs as evidence in `sources/` |

- Schematics are needed for EN 60204-1 and the ISO 13849 safety circuit. QElectroTech is open
  source and its XML projects diff in git. The ECAD tool owns only where symbols sit on the sheet.
- The front view is a planning aid, not a manufacturing drawing: no bend radii, bundles or 3D
  clearances.
- Heat: the check sums the devices' power loss against the enclosure's Max power loss. A full
  IEC/TR 60890 temperature-rise calculation is out of scope.
- WireViz and QElectroTech are GPL: run them, do not copy their code into this Apache-2.0 repo.

### Reading a schematic

A customer's schematic in `sources/` is evidence for devices and connections. Symbols are IEC 60617;
take their meaning from the drawing's legend or the ECAD tool's library, not from memory.

- Contacts are drawn at rest: unpowered, not operated. An NC stop button is drawn closed.
- A coil and its contacts share one designation. A table under the coil names the sheet and column
  of each contact: `/3.4` is sheet 3, column 4 (IEC 61082).
- Supply runs top to bottom: +24 V at the top, 0 V at the bottom.
- A dashed line is a mechanical link: an actuator and its contacts, or the poles of one contactor.
- A value taken from a schematic names its file, sheet and column, here and in the commit.

Check fill, height and heat, then draw the front view to `build/cabinet/` next to the spec:

```
python3 tools/cabinet/cabinet.py check customers/<customer>/<machine>/<machine>.electrical.md
python3 tools/cabinet/cabinet.py render customers/<customer>/<machine>/<machine>.electrical.md
```

`check` exits 1 only on a definite overflow; unknowns are warnings.
