"""Tests for cabinet.py against the fictional fixtures in fixtures/.

Run: python3 -m unittest discover -s tools/cabinet/tests
"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import cabinet  # noqa: E402

FIXTURES = HERE / "fixtures"
SPEC = FIXTURES / "test.electrical.md"
UNKNOWNS = FIXTURES / "unknowns.electrical.md"
SVG = "{http://www.w3.org/2000/svg}"


def run(*argv):
    """Run the CLI; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cabinet.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def enclosure(model, location):
    return next(e for e in model["enclosures"] if e["location"] == location)


def row(e, number):
    return next(r for r in e["rows"] if r["row"] == str(number))


class Markdown(unittest.TestCase):
    TEXT = "\n".join([
        "# T", "## 2. Devices", "text",
        "| Part | Designation |", "|---|:-:|", "| [a](x.md) | `+A-B1` |", "| ? | `+A-B2` |",
        "### Sub", "| Other |", "|---|", "| 1 |",
        "## 3. Next", "| Designation | Part |", "|---|---|", "| `+Z-Z1` | ? |"])

    def test_section_by_heading_text_not_number(self):
        lines = cabinet.section(self.TEXT, "Devices")
        self.assertIn("text", lines)
        self.assertIn("| Other |", lines)            # subsections belong to the section
        self.assertNotIn("| `+Z-Z1` | ? |", lines)
        self.assertIsNone(cabinet.section(self.TEXT, "Layout"))

    def test_table_by_header_not_position(self):
        rows = cabinet.table_with(cabinet.section(self.TEXT, "Devices"), "designation", "part")
        self.assertEqual([cabinet.plain(r["designation"]) for r in rows], ["+A-B1", "+A-B2"])
        self.assertEqual(rows[0]["part"], "[a](x.md)")

    def test_part_link(self):
        self.assertEqual(cabinet.part_link("[a](parts/x.md)", Path("/s")), Path("/s/parts/x.md"))
        self.assertIsNone(cabinet.part_link("?", Path("/s")))
        self.assertIsNone(cabinet.part_link("? (spec ?1)", Path("/s")))


class Parts(unittest.TestCase):
    def test_values_with_units(self):
        warnings = []
        part = cabinet.read_part(FIXTURES / "parts" / "testco-tc-box-300.md", warnings)
        self.assertEqual(cabinet.part_quantity(part, "plate width", "mm", "x", warnings), 300)
        self.assertEqual(cabinet.part_quantity(part, "max power loss", "W", "x", warnings), 40)
        self.assertIsNone(cabinet.part_quantity(part, "width", "mm", "x", warnings))
        self.assertEqual(warnings, [])

    def test_value_without_source_is_unknown(self):
        warnings = []
        part = cabinet.read_part(FIXTURES / "parts" / "testco-tc-term-5.md", warnings)
        self.assertIsNone(cabinet.part_quantity(part, "power loss", "W", "x", warnings))
        self.assertIn("no source", warnings[0])

    def test_missing_part_file_warns(self):
        warnings = []
        self.assertIsNone(cabinet.read_part(FIXTURES / "parts" / "missing.md", warnings))
        self.assertEqual(len(warnings), 1)


class Check(unittest.TestCase):
    def setUp(self):
        self.model = cabinet.analyse(SPEC)
        self.cab1 = enclosure(self.model, "+CAB1")
        self.cab2 = enclosure(self.model, "+CAB2")

    def test_known_enclosure(self):
        self.assertEqual(self.cab1["plate"], {"width": 300, "width_known": True,
                                              "height": 400, "height_known": True})
        self.assertEqual(self.cab1["power"]["limit"], 40)

    def test_rows_in_order(self):
        self.assertEqual([(r["row"], r["kind"]) for r in self.cab1["rows"]],
                         [("1", "duct"), ("2", "rail"), ("3", "duct"), ("4", "rail"),
                          ("5", "duct")])
        self.assertEqual([r["y"] for r in self.cab1["rows"]], [0, 40, 140, 200, 280])

    def test_rail_with_known_and_unknown_parts(self):
        rail = row(self.cab1, 2)
        self.assertEqual([d["designation"] for d in rail["devices"]],
                         ["+CAB1-FC1", "+CAB1-TC1", "+CAB1-KE1", "+CAB1-XD1", "+CAB1-XD2"])
        self.assertEqual([d["x"] for d in rail["devices"]], [0, 18, 108, 153, 158])
        ke1 = rail["devices"][2]
        self.assertEqual((ke1["width"], ke1["width_known"]), (45, False))
        self.assertEqual(rail["fill"]["used"], 163)
        self.assertEqual(rail["fill"]["known"], 118)
        self.assertFalse(rail["fill"]["over"])
        self.assertEqual(rail["height"], 100)       # the tallest device, TC1
        self.assertEqual(rail["devices"][3]["label"], "X1")
        self.assertEqual(rail["devices"][0]["label"], "")       # `?` is no label

    def test_rail_overflow(self):
        rail = row(self.cab1, 4)
        self.assertEqual(rail["fill"]["used"], 330)
        self.assertTrue(rail["fill"]["definite"])
        self.assertTrue(rail["fill"]["all_known"])
        self.assertEqual([d["overflow"] for d in rail["devices"]], [False, False, True])
        self.assertTrue(self.cab1["overflow"])
        self.assertTrue(self.model["overflow"])

    def test_duct_with_unknown_height(self):
        duct = row(self.cab1, 3)
        self.assertEqual((duct["height"], duct["height_known"]), (60, False))
        self.assertIn("+CAB1 row 3 duct: height ?, assumed 60 mm", self.cab1["unknowns"])

    def test_stacked_height(self):
        h = self.cab1["height"]
        self.assertEqual((h["used"], h["known"], h["limit"]), (320, 260, 400))
        self.assertFalse(h["over"])
        self.assertFalse(h["all_known"])

    def test_power_loss(self):
        p = self.cab1["power"]
        self.assertEqual((p["used"], p["limit"], p["ratio"]), (26, 40, 0.65))
        self.assertFalse(p["definite"])
        self.assertFalse(p["all_known"])            # KE1 unknown, XD1/XD2 without source

    def test_unknowns_listed(self):
        self.assertTrue(any(u.startswith("+CAB1-KE1: part ?") for u in self.cab1["unknowns"]))
        self.assertIn("+CAB2: plate width ?, assumed 600 mm", self.cab2["unknowns"])
        self.assertIn("+CAB2: plate height ?, assumed 800 mm", self.cab2["unknowns"])
        self.assertIsNone(self.cab2["power"]["limit"])
        self.assertFalse(self.cab2["overflow"])

    def test_unplaced_device_in_cabinet_warns(self):
        text = SPEC.read_text().replace("`+CAB1-XD1`, `+CAB1-XD2`", "`+CAB1-XD1`")
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "t.electrical.md"
            spec.write_text(text.replace("](parts/", f"]({FIXTURES}/parts/"))
            model = cabinet.analyse(spec)
        self.assertIn("+CAB1-XD2: in +CAB1 but on no rail", model["warnings"])

    def test_exit_1_on_definite_overflow(self):
        code, out, _ = run("check", str(SPEC))
        self.assertEqual(code, 1)
        self.assertIn("OVERFLOW", out)

    def test_exit_0_on_unknowns_only(self):
        code, out, _ = run("check", str(UNKNOWNS))
        self.assertEqual(code, 0)
        self.assertIn("may overflow", out)
        model = cabinet.analyse(UNKNOWNS)
        rail = row(model["enclosures"][0], 2)
        self.assertTrue(rail["fill"]["over"])
        self.assertFalse(rail["fill"]["definite"])

    def test_json(self):
        for argv in (["--json", "check", str(SPEC)], ["check", str(SPEC), "--json"]):
            code, out, _ = run(*argv)
            self.assertEqual(code, 1)
            data = json.loads(out)
            self.assertTrue(data["overflow"])
            self.assertEqual(len(data["enclosures"]), 2)

    def test_error_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "t.electrical.md"
            spec.write_text("# T\n\n## 2. Devices\n\n| Designation | Part |\n|---|---|\n")
            code, _, err = run("--json", "check", str(spec))
        self.assertEqual(code, 2)
        self.assertIn("no Layout section", json.loads(err)["error"])


class Render(unittest.TestCase):
    def test_writes_valid_svg_per_enclosure(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run("--json", "render", str(SPEC), "-o", tmp)
            self.assertEqual(code, 0)
            written = json.loads(out)["written"]
            self.assertEqual(sorted(Path(w).name for w in written), ["CAB1.svg", "CAB2.svg"])
            roots = {Path(w).stem: ET.parse(w).getroot() for w in written}
        cab1 = roots["CAB1"]
        self.assertEqual(cab1.tag, f"{SVG}svg")
        self.assertTrue(cab1.get("viewBox").startswith("-20 -30 "))

        def rects(root, cls):
            return [r for r in root.iter(f"{SVG}rect") if r.get("class") == cls]

        self.assertEqual(len(rects(cab1, "device")), 8)
        self.assertEqual(len(rects(roots["CAB2"], "device")), 1)
        self.assertEqual(len(rects(cab1, "rail")), 2)
        self.assertEqual(len(rects(cab1, "duct")), 3)
        devices = rects(cab1, "device")
        self.assertEqual(sum(r.get("fill") == "#f28b82" for r in devices), 1)   # KF3, red
        dashed = [r for r in devices if r.get("stroke-dasharray")]
        self.assertEqual([(r.get("x"), r.get("width")) for r in dashed], [("108", "45")])
        plate2 = rects(roots["CAB2"], "plate")[0]
        self.assertEqual((plate2.get("width"), plate2.get("height")), ("600", "800"))
        self.assertTrue(plate2.get("stroke-dasharray"))
        texts = "".join(cab1.itertext())
        self.assertIn("+CAB1-KE1", texts)
        self.assertIn("X1", texts)
        self.assertIn("?", texts)

    def test_default_dir_next_to_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "t.electrical.md"
            spec.write_text(SPEC.read_text().replace("](parts/", f"]({FIXTURES}/parts/"))
            code, _, _ = run("render", str(spec))
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "build" / "cabinet" / "CAB1.svg").is_file())


if __name__ == "__main__":
    unittest.main()
