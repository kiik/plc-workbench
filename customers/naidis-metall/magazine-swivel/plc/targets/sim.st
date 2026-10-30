(* Simulation target: OpenPLC runtime in Docker, PlantSim in place of the station.
   Everything is on coils and holding registers so a Modbus client can read and write it.
     coils %QX0.x  panel lamps        (as hw target)
     coils %QX1.x  valve coils        (as hw target)
     coils %QX2.x  sensors, written by PlantSim; bit = XMA2 terminal I<n>
     coils %QX3.x  panel buttons, written by the operator; bit = PNL2 terminal O<n>
     coils %QX4.x  fault injection
     holding %QW0..3  step number, parts in magazine (writable), delivered, lost *)

CONFIGURATION Config0
    VAR_GLOBAL
        PNL_StartLamp AT %QX0.0 : BOOL;
        PNL_ResetLamp AT %QX0.1 : BOOL;
        PNL_LampQ1 AT %QX0.2 : BOOL;
        PNL_LampQ2 AT %QX0.3 : BOOL;
        MAG_CylRetract AT %QX1.0 : BOOL;
        GRP_Grip AT %QX1.1 : BOOL;
        GRP_Release AT %QX1.2 : BOOL;
        SWV_ToPickup AT %QX1.3 : BOOL;
        SWV_ToDropdown AT %QX1.4 : BOOL;
        MAG_CylExtended AT %QX2.1 : BOOL;
        MAG_CylRetracted AT %QX2.2 : BOOL;
        GRP_PartGripped AT %QX2.3 : BOOL;
        SWV_AtPickup AT %QX2.4 : BOOL;
        SWV_AtDropdown AT %QX2.5 : BOOL;
        MAG_PickupOccupied AT %QX2.6 : BOOL;
        PNL_StartButton AT %QX3.0 : BOOL;
        PNL_StopReleased AT %QX3.1 : BOOL := TRUE;
        PNL_Manual AT %QX3.2 : BOOL;
        PNL_ResetButton AT %QX3.3 : BOOL;
        PNL_EStopOk AT %QX3.4 : BOOL := TRUE;   (* hw address unknown, spec 0S5 *)
        SIM_VacuumFault AT %QX4.0 : BOOL;
        SIM_SwivelJam AT %QX4.1 : BOOL;
        StepNo AT %QW0 : INT;
        SIM_PartsInMagazine AT %QW1 : INT := 5;
        SIM_PartsDelivered AT %QW2 : INT;
        SIM_PartsLost AT %QW3 : INT;
    END_VAR

    RESOURCE Res0 ON PLC
        TASK Main(INTERVAL := T#10MS, PRIORITY := 0);
        PROGRAM Plant WITH Main : PlantSim;
        PROGRAM Station0 WITH Main : Station;
    END_RESOURCE
END_CONFIGURATION
