(* Magazine and swivel station: step sequence.
   Spec: ../spec.md, section 5.
   I/O symbols are globals declared by the target (targets/*.st). *)

TYPE
    StepT : (
        S0_Ready,
        S1_MagRetract,
        S2_MagPushOut,
        S3_SwvToPickup,
        S4_VacuumOn,
        S5_SwvToDropdown,
        S6_VacuumOff,
        S7_CycleEnd,
        S8_MagEmpty,
        S90_HomingRequired,
        S91_HomeSwivel,
        S92_HomeVacuumOff,
        S99_Alarm);
END_TYPE

PROGRAM Station
    VAR_EXTERNAL
        PNL_StartButton : BOOL;
        PNL_StopReleased : BOOL;
        PNL_Manual : BOOL;
        PNL_ResetButton : BOOL;
        PNL_EStopOk : BOOL;
        MAG_CylExtended : BOOL;
        MAG_CylRetracted : BOOL;
        GRP_PartGripped : BOOL;
        SWV_AtPickup : BOOL;
        SWV_AtDropdown : BOOL;
        MAG_PickupOccupied : BOOL;
        PNL_StartLamp : BOOL;
        PNL_ResetLamp : BOOL;
        PNL_LampQ1 : BOOL;
        PNL_LampQ2 : BOOL;
        MAG_CylRetract : BOOL;
        GRP_Grip : BOOL;
        GRP_Release : BOOL;
        SWV_ToPickup : BOOL;
        SWV_ToDropdown : BOOL;
        StepNo : INT;   (* Step as a number (S90 = 90) for HMI and simulation *)
    END_VAR
    VAR
        CurStep : StepT := S90_HomingRequired;
        LastStep : StepT := S90_HomingRequired;
        StepTimer : TON;
        StepTime : TIME;
        FirstScan : BOOL := TRUE;
        StartTrig : R_TRIG;
        ResetTrig : R_TRIG;
        StartP : BOOL;
        ResetP : BOOL;
        BlinkTimer : TON;
        Blink1Hz : BOOL;
        Home : BOOL;
        StopReq : BOOL;
    END_VAR

    StepTimer(IN := CurStep = LastStep, PT := T#24H);  (* restarts on every step change *)
    StepTime := StepTimer.ET;
    LastStep := CurStep;

    BlinkTimer(IN := NOT BlinkTimer.Q, PT := T#500MS);
    IF BlinkTimer.Q THEN Blink1Hz := NOT Blink1Hz; END_IF;

    StartTrig(CLK := PNL_StartButton);
    StartP := StartTrig.Q;
    ResetTrig(CLK := PNL_ResetButton);
    ResetP := ResetTrig.Q;

    Home := MAG_CylExtended AND SWV_AtDropdown;

    IF CurStep = S0_Ready OR CurStep = S8_MagEmpty THEN
        StopReq := FALSE;
    ELSIF NOT PNL_StopReleased THEN
        StopReq := TRUE;
    END_IF;

    IF FirstScan THEN
        IF Home THEN CurStep := S0_Ready; ELSE CurStep := S90_HomingRequired; END_IF;
    ELSIF NOT PNL_EStopOk THEN
        CurStep := S90_HomingRequired;
    ELSE
        CASE CurStep OF
        S90_HomingRequired:
            IF ResetP AND PNL_EStopOk THEN CurStep := S91_HomeSwivel; END_IF;

        S91_HomeSwivel:
            IF SWV_AtDropdown THEN CurStep := S92_HomeVacuumOff;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S92_HomeVacuumOff:
            IF StepTime >= T#50MS AND Home THEN CurStep := S0_Ready;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S0_Ready:
            IF NOT Home THEN CurStep := S90_HomingRequired;
            ELSIF StartP AND PNL_StopReleased THEN
                IF MAG_PickupOccupied THEN CurStep := S3_SwvToPickup; ELSE CurStep := S1_MagRetract; END_IF;
            END_IF;

        S1_MagRetract:
            IF MAG_CylRetracted THEN CurStep := S2_MagPushOut;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S2_MagPushOut:
            IF MAG_CylExtended THEN
                IF MAG_PickupOccupied THEN CurStep := S3_SwvToPickup; ELSE CurStep := S8_MagEmpty; END_IF;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S3_SwvToPickup:
            IF SWV_AtPickup THEN CurStep := S4_VacuumOn;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S4_VacuumOn:
            IF GRP_PartGripped THEN CurStep := S5_SwvToDropdown;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;  (* part not gripped *)

        S5_SwvToDropdown:
            IF NOT GRP_PartGripped THEN CurStep := S99_Alarm;          (* part lost *)
            ELSIF SWV_AtDropdown THEN CurStep := S6_VacuumOff;
            ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;

        S6_VacuumOff:
            IF StepTime >= T#50MS THEN CurStep := S7_CycleEnd; END_IF;

        S7_CycleEnd:
            IF StopReq OR PNL_Manual THEN CurStep := S0_Ready; ELSE CurStep := S1_MagRetract; END_IF;

        S8_MagEmpty:
            IF NOT Home THEN CurStep := S90_HomingRequired;
            ELSIF StartP AND PNL_StopReleased THEN CurStep := S1_MagRetract; END_IF;

        S99_Alarm:
            IF ResetP AND PNL_EStopOk THEN CurStep := S91_HomeSwivel; END_IF;
        END_CASE;
    END_IF;

    (* one line per output; never assigned anywhere else *)
    MAG_CylRetract := CurStep = S1_MagRetract AND SWV_AtDropdown;
    GRP_Grip := CurStep = S4_VacuumOn OR CurStep = S5_SwvToDropdown;
    GRP_Release := CurStep = S92_HomeVacuumOff OR CurStep = S6_VacuumOff;
    SWV_ToPickup := (CurStep = S3_SwvToPickup OR CurStep = S4_VacuumOn) AND MAG_CylExtended;
    SWV_ToDropdown := CurStep = S91_HomeSwivel OR CurStep = S92_HomeVacuumOff
        OR CurStep = S5_SwvToDropdown OR CurStep = S6_VacuumOff;
    PNL_StartLamp := (CurStep = S0_Ready OR CurStep = S8_MagEmpty) AND Blink1Hz
        OR CurStep = S1_MagRetract OR CurStep = S2_MagPushOut OR CurStep = S3_SwvToPickup
        OR CurStep = S4_VacuumOn OR CurStep = S5_SwvToDropdown OR CurStep = S6_VacuumOff
        OR CurStep = S7_CycleEnd;
    PNL_ResetLamp := CurStep = S90_HomingRequired AND (Blink1Hz OR NOT PNL_EStopOk)
        OR CurStep = S91_HomeSwivel OR CurStep = S92_HomeVacuumOff
        OR CurStep = S99_Alarm AND Blink1Hz;
    PNL_LampQ1 := PNL_ResetLamp;   (* same steps and modifiers as the reset lamp *)
    PNL_LampQ2 := PNL_ResetLamp OR CurStep = S8_MagEmpty AND Blink1Hz;

    CASE CurStep OF
    S0_Ready: StepNo := 0;
    S1_MagRetract: StepNo := 1;
    S2_MagPushOut: StepNo := 2;
    S3_SwvToPickup: StepNo := 3;
    S4_VacuumOn: StepNo := 4;
    S5_SwvToDropdown: StepNo := 5;
    S6_VacuumOff: StepNo := 6;
    S7_CycleEnd: StepNo := 7;
    S8_MagEmpty: StepNo := 8;
    S90_HomingRequired: StepNo := 90;
    S91_HomeSwivel: StepNo := 91;
    S92_HomeVacuumOff: StepNo := 92;
    S99_Alarm: StepNo := 99;
    END_CASE;

    FirstScan := FALSE;
END_PROGRAM
