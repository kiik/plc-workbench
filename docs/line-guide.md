# Line guide

How to write a line spec: one Markdown file per line, `customers/<customer>/lines/<line>/<line>.line.md`.
A line is machines in flow order that hand parts on to each other. The line spec owns what lies
between them: the transfers, the signals that keep them in step, shared emergency stop zones and the
on-site HMI. Each machine spec owns its own end of a signal: its I/O list row (module `LNK`) and the
steps that use it ([spec guide](spec-guide.md)). Projects that change the line have their plans in
`lines/<line>/projects/` ([plan guide](plan-guide.md)).
Example: [`cap-line`](../customers/naidis-metall/lines/cap-line/cap-line.line.md).

## Rules

1. Never invent a signal, address or connection (spec rule 1). Unknowns are `?` with an open
   question.
2. Each signal between machines is listed once, here, with both ends as machine, tag and symbol.
3. The downstream machine says when it can take a part. The upstream machine moves into the
   transfer point only while that signal reads 1; a broken beam or wire reads 0, so it waits (spec
   safety rule 9).
4. Waiting for a neighbour is a step of its own with no timeout, and it keeps checking what the
   machine holds (part lost).
5. The HMI reads the machines' symbols. It writes only what the HMI section lists, never an output
   or a safety signal; Reset and Start stay on the machines' panels.

## Spec sections

| # | Section | Contents |
|---|---|---|
| 1 | Stations | `\| # \| Machine \| Spec \| Role \|` in flow order |
| 2 | Transfers | `\| From \| To \| Transfer point \| Ready signal \|` |
| 3 | Signals | `\| Signal \| Sender \| Receiver \| Medium \| 1 = \|`; sender and receiver as machine, tag, symbol |
| 4 | Emergency stop zones | `\| Zone \| Emergency stops \| Stops \|` |
| 5 | HMI | Device, location and connection; `\| Screen \| Shows \| Operator can \|`; `\| Machine \| Alarm \| Text \|` |
| 6 | Open questions | `- [ ] **?n** …`, numbered per file |

Title: `# <Line name>`, then a status line as in the machine spec.
