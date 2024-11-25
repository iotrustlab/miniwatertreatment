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


PROGRAM plc2
  VAR
    ColorSensor_RED : INT;
    ColorSensor_GREEN : INT;
    ColorSensor_BLUE : INT;
    RangeSensor : INT;
    Doser_YELLOW : BOOL := FALSE;
    Doser_BLUE : BOOL := FALSE;
  END_VAR
  VAR
    settleTime : TIME;
    doseTime : TIME;
  END_VAR
  VAR
    treatmentComplete : BOOL := FALSE;
    UnderFlowt2 : BOOL;
    stage : INT := 0;
    desiredDistanceFill : INT := 7;
    desiredDistanceMin : INT := 13;
  END_VAR
  VAR
    minBlue : INT := 20;
    doserYellowTimer : TON;
    doserBlueTimer : TON;
    settleTimer : TON;
    settleEN : BOOL := FALSE;
  END_VAR
  VAR
    Valve : BOOL := FALSE;
  END_VAR

  (*Workaround to distance measure bug*)
  desiredDistanceFill := 10;
  minBlue := 20;
  doseTime := T#3000ms;
  settleTime := T#8000ms;

  doserYellowTimer(IN:=Doser_YELLOW, PT:=doseTime);
  doserBlueTimer(IN:=Doser_BLUE,PT:=doseTime);
  settleTimer(IN:=settleEN, PT:=settleTime);

  CASE stage OF
      0:  (*Filling stage: it will fill up to a certain amount that corresponds to a certain distance*)
      
          IF RangeSensor > desiredDistanceFill THEN
            Valve := TRUE;
          ELSE
            Valve := FALSE;
            stage := 1;
          END_IF;
          
     1:  (*Treatment stage*)
          IF ColorSensor_BLUE < minBlue THEN (*Ensure minimum blue value is inserted*)
            stage := 3;
            Doser_BLUE := TRUE;
            
          (*ELSIF ColorSensor_BLUE > ColorSensor_RED  THEN (*Ensure red quantity is > blue *)
          ELSIF ColorSensor_BLUE > ColorSensor_GREEN THEN (*Ensure green quantity is > blue *)
            
              stage := 2;
              Doser_YELLOW := TRUE;
          
          ELSE  (*Treatment complete*)
            
            stage := 5;
            
          END_IF;
          
      2:  (*Yellow Dosing Stage*)
      
          IF doserYellowTimer.Q THEN
            Doser_YELLOW := FALSE;
            stage := 4;
            settleEN := True;
            (*settleTimer(IN:= True, PT:= settleTime); (*let the dose settle*)
          END_IF;
          
      3: (* Blue Dosing Stage*)
      
          IF doserBlueTimer.Q THEN
            Doser_BLUE := FALSE;
            stage := 4;
            settleEN := True;
          END_IF;
          
      4: (*Settling Stage for Dosage*)
      
          IF settleTimer.Q THEN
            stage := 1;
            settleEN := False;
          END_IF;
      
      5: (*Treatment Complete*)
        stage:=5;
        treatmentComplete := TRUE;
        IF RangeSensor < desiredDistanceMin THEN
          UnderFlowt2 := FALSE;
        ELSE
          UnderFlowt2 := TRUE;
        END_IF;      
        
  END_CASE;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : plc2;
  END_RESOURCE
END_CONFIGURATION
