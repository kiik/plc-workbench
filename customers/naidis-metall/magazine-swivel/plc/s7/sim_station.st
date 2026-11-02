(* Sim only, in place of OB1 of Main.scl: PROGRAM Station calls the S7 function block with the
   sim target's globals, so targets/sim.st, the plant model and tests/ run unchanged against the
   SCL port (target sim-s7). *)

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
        LNK_NextReady : BOOL;
        PNL_StartLamp : BOOL;
        PNL_ResetLamp : BOOL;
        PNL_LampQ1 : BOOL;
        PNL_LampQ2 : BOOL;
        MAG_CylRetract : BOOL;
        GRP_Grip : BOOL;
        GRP_Release : BOOL;
        SWV_ToPickup : BOOL;
        SWV_ToDropdown : BOOL;
        StepNo : INT;
    END_VAR
    VAR
        Fb : MagazineSwivel;
    END_VAR

    Fb(PNL_StartButton := PNL_StartButton, PNL_StopReleased := PNL_StopReleased,
       PNL_Manual := PNL_Manual, PNL_ResetButton := PNL_ResetButton, PNL_EStopOk := PNL_EStopOk,
       MAG_CylExtended := MAG_CylExtended, MAG_CylRetracted := MAG_CylRetracted,
       GRP_PartGripped := GRP_PartGripped, SWV_AtPickup := SWV_AtPickup,
       SWV_AtDropdown := SWV_AtDropdown, MAG_PickupOccupied := MAG_PickupOccupied,
       LNK_NextReady := LNK_NextReady);
    PNL_StartLamp := Fb.PNL_StartLamp;
    PNL_ResetLamp := Fb.PNL_ResetLamp;
    PNL_LampQ1 := Fb.PNL_LampQ1;
    PNL_LampQ2 := Fb.PNL_LampQ2;
    MAG_CylRetract := Fb.MAG_CylRetract;
    GRP_Grip := Fb.GRP_Grip;
    GRP_Release := Fb.GRP_Release;
    SWV_ToPickup := Fb.SWV_ToPickup;
    SWV_ToDropdown := Fb.SWV_ToDropdown;
    StepNo := Fb.StepNo;
END_PROGRAM
