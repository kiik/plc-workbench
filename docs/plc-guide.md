# PLC guide

How to lay out a PLC program: one per machine, `customers/<customer>/<machine>/plc/`, next to the
spec it implements. The CLI finds it by machine name. Programs are IEC 61131-3 Structured Text in plain `.st`
files, compiled by matiec as in OpenPLC v3; the same code ports to CODESYS, TwinCAT and Siemens
SCL. Example: [`magazine-swivel`](../customers/naidis-metall/magazine-swivel/plc/).

## Layout

| Path | Contents |
|---|---|
| `plc.toml` | `spec` path, relative to `plc.toml`; one `[targets.<name>]` per build, listing its `sources` in order |
| `src/` | Logic: types, programs, function blocks. No addresses |
| `targets/<name>.st` | One `CONFIGURATION Config0` (the name OpenPLC v3 requires) per target: the I/O map (`VAR_GLOBAL` with `AT %…`) and tasks |
| `s7/` | Optional Siemens S7-1200/1500 port, as TIA Portal external sources: the logic as one SCL function block, `<Machine>.scl`; `Main.scl` with its instance DB, OB100 and OB1, the I/O map; `sim_station.st`, which calls the block in simulation |
| `tests/` | `test_*.py` scenario tests, run against every `sim` target |
| `build/` | Generated, not in git: `build/<target>.st`, the single file uploaded to OpenPLC |

Targets:

- `hw`: the real PLC. Addresses come from the spec's I/O list; where the spec has `?`, the symbol
  is declared without `AT` at its safe value and the comment names the tag.
- `sim`: OpenPLC in Docker. A `PlantSim` program in `src/plant_sim.st` stands in for the machine:
  it reads the outputs and writes the inputs. All symbols sit on coils (`%QX`) and holding
  registers (`%QW`) so a Modbus client can read and write them; sim-only symbols start with `SIM_`.
- `sim-s7`: the `sim` target with the S7 block in place of `src/`. The CLI translates `.scl`
  sources for matiec (block attributes, `#` locals, quoted names, `TON_TIME`, constants as `CASE`
  labels), so the same plant model and tests run against the SCL logic. TIA Portal is still the
  only check that the sources import and compile on Siemens.

## Rules

1. The logic in `src/` is the spec's step table, implemented as in
   [Implementing](spec-guide.md#implementing). Step and symbol names are the spec's.
2. Programs reach I/O only through `VAR_EXTERNAL`; only `targets/` have addresses.
3. A change to the spec's control section changes `src/`, `s7/` and `tests/` in the same commit,
   and the tests pass on every sim target.
4. The S7 port is the step table as in [Implementing](spec-guide.md#implementing): steps are local
   `Int` constants valued like the step (`S90_HomingRequired` = 90), so `StepNo` is the step itself;
   I/O symbols are the block's parameters, wired to addresses only in OB1.
5. Programs are run and tested only on the local simulation runtime. Agents do not download to a
   PLC on a machine ([spec rule 4](spec-guide.md#rules)); the CLI refuses non-local runtimes.

## Commands

[`tools/openplc`](../tools/openplc/) does the work:

```sh
tools/openplc/openplc.py up                                  # start the local runtime
tools/openplc/openplc.py check magazine-swivel -t hw          # compile a target with matiec
tools/openplc/openplc.py test magazine-swivel                # deploy sim, run tests/
tools/openplc/openplc.py test magazine-swivel -t sim-s7      # the same against the S7 port
```
