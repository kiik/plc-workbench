(* Hardware target: OpenPLC runtime on the station PLC (model ?, spec section 2).
   Assumed until the PLC is known: PLC connection 1 (PNL2) is byte 0, PLC connection 2 (XMA2)
   is byte 1, bit = terminal number. PNL2 is labeled from the panel side: buttons on O, lamps on I. *)

CONFIGURATION Config0
    VAR_GLOBAL
        PNL_StartButton AT %IX0.0 : BOOL;     (* 0S1 PNL2.O0 *)
        PNL_StopReleased AT %IX0.1 : BOOL;    (* 0S2 PNL2.O1, NC *)
        PNL_Manual AT %IX0.2 : BOOL;          (* 0S3 PNL2.O2 *)
        PNL_ResetButton AT %IX0.3 : BOOL;     (* 0S4 PNL2.O3 *)
        PNL_EStopOk : BOOL := FALSE;          (* 0S5 address ?: stays in S90 until wired *)
        MAG_CylExtended AT %IX1.1 : BOOL;     (* 1S1 XMA2.I1 *)
        MAG_CylRetracted AT %IX1.2 : BOOL;    (* 1S2 XMA2.I2 *)
        GRP_PartGripped AT %IX1.3 : BOOL;     (* 2S1 XMA2.I3 *)
        SWV_AtPickup AT %IX1.4 : BOOL;        (* 3S1 XMA2.I4 *)
        SWV_AtDropdown AT %IX1.5 : BOOL;      (* 3S2 XMA2.I5 *)
        MAG_PickupOccupied AT %IX1.6 : BOOL;  (* 1S3 XMA2.I6 *)
        PNL_StartLamp AT %QX0.0 : BOOL;       (* 0H1 PNL2.I0 *)
        PNL_ResetLamp AT %QX0.1 : BOOL;       (* 0H2 PNL2.I1 *)
        PNL_LampQ1 AT %QX0.2 : BOOL;          (* 0H3 PNL2.I2 *)
        PNL_LampQ2 AT %QX0.3 : BOOL;          (* 0H4 PNL2.I3 *)
        MAG_CylRetract AT %QX1.0 : BOOL;      (* 1Y1A XMA2.O0 *)
        GRP_Grip AT %QX1.1 : BOOL;            (* 2Y1A XMA2.O1 *)
        GRP_Release AT %QX1.2 : BOOL;         (* 2Y1B XMA2.O2 *)
        SWV_ToPickup AT %QX1.3 : BOOL;        (* 3Y1A XMA2.O3 *)
        SWV_ToDropdown AT %QX1.4 : BOOL;      (* 3Y1B XMA2.O4 *)
        StepNo : INT;
    END_VAR

    RESOURCE Res0 ON PLC
        TASK Main(INTERVAL := T#10MS, PRIORITY := 0);
        PROGRAM Station0 WITH Main : Station;
    END_RESOURCE
END_CONFIGURATION
