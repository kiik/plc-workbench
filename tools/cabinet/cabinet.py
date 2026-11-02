#!/usr/bin/env python3
"""Check and draw cabinet mounting plates from a machine's electrical spec.

Standard library only. Reads the Devices and Layout sections of a <machine>.electrical.md and
the parts-library files its Part columns link to. `check` prints each rail's fill, the stacked
row height and the power loss per enclosure, text or one JSON object with --json; `render`
writes a front view SVG per enclosure. Unknown values are assumed and listed, never guessed
silently. Exit 0 ok or only unknowns, 1 a definite overflow (check), 2 an error.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Placeholders for unknown dimensions, in mm. Drawn dashed and listed as assumed.
DEVICE_WIDTH, DEVICE_HEIGHT = 45, 90
DUCT_HEIGHT = 60
PLATE_WIDTH, PLATE_HEIGHT = 600, 800
RAIL_HEIGHT = 35      # TS35 (EN 60715) rail: the least height of a rail row, also when empty
RAIL_BAR = 5          # drawn height of the rail bar
SVG_NS = "http://www.w3.org/2000/svg"


class CliError(Exception):
    pass


# ---------------------------------------------------------------- markdown

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERING = re.compile(r"^\d+(\.\d+)*\.?\s+")
SEPARATOR = re.compile(r"^:?-+:?$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def section(text, title):
    """Lines of the section whose heading reads `title`, numbering ignored; None if absent."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and NUMBERING.sub("", m.group(2)).strip().lower() == title.lower():
            level = len(m.group(1))
            body = []
            for rest in lines[i + 1:]:
                h = HEADING.match(rest)
                if h and len(h.group(1)) <= level:
                    break
                body.append(rest)
            return body
    return None


def split_row(line):
    cells = CELL_SPLIT.split(line.strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


def tables(lines):
    """Every Markdown table in `lines`: (lowercase headers, rows as {header: cell} dicts)."""
    found, block = [], []
    for line in [*lines, ""]:
        if line.lstrip().startswith("|"):
            block.append(line)
            continue
        if len(block) >= 2 and all(SEPARATOR.match(c.replace(" ", ""))
                                   for c in split_row(block[1])):
            header = [h.lower() for h in split_row(block[0])]
            rows = []
            for row in block[2:]:
                cells = split_row(row)
                cells += [""] * (len(header) - len(cells))
                rows.append(dict(zip(header, cells)))
            found.append((header, rows))
        block = []
    return found


def table_with(lines, *columns):
    """The rows of the first table whose header has all `columns` (lowercase), or None."""
    for header, rows in tables(lines):
        if all(c in header for c in columns):
            return rows
    return None


def plain(cell):
    """A cell's text without backticks and surrounding space; `?` and empty stay as they are."""
    return cell.replace("`", "").strip()


def known(cell):
    """True when a cell carries a value: not empty and not `?`."""
    return plain(cell) not in ("", "?")


# ---------------------------------------------------------------- parts library

QUANTITY = re.compile(r"^(\d+(?:[.,]\d+)?)\s*(mm|W)$")


def read_part(path, warnings):
    """A parts-library file as {field: (value, source)}, field lowercase without its unit."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        warnings.append(f"cannot read part {path}: {e.strerror}")
        return None
    rows = table_with(text.splitlines(), "field", "value", "source")
    if rows is None:
        warnings.append(f"{path}: no | Field | Value | Source | table")
        return None
    part = {}
    for row in rows:
        field = re.sub(r"\s*\(.*\)\s*$", "", plain(row["field"])).lower()
        part[field] = (plain(row["value"]), plain(row["source"]))
    title = next((HEADING.match(l).group(2) for l in text.splitlines()
                  if HEADING.match(l) and HEADING.match(l).group(1) == "#"), None)
    part["_title"] = (title or path.stem, "")
    return part


def part_quantity(part, field, unit, where, warnings):
    """A numeric part value in `unit`, or None when it is missing, `?` or has no source."""
    if not part or field not in part:
        return None
    value, source = part[field]
    if value in ("", "?"):
        return None
    if source in ("", "?"):
        warnings.append(f"{where}: {field} {value} has no source; treated as ?")
        return None
    m = QUANTITY.match(value)
    if not m or m.group(2) != unit:
        warnings.append(f"{where}: {field} {value!r} is not a number in {unit}; treated as ?")
        return None
    number = float(m.group(1).replace(",", "."))
    return int(number) if number.is_integer() else number


def part_link(cell, spec_dir):
    """The parts-library path a Part cell links to, or None for `?` or plain text."""
    m = LINK.search(cell)
    if not m or m.group(2).startswith(("http://", "https://")):
        return None
    return (spec_dir / m.group(2).split("#")[0]).resolve()


# ---------------------------------------------------------------- spec

def location_of(designation):
    m = re.search(r"\+([A-Za-z0-9.]+)", designation)
    return f"+{m.group(1)}" if m else None


def fmt(x):
    if x is None:
        return "?"
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def budget(used, known_sum, limit, limit_known, all_known):
    """A used / limit figure. Definite overflow: the known values alone exceed a known limit."""
    ratio = used / limit if limit else None
    return {"used": used, "known": known_sum, "limit": limit,
            "ratio": round(ratio, 3) if ratio is not None else None,
            "all_known": all_known and limit_known,
            "over": ratio is not None and used > limit,
            "definite": limit_known and limit is not None and known_sum > limit}


def analyse(spec_path):
    """Parse the spec and its parts into enclosures with rows, devices, placements and budgets."""
    spec_path = Path(spec_path)
    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError as e:
        raise CliError(f"cannot read {spec_path}: {e.strerror}")
    spec_dir = spec_path.resolve().parent
    warnings = []

    device_lines = section(text, "Devices")
    if device_lines is None:
        raise CliError(f"{spec_path}: no Devices section")
    device_rows = table_with(device_lines, "designation", "part")
    if device_rows is None:
        raise CliError(f"{spec_path}: Devices has no | Designation | … | Part | table")
    devices = {}
    for row in device_rows:
        designation = plain(row["designation"])
        if not designation or designation == "?":
            continue
        path = part_link(row["part"], spec_dir)
        devices[designation] = {
            "label": plain(row.get("label", "")) if known(row.get("label", "")) else "",
            "name": plain(row.get("name", "")),
            "part_path": path,
            "part": read_part(path, warnings) if path else None}

    layout = section(text, "Layout")
    if layout is None:
        raise CliError(f"{spec_path}: no Layout section")
    enclosure_rows = table_with(layout, "location", "part")
    row_rows = table_with(layout, "location", "row", "kind")
    if enclosure_rows is None:
        raise CliError(f"{spec_path}: Layout has no | Location | Part | Notes | table")
    if row_rows is None:
        raise CliError(f"{spec_path}: Layout has no "
                       "| Location | Row | Kind | Height | Contents | table")

    enclosures = {}
    for row in enclosure_rows:
        location = plain(row["location"])
        path = part_link(row["part"], spec_dir)
        enclosures[location] = {"location": location, "part_path": path,
                                "part": read_part(path, warnings) if path else None, "rows": []}
    for row in row_rows:
        location = plain(row["location"])
        if location not in enclosures:
            warnings.append(f"{location}: rows given but no Enclosures entry; part treated as ?")
            enclosures[location] = {"location": location, "part_path": None, "part": None,
                                    "rows": []}
        enclosures[location]["rows"].append(row)

    placed = set()
    result = [place(e, devices, placed, warnings) for e in enclosures.values()]
    for designation in devices:
        location = location_of(designation)
        if location in enclosures and designation not in placed:
            warnings.append(f"{designation}: in {location} but on no rail")
    return {"spec": str(spec_path), "enclosures": result, "warnings": warnings,
            "overflow": any(e["overflow"] for e in result)}


def place(enclosure, devices, placed, warnings):
    """Lay the enclosure's rows out top to bottom and its devices left to right; sum budgets."""
    location = enclosure["location"]
    part = enclosure["part"]
    unknowns = []
    if enclosure["part_path"] is None:
        unknowns.append(f"{location}: enclosure part ?")

    def plate(field, placeholder):
        value = part_quantity(part, field, "mm", location, warnings)
        if value is None:
            unknowns.append(f"{location}: {field} ?, assumed {placeholder} mm")
            return placeholder, False
        return value, True

    plate_w, plate_w_known = plate("plate width", PLATE_WIDTH)
    plate_h, plate_h_known = plate("plate height", PLATE_HEIGHT)
    max_loss = part_quantity(part, "max power loss", "W", location, warnings)
    if max_loss is None:
        unknowns.append(f"{location}: max power loss ?, power not checked")

    rows, y, y_known, all_heights_known = [], 0, 0, True
    loss, loss_all_known = 0, True
    for row in sorted(enclosure["rows"], key=lambda r: int(plain(r["row"]))
                      if plain(r["row"]).isdigit() else 0):
        number, kind = plain(row["row"]), plain(row["kind"]).lower()
        where = f"{location} row {number}"
        height_cell = plain(row.get("height", ""))
        if kind == "duct":
            height = None
            m = re.match(r"^(\d+(?:\.\d+)?)\s*(mm)?$", height_cell)
            if m:
                height = float(m.group(1))
                height = int(height) if height.is_integer() else height
            elif height_cell not in ("", "?"):
                warnings.append(f"{where}: duct height {height_cell!r} is not a number")
            h_known = height is not None
            if not h_known:
                unknowns.append(f"{where} duct: height ?, assumed {DUCT_HEIGHT} mm")
                height = DUCT_HEIGHT
            rows.append({"row": number, "kind": "duct", "y": y, "height": height,
                         "height_known": h_known})
            y += height
            y_known += height if h_known else 0
            all_heights_known &= h_known
            continue
        if kind != "rail":
            warnings.append(f"{where}: kind {kind!r} is neither rail nor duct; row ignored")
            continue
        if height_cell:
            warnings.append(f"{where}: a rail is as tall as its devices; "
                            f"height {height_cell!r} ignored")
        x, x_known, widths_known, placed_devices = 0, 0, True, []
        tallest, tallest_known, heights_known = RAIL_HEIGHT, RAIL_HEIGHT, True
        for designation in [plain(d) for d in row.get("contents", "").split(",") if plain(d)]:
            device = devices.get(designation)
            if device is None:
                warnings.append(f"{where}: {designation} is not in the device table")
                device = {"label": "", "name": "", "part_path": None, "part": None}
            if location_of(designation) not in (None, location):
                warnings.append(f"{where}: {designation} is designated for another location")
            if designation in placed:
                warnings.append(f"{designation}: placed on more than one rail")
            placed.add(designation)
            dpart = device["part"]
            width = part_quantity(dpart, "width", "mm", designation, warnings)
            height = part_quantity(dpart, "height", "mm", designation, warnings)
            power = part_quantity(dpart, "power loss", "W", designation, warnings)
            assumed = []
            if device["part_path"] is None:
                assumed.append("part ?")
            if width is None:
                assumed.append(f"width ?, assumed {DEVICE_WIDTH} mm")
            if height is None:
                assumed.append(f"height ?, assumed {DEVICE_HEIGHT} mm")
            if power is None:
                assumed.append("power loss ?, not counted")
            if assumed:
                unknowns.append(f"{designation}: " + "; ".join(assumed))
            w = width if width is not None else DEVICE_WIDTH
            h = height if height is not None else DEVICE_HEIGHT
            placed_devices.append({
                "designation": designation, "label": device["label"], "name": device["name"],
                "part": str(device["part_path"]) if device["part_path"] else None,
                "x": x, "width": w, "width_known": width is not None,
                "height": h, "height_known": height is not None,
                "power_loss": power,
                "overflow": width is not None and x + w > plate_w})
            x += w
            x_known += width or 0
            widths_known &= width is not None
            tallest = max(tallest, h)
            tallest_known = max(tallest_known, height or 0)
            heights_known &= height is not None
            if power is None:
                loss_all_known = False
            else:
                loss += power
        rows.append({"row": number, "kind": "rail", "y": y, "height": tallest,
                     "height_known": heights_known, "devices": placed_devices,
                     "fill": budget(x, x_known, plate_w, plate_w_known, widths_known)})
        y += tallest
        y_known += tallest_known
        all_heights_known &= heights_known

    stack = budget(y, y_known, plate_h, plate_h_known, all_heights_known)
    power = budget(loss, loss, max_loss, max_loss is not None, loss_all_known)
    overflow = (stack["definite"] or power["definite"]
                or any(r["fill"]["definite"] for r in rows if r["kind"] == "rail"))
    name = None
    if part:
        name = part.get("name", ("", ""))[0] or part["_title"][0]
    return {"location": location, "part": str(enclosure["part_path"]) if part else None,
            "name": name,
            "plate": {"width": plate_w, "width_known": plate_w_known,
                      "height": plate_h, "height_known": plate_h_known},
            "rows": rows, "height": stack, "power": power, "unknowns": unknowns,
            "overflow": overflow}


# ---------------------------------------------------------------- text

def verdict(b):
    if b["definite"]:
        return "OVERFLOW"
    if b["over"]:
        return "may overflow (assumed values)"
    return ""


def line(label, b, unit):
    if b["limit"] is None:
        return f"  {label:<12} {fmt(b['used']):>5} / ? {unit}"
    pct = f"{round(b['ratio'] * 100)} %"
    return f"  {label:<12} {fmt(b['used']):>5} / {fmt(b['limit'])} {unit:<3} {pct:>6}  " \
           f"{verdict(b)}".rstrip()


def report(model):
    out = []
    for e in model["enclosures"]:
        p = e["plate"]
        plate = f"plate {fmt(p['width'])}{'' if p['width_known'] else '?'} × " \
                f"{fmt(p['height'])}{'' if p['height_known'] else '?'} mm"
        out.append(f"{e['location']}  {e['name'] or 'enclosure ?'}, {plate}")
        for r in e["rows"]:
            if r["kind"] == "rail":
                out.append(line(f"row {r['row']} rail", r["fill"], "mm"))
        out.append(line("height", e["height"], "mm"))
        out.append(line("power loss", e["power"], "W"))
        if e["unknowns"]:
            out.append("  assumed:")
            out += [f"    {u}" for u in e["unknowns"]]
    if model["warnings"]:
        out.append("warnings:")
        out += [f"  {w}" for w in model["warnings"]]
    out.append("OVERFLOW" if model["overflow"] else "ok")
    return "\n".join(out)


# ---------------------------------------------------------------- svg

def el(parent, tag, text=None, **attrs):
    e = ET.SubElement(parent, tag, {k.rstrip("_").replace("_", "-"): str(v)
                                    for k, v in attrs.items()})
    if text is not None:
        e.text = text
    return e


def svg(e):
    """A front view of one enclosure's plate, 1 mm = 1 unit, as an ElementTree root."""
    p = e["plate"]
    width = max([p["width"]] + [d["x"] + d["width"] for r in e["rows"]
                                for d in r.get("devices", [])])
    height = max([p["height"]] + [r["y"] + r["height"] for r in e["rows"]])
    margin, top = 20, 30
    root = ET.Element("svg", {"xmlns": SVG_NS,
                              "viewBox": f"{-margin} {-top} {fmt(width + 2 * margin)} "
                                         f"{fmt(height + top + margin)}",
                              "width": f"{fmt(width + 2 * margin)}mm",
                              "height": f"{fmt(height + top + margin)}mm",
                              "font-family": "sans-serif"})
    el(root, "title", f"{e['location']} front view")
    defs = el(root, "defs")
    hatch = el(defs, "pattern", id="hatch", patternUnits="userSpaceOnUse", width=6, height=6,
               patternTransform="rotate(45)")
    el(hatch, "rect", width=6, height=6, fill="#e6e6e6")
    el(hatch, "line", x1=0, y1=0, x2=0, y2=6, stroke="#9a9a9a", stroke_width=1.5)
    el(root, "rect", class_="background", x=-margin, y=-top, width=fmt(width + 2 * margin),
       height=fmt(height + top + margin), fill="#ffffff")

    plate = f"plate {fmt(p['width'])}{'' if p['width_known'] else '?'} × " \
            f"{fmt(p['height'])}{'' if p['height_known'] else '?'} mm"
    el(root, "text", f"{e['location']}  {e['name'] or 'enclosure ?'}, {plate}",
       x=0, y=-12, font_size=8, fill="#222222")
    dashed = {} if p["width_known"] and p["height_known"] else {"stroke_dasharray": "8 4"}
    el(root, "rect", class_="plate", x=0, y=0, width=fmt(p["width"]), height=fmt(p["height"]),
       fill="#f5f5f0", stroke="#333333", stroke_width=1.5, **dashed)

    for r in e["rows"]:
        if r["kind"] == "duct":
            extra = {} if r["height_known"] else {"stroke_dasharray": "6 3"}
            el(root, "rect", class_="duct", x=0, y=fmt(r["y"]), width=fmt(p["width"]),
               height=fmt(r["height"]), fill="url(#hatch)", stroke="#777777", stroke_width=0.8,
               **extra)
            label = f"duct {fmt(r['height']) if r['height_known'] else '?'} mm"
            el(root, "text", label, x=4, y=fmt(r["y"] + min(r["height"], 12) - 3), font_size=4,
               fill="#444444")
            continue
        mid = r["y"] + r["height"] / 2
        el(root, "rect", class_="rail", x=0, y=fmt(mid - RAIL_BAR / 2), width=fmt(p["width"]),
           height=RAIL_BAR, fill="#a0a4a8", stroke="#6c7075", stroke_width=0.5)
        for d in r["devices"]:
            y = mid - d["height"] / 2
            unknown = not (d["width_known"] and d["height_known"])
            attrs = {"stroke_dasharray": "4 2"} if unknown else {}
            g = el(root, "g", class_="device-group")
            el(g, "title", f"{d['designation']} {d['name']}".strip())
            el(g, "rect", class_="device", x=fmt(d["x"]), y=fmt(y), width=fmt(d["width"]),
               height=fmt(d["height"]), fill="#f28b82" if d["overflow"] else "#dfe8f1",
               stroke="#c5221f" if d["overflow"] else "#2b4a6b", stroke_width=0.8, **attrs)
            lines = [d["designation"]] + ([d["label"]] if d["label"] else []) \
                + (["?"] if unknown else [])
            cx, cy = fmt(round(d["x"] + d["width"] / 2, 2)), fmt(round(mid, 2))
            vertical = d["width"] < 30 and d["height"] > d["width"]
            if vertical:        # one line along a narrow device, so it stays on the device
                lines = ["  ".join(lines)]
            room = d["height"] if vertical else d["width"]
            size = round(max(1.5, min(4.0, (room - 2) / (0.62 * max(map(len, lines))))), 2)
            turn = {"transform": f"rotate(-90 {cx} {cy})"} if vertical else {}
            text = el(g, "text", x=cx, y=cy, font_size=fmt(size), text_anchor="middle",
                      fill="#111111", **turn)
            step = round(size * 1.2, 2)
            first = round(size * 0.35 - (len(lines) - 1) / 2 * step, 2)
            for i, t in enumerate(lines):
                el(text, "tspan", t, x=cx, dy=fmt(first if i == 0 else step))
    return root


def render(model, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for e in model["enclosures"]:
        path = out_dir / f"{e['location'].lstrip('+')}.svg"
        tree = ET.ElementTree(svg(e))
        ET.indent(tree)
        tree.write(path, encoding="utf-8", xml_declaration=True)
        written.append(str(path))
    return written


# ---------------------------------------------------------------- cli

def cmd_check(a):
    model = analyse(a.spec)
    return model, report(model), 1 if model["overflow"] else 0


def cmd_render(a):
    model = analyse(a.spec)
    out_dir = Path(a.output) if a.output else Path(a.spec).resolve().parent / "build" / "cabinet"
    written = render(model, out_dir)
    text = "\n".join([*(f"wrote {w}" for w in written),
                      *(f"warning: {w}" for w in model["warnings"])])
    return {"written": written, "warnings": model["warnings"]}, text, 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cabinet", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, help):
        p = sub.add_parser(name, help=help)
        p.add_argument("spec", help="a <machine>.electrical.md")
        p.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                       help="print JSON")
        p.set_defaults(func=func)
        return p

    add("check", cmd_check, "rail fill, plate height and power loss per enclosure")
    add("render", cmd_render, "write a front view SVG per enclosure") \
        .add_argument("-o", "--output", help="directory; default build/cabinet/ next to the spec")

    a = parser.parse_args(argv)
    try:
        result, text, code = a.func(a)
    except (CliError, OSError) as e:
        print(json.dumps({"error": str(e)}) if a.json else f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(result) if a.json else text)
    return code


if __name__ == "__main__":
    sys.exit(main())
