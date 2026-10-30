(* Plant model of the magazine and swivel station, for the sim target only.
   Reads the valve coils and writes the sensors, once per 10 ms scan before Station.
   Positions count scans: one count per scan, so 40 counts = 400 ms of travel. *)

PROGRAM PlantSim
    VAR_EXTERNAL
        MAG_CylExtended : BOOL;
        MAG_CylRetracted : BOOL;
        GRP_PartGripped : BOOL;
        SWV_AtPickup : BOOL;
        SWV_AtDropdown : BOOL;
        MAG_PickupOccupied : BOOL;
        MAG_CylRetract : BOOL;
        GRP_Grip : BOOL;
        GRP_Release : BOOL;
        SWV_ToPickup : BOOL;
        SWV_ToDropdown : BOOL;
        SIM_PartsInMagazine : INT;
        SIM_PartsDelivered : INT;
        SIM_PartsLost : INT;
        SIM_VacuumFault : BOOL;
        SIM_SwivelJam : BOOL;
    END_VAR
    VAR CONSTANT
        MagStroke : INT := 40;    (* 0 = extended, MagStroke = retracted *)
        SwvStroke : INT := 50;    (* 0 = at dropdown, SwvStroke = at pickup *)
    END_VAR
    VAR
        MagPos : INT := 0;
        SwvPos : INT := 0;
        PartInFront : BOOL;       (* dropped from the magazine in front of the retracted cylinder *)
        PartAtPickup : BOOL;
        PartOnGripper : BOOL;
        Vacuum : BOOL;
        VacuumBuildUp : TON;
    END_VAR

    (* 1A1 magazine cylinder: 5/2 single solenoid, coil on retracts, spring extends *)
    IF MAG_CylRetract THEN
        IF MagPos < MagStroke THEN MagPos := MagPos + 1; END_IF;
    ELSIF MagPos > 0 THEN
        MagPos := MagPos - 1;
    END_IF;
    IF MagPos = MagStroke AND NOT PartInFront AND SIM_PartsInMagazine > 0 THEN
        PartInFront := TRUE;
        SIM_PartsInMagazine := SIM_PartsInMagazine - 1;
    END_IF;
    IF MagPos = 0 AND PartInFront THEN
        PartInFront := FALSE;
        PartAtPickup := TRUE;
    END_IF;

    (* 3A1 swivel: 5/3 closed centre, stops with both coils off or both on *)
    IF NOT SIM_SwivelJam THEN
        IF SWV_ToPickup AND NOT SWV_ToDropdown AND SwvPos < SwvStroke THEN
            SwvPos := SwvPos + 1;
        ELSIF SWV_ToDropdown AND NOT SWV_ToPickup AND SwvPos > 0 THEN
            SwvPos := SwvPos - 1;
        END_IF;
    END_IF;

    (* 2A1 vacuum gripper: valve keeps its last coil *)
    IF GRP_Grip AND NOT GRP_Release THEN
        Vacuum := TRUE;
    ELSIF GRP_Release AND NOT GRP_Grip THEN
        Vacuum := FALSE;
    END_IF;
    IF Vacuum AND SwvPos = SwvStroke AND PartAtPickup THEN
        PartAtPickup := FALSE;
        PartOnGripper := TRUE;
    END_IF;
    IF PartOnGripper AND (NOT Vacuum OR SIM_VacuumFault) THEN
        PartOnGripper := FALSE;
        IF SwvPos = 0 THEN
            SIM_PartsDelivered := SIM_PartsDelivered + 1;
        ELSIF SwvPos = SwvStroke THEN
            PartAtPickup := TRUE;
        ELSE
            SIM_PartsLost := SIM_PartsLost + 1;
        END_IF;
    END_IF;
    VacuumBuildUp(IN := Vacuum AND PartOnGripper, PT := T#100MS);

    MAG_CylExtended := MagPos = 0;
    MAG_CylRetracted := MagPos = MagStroke;
    MAG_PickupOccupied := PartAtPickup;
    SWV_AtDropdown := SwvPos = 0;
    SWV_AtPickup := SwvPos = SwvStroke;
    GRP_PartGripped := VacuumBuildUp.Q;
END_PROGRAM
