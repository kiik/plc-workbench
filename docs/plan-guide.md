# Plan guide

How to plan a project: one folder per project on a machine,
`customers/<customer>/<machine>/projects/<YYYY-MM-DD>-<project>/`, dated by the day the work
started, holding `plan.md` and what only this project needs (site photos, checklists). The spec
says what the machine does and outlives the project ([spec guide](spec-guide.md)); the plan says
why, who does what by when, and what can go wrong on the way, and is closed when the project ends.
Example: [`first-install`](../customers/naidis-metall/magazine-swivel/projects/2026-10-29-first-install/plan.md).

## Rules

1. The plan holds what the spec must not: the request, people, dates, risks and history. It names
   spec items by tag, symbol or step and never restates a value from the spec.
2. Before planning activities, read the brief, goal and result against each other. Where they
   disagree, fix them first.
3. Work back from the result: for each result line, ask what must have happened before it. That
   gives the activities and their prerequisites.
4. Every activity has an owner and a no-later-than date (NLT). Without both it is not planned.
5. Put the most important and riskiest work first, so a setback still leaves time to recover; work
   that can be dropped goes last. Keep a reserve day.
6. Nothing reaches the site that could be checked before it: open questions answered, sim tests
   passed, real parts tried on the mechanics, spares on hand. Leaving a check for site is a
   decision, written in the plan.
7. Trials on a customer's machine never touch its production data: use a separate program, recipe
   or job, and switch back with the customer's check.
8. Confirm every person and partner the day depends on two days before it.
9. Write the retrospective before closing the plan. An activity that was not done is moved to a
   new date with a note, marked not done, or deleted.

## Sections

| # | Section | Contents |
|---|---|---|
| 1 | Brief | The request as the customer gave it, today's situation, and a table `\| Customer asked for \| Answered by \|` pointing into the spec |
| 2 | Team | `\| Role \| Who \| Responsible for \|`; owners in section 6 are these roles |
| 3 | Goal | What changes for the customer when the project is done |
| 4 | Result | Checkable lines in priority order, each true or false at the end |
| 5 | Constraints | What the plan must work around: site, existing equipment, production windows |
| 6 | Activities | Per phase: description, `\| Activity \| Owner \| NLT \|`, prerequisites, end result |
| 7 | Risks | Per risk: description, likelihood, impact, mitigable (fully, partly, no), countermeasures |
| 8 | Retrospective | Written after handover: the questions below, answered |

Title: `# <Station name>: project plan`, then a status line: `Status: planning`,
`Status: in progress` or `Status: closed <date>`.

## Retrospective

1. Did the project succeed: is every result line true?
2. What caused the successes and the setbacks?
3. Was the plan right? What should it have done differently, and why?
4. What to repeat and what to avoid next time, and in which situations?
5. Guidelines for the next plan. A guideline that applies to every project goes into this guide.
