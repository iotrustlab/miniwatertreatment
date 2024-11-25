PROGRAM plc3
  VAR
    RangeSensor AT %IW3 : INT;
    FlowSensor AT %IW4 : INT;
    Pump AT %QX0.6 : BOOL := False;
    Valve AT %QX1.0 : BOOL := False;
    treatmentComplete AT %IX0.0 : BOOL := False;
    UnderFlowT2 AT %IX0.1 : BOOL;
    maxWaterLevel AT %MW5 : INT := 4;
  END_VAR

  if NOT UnderFlowT2 AND RangeSensor > maxWaterLevel AND treatmentComplete THEN
    Pump := True;
    Valve := True;
  ELSE
    Pump := False;
    Valve := False;
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : plc3;
  END_RESOURCE
END_CONFIGURATION
