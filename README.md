# plc-workbench

A superrepo of automation projects: specs, project plans and PLC programs for manufacturing
equipment. Its aim is a formal set of guides precise enough that an AI agent can turn plain context
(a customer's request, notes, equipment labels) into a spec, a plan and a PLC program tested in
simulation. Every project here is written to the guides and serves as their worked example.

One folder per machine, grouped by customer; a machine is what one PLC controls. Machines that
hand parts on to each other form a line.

```
customers/<customer>/<machine>/
  <machine>.spec.md                  what the machine does; kept current      (spec guide)
  <machine>.electrical.md            cabinet and wiring, IEC 81346 designations (electrical guide)
  sources/                           drawings, labels, notes the specs are taken from
  plc/                               the program that implements the spec     (PLC guide)
  projects/<YYYY-MM-DD>-<project>/   one folder per project on the machine    (plan guide)
    plan.md                          request, people, dates, risks, retrospective
customers/<customer>/lines/<line>/
  <line>.line.md                     stations, signals between them, on-site HMI (line guide)
library/parts/                       dimensions and ratings, one file per part
docs/                                guides
tools/<tool>/                        building, simulating and testing
```

The spec and program are the machine's and change with it; a plan belongs to one project and is
closed when it ends. A machine with several stations has one `<station>.spec.md` per station in
place of `<machine>.spec.md`.

| Guide | Covers |
|---|---|
| [Spec guide](docs/spec-guide.md) | Writing `<machine>.spec.md`: modules, I/O list, step table, safety rules |
| [Electrical guide](docs/electrical-guide.md) | Writing `<machine>.electrical.md`: IEC 81346 designations, devices, cables, connections |
| [PLC guide](docs/plc-guide.md) | Laying out `plc/`: targets, simulation, tests |
| [Line guide](docs/line-guide.md) | Writing `<line>.line.md`: transfers, ready signals, HMI |
| [Plan guide](docs/plan-guide.md) | Writing `plan.md`: activities, risks, retrospective |
| [Tools](tools/) | The `openplc` CLI: build, simulate, test. The `cabinet` CLI: check and draw cabinet layouts |

| Customer | Machine | Spec | Electrical | Program | Projects |
|---|---|---|---|---|---|
| `naidis-metall` (demo) | `magazine-swivel` | [spec](customers/naidis-metall/magazine-swivel/magazine-swivel.spec.md) | [electrical](customers/naidis-metall/magazine-swivel/magazine-swivel.electrical.md) | [`plc/`](customers/naidis-metall/magazine-swivel/plc/) | [first install](customers/naidis-metall/magazine-swivel/projects/2026-10-29-first-install/plan.md) |
| `naidis-metall` (demo) | `color-sorter` | [spec](customers/naidis-metall/color-sorter/color-sorter.spec.md) (placeholder) | — | — | — |

The demo line is [`cap-line`](customers/naidis-metall/lines/cap-line/cap-line.line.md): the magazine
and swivel station feeds the colour sorter, which reports over an IR beam when it can take a cap.

The toolchain hello world is [`tools/openplc/examples/blinker`](tools/openplc/examples/blinker/).

## License

Copyright 2026 Meelik Kiik. Licensed under [Apache-2.0](LICENSE).
