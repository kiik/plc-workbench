# plc-workbench

A superrepo of automation projects: specs, project plans and PLC programs for manufacturing
equipment. Its aim is a formal set of guides precise enough that an AI agent can turn plain context
(a customer's request, notes, equipment labels) into a spec, a plan and a PLC program tested in
simulation. Every project here is written to the guides and serves as their worked example.

One folder per machine, grouped by customer; a machine is what one PLC controls.

```
customers/<customer>/<machine>/
  spec.md                            what the machine does; kept current      (spec guide)
  sources/                           drawings, labels, notes the spec is taken from
  plc/                               the program that implements the spec     (PLC guide)
  projects/<YYYY-MM-DD>-<project>/   one folder per project on the machine    (plan guide)
    plan.md                          request, people, dates, risks, retrospective
docs/                                guides
tools/<tool>/                        building, simulating and testing
```

The spec and program are the machine's and change with it; a plan belongs to one project and is
closed when it ends. A machine with several stations has one `<station>.md` per station in place
of `spec.md`.

| Guide | Covers |
|---|---|
| [Spec guide](docs/spec-guide.md) | Writing `spec.md`: modules, I/O list, step table, safety rules |
| [PLC guide](docs/plc-guide.md) | Laying out `plc/`: targets, simulation, tests |
| [Plan guide](docs/plan-guide.md) | Writing `plan.md`: activities, risks, retrospective |
| [Tools](tools/) | The `openplc` CLI: build, simulate, test |

| Customer | Machine | Spec | Program | Projects |
|---|---|---|---|---|
| `naidis-metall` (demo) | `magazine-swivel` | [spec](customers/naidis-metall/magazine-swivel/spec.md) | [`plc/`](customers/naidis-metall/magazine-swivel/plc/) | [first install](customers/naidis-metall/magazine-swivel/projects/2026-10-29-first-install/plan.md) |

The toolchain hello world is [`tools/openplc/examples/blinker`](tools/openplc/examples/blinker/).

## License

Copyright 2026 Meelik Kiik. Licensed under [Apache-2.0](LICENSE).
