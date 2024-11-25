TYPE
  LOGLEVEL : (CRITICAL, WARNING, INFO, DEBUG) := INFO;
END_TYPE

FUNCTION_BLOCK LOGGER
  VAR_INPUT
    TRIG : BOOL;
    MSG : STRING;
    LEVEL : LOGLEVEL := INFO;
  END_VAR
  VAR
    TRIG0 : BOOL;
  END_VAR

  IF TRIG AND NOT TRIG0 THEN
  {{
   LogMessage(GetFbVar(LEVEL),(char*)GetFbVar(MSG, .body),GetFbVar(MSG, .len));
  }}
  END_IF;
  TRIG0:=TRIG;
END_FUNCTION_BLOCK


PROGRAM plc3
  VAR
    RangeSensor : INT;
    FlowSensor : INT;
    Pump : BOOL := False;
    Valve : BOOL := False;
    treatmentComplete : BOOL := False;
    UnderFlowT2 : BOOL;
    maxWaterLevel : INT := 4;
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
