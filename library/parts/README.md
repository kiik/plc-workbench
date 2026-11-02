# Parts library

One Markdown file per part: what it is, how big it is and how much heat it gives off, each value
with where it was read. Electrical specs link to these files from the device table's Part column
and from the Layout section's Enclosures table, so dimensions and ratings are not repeated in each
spec. The cabinet tool (`tools/cabinet/`) reads them to check rail fill, plate height and power
loss. See the [electrical guide](../../docs/electrical-guide.md).

## Files

`library/parts/<maker>-<order-number>.md`: lowercase, spaces and slashes as `-`. A fictional maker
`Acme` with order number `AB 12/3` is `acme-ab-12-3.md`. Start from [`_template.md`](_template.md).

Title `# <Maker> <order number>`, then one table:

| Field | Value | Source |
|---|---|---|

## Fields

In this order. Only Maker and Order number are required; leave out a row that has no sourced
value. Values are a number plus unit, as in the Example column.

| Field | Unit | Example | Meaning |
|---|---|---|---|
| Maker | | `Acme` | Manufacturer, as on the label |
| Order number | | `AB 12/3` | Maker's order number, exactly as on the label or datasheet |
| Name | | `24 V DC power supply` | What the part is |
| Width (mm) | mm | `45 mm` | Front view, along the rail |
| Height (mm) | mm | `90 mm` | Front view, across the rail |
| Depth (mm) | mm | `110 mm` | From the mounting plate out |
| Mounting | | `TS35` | How it is fixed: rail type, or screw mounting |
| Power loss (W) | W | `14 W` | Heat given off at rated load |
| Datasheet | | URL | Maker's datasheet |

Enclosures add:

| Field | Unit | Example | Meaning |
|---|---|---|---|
| Plate width (mm) | mm | `500 mm` | Usable width of the mounting plate |
| Plate height (mm) | mm | `700 mm` | Usable height of the mounting plate |
| Max power loss (W) | W | `60 W` | What the enclosure can dissipate at its rated ambient, per the maker's data |

## Sources

A value without a source is not written. Source says where the value was read: a datasheet page
(`datasheet p. 4`) or a label photo in a machine's `sources/`, linked. For the Datasheet row it
says where the link was found (`maker's product page`). Never estimate a value from a similar
part; an unknown stays out of the file, and the spec or the tool treats it as `?`.

## Adding a part

A part file is added the first time a machine uses the part, from its datasheet. Later machines
link to the same file. A value changes only on evidence, like any spec value, and the commit names
it.
