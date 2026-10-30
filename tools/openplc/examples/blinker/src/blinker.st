(* Hello world for the OpenPLC toolchain: a lamp blinks at 1 Hz while Enable is on and
   Blinks counts its flashes. Enable and Blinks can be written over Modbus. *)

PROGRAM Blinker
    VAR_EXTERNAL
        Enable : BOOL;
        Lamp : BOOL;
        Blinks : INT;
    END_VAR
    VAR
        HalfPeriod : TON;
    END_VAR

    HalfPeriod(IN := Enable AND NOT HalfPeriod.Q, PT := T#500MS);
    IF HalfPeriod.Q THEN
        Lamp := NOT Lamp;
        IF Lamp THEN Blinks := Blinks + 1; END_IF;
    END_IF;
    IF NOT Enable THEN Lamp := FALSE; END_IF;
END_PROGRAM

CONFIGURATION Config0
    VAR_GLOBAL
        Lamp AT %QX0.0 : BOOL;
        Enable AT %QX0.1 : BOOL := TRUE;
        Blinks AT %QW0 : INT;
    END_VAR

    RESOURCE Res0 ON PLC
        TASK Main(INTERVAL := T#10MS, PRIORITY := 0);
        PROGRAM Blinker0 WITH Main : Blinker;
    END_RESOURCE
END_CONFIGURATION
