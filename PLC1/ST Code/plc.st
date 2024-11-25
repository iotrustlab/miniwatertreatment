PROGRAM PLC1_Control
  VAR
    FlowSensor AT %IW0 : INT;
    RangeSensor AT %IW1 : INT;
    desiredDistanceFill AT %MW2 : INT;
    Pump AT %QX0.0 : BOOL := False;
  END_VAR

  (*Workaround to distance measure bug*)
  (*desiredDistanceFill := INT_TO_REAL(RangeSensor)/100.0;*)
  desiredDistanceFill := 10;


  IF RangeSensor < desiredDistanceFill THEN

    Pump := TRUE;

  ELSE

    Pump := FALSE;

  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : PLC1_Control;
  END_RESOURCE
END_CONFIGURATION
