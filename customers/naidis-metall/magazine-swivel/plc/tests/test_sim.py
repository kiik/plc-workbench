"""Scenario tests of the sim target against the step table in the spec, section 5.

Run with `tools/openplc/openplc.py test magazine-swivel`, which deploys the sim target to
the local runtime first. Each test starts in S0_Ready, manual, with 5 parts in the magazine.
"""

import os
import time
import unittest

import openplc

PROJECT = os.environ.get("OPENPLC_PROJECT", "magazine-swivel")
COILS = ["MAG_CylRetract", "GRP_Grip", "GRP_Release", "SWV_ToPickup", "SWV_ToDropdown"]


class Station(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.io = openplc.Io(openplc.build(PROJECT, "sim"))

    @classmethod
    def tearDownClass(cls):
        cls.io.modbus.close()

    def get(self, name):
        return self.io.read([name])[name]

    def set(self, **values):
        for name, value in values.items():
            self.io.write(name, value)

    def wait_step(self, *steps, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.get("StepNo") in steps:
                return
            time.sleep(0.02)
        self.fail(f"in step {self.get('StepNo')}, expected {steps} within {timeout} s")

    def values_seen(self, name, seconds):
        seen = set()
        end = time.time() + seconds
        while time.time() < end:
            seen.add(self.get(name))
            time.sleep(0.05)
        return seen

    def setUp(self):
        self.set(SIM_VacuumFault=0, SIM_SwivelJam=0, PNL_Manual=1, PNL_StopReleased=1,
                 PNL_EStopOk=1, PNL_StartButton=0, PNL_ResetButton=0, SIM_PartsInMagazine=5)
        self.wait_step(0, 8, 90, 99, timeout=10)
        if self.get("StepNo") in (90, 99):
            self.io.press("PNL_ResetButton")
        if self.get("StepNo") == 8:
            self.io.press("PNL_StartButton")
        self.wait_step(0, timeout=10)
        self.set(SIM_PartsDelivered=0, SIM_PartsLost=0)

    def test_manual_runs_one_cycle(self):
        self.io.press("PNL_StartButton")
        self.wait_step(3)
        self.wait_step(0)
        self.assertEqual(self.get("SIM_PartsDelivered"), 1)

    def test_held_start_runs_one_cycle(self):
        self.set(PNL_StartButton=1)
        self.wait_step(3)
        self.wait_step(0)
        time.sleep(0.5)
        self.assertEqual(self.get("StepNo"), 0)
        self.set(PNL_StartButton=0)
        self.assertEqual(self.get("SIM_PartsDelivered"), 1)

    def test_auto_runs_until_magazine_empty(self):
        self.set(PNL_Manual=0, SIM_PartsInMagazine=2)
        at_pickup = self.get("MAG_PickupOccupied")   # left there by an earlier test
        self.io.press("PNL_StartButton")
        self.wait_step(8, timeout=15)
        self.assertEqual(self.get("SIM_PartsDelivered"), 2 + at_pickup)
        self.assertEqual(self.values_seen("PNL_LampQ2", 1.5), {False, True}, "Q2 blinks")

    def test_stop_finishes_cycle(self):
        self.set(PNL_Manual=0)
        self.io.press("PNL_StartButton")
        self.wait_step(3)
        self.set(PNL_StopReleased=0)   # NC: 0 = pressed
        time.sleep(0.2)
        self.set(PNL_StopReleased=1)
        self.wait_step(0)
        self.assertEqual(self.get("SIM_PartsDelivered"), 1)

    def test_part_lost_alarms(self):
        self.io.press("PNL_StartButton")
        self.wait_step(5)
        self.set(SIM_VacuumFault=1)
        self.wait_step(99)
        self.assertEqual(self.get("SIM_PartsLost"), 1)
        coils = self.io.read(COILS)
        self.assertFalse(any(coils.values()), coils)

    def test_part_not_gripped_times_out(self):
        self.set(SIM_VacuumFault=1)
        self.io.press("PNL_StartButton")
        self.wait_step(4)
        self.wait_step(99, timeout=3.5)

    def test_swivel_jam_times_out(self):
        self.set(SIM_SwivelJam=1)
        self.io.press("PNL_StartButton")
        self.wait_step(3)
        time.sleep(2.5)
        self.assertEqual(self.get("StepNo"), 3)
        self.wait_step(99, timeout=1.5)
        self.set(SIM_SwivelJam=0)
        self.io.press("PNL_ResetButton")
        self.wait_step(0)

    def test_emergency_stop_needs_reset_and_homing(self):
        self.io.press("PNL_StartButton")
        self.wait_step(3)
        time.sleep(0.2)
        self.set(PNL_EStopOk=0)
        self.wait_step(90)
        coils = self.io.read(COILS)
        self.assertFalse(any(coils.values()), coils)
        time.sleep(0.2)
        self.assertFalse(self.get("SWV_AtDropdown") or self.get("SWV_AtPickup"),
                         "5/3 closed centre: swivel stops where it is")
        self.assertEqual(self.values_seen("PNL_LampQ1", 1.2), {True}, "Q1 steady while pressed")
        self.io.press("PNL_ResetButton")
        time.sleep(0.3)
        self.assertEqual(self.get("StepNo"), 90, "reset must not act while E-stop is pressed")
        self.set(PNL_EStopOk=1)
        self.io.press("PNL_ResetButton")
        self.wait_step(91)
        self.wait_step(0)
        self.assertTrue(self.get("SWV_AtDropdown"))


if __name__ == "__main__":
    unittest.main()
