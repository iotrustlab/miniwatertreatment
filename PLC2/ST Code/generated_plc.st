PROGRAM plc2
  VAR
    ColorSensor_RED AT %IW0 : INT;
    ColorSensor_GREEN AT %IW1 : INT;
    ColorSensor_BLUE AT %IW2 : INT;
    RangeSensor AT %IW3 : INT;
    Doser_YELLOW AT %QX1.1 : BOOL := FALSE;
    Doser_BLUE AT %QX1.2 : BOOL := FALSE;
  END_VAR
  VAR
    settleTime : TIME;
    doseTime : TIME;
  END_VAR
  VAR
    treatmentComplete AT %QX0.0 : BOOL := FALSE;
    UnderFlowt2 AT %QX0.1 : BOOL;
    stage AT %QW0 : INT := 0;
    desiredDistanceFill AT %QW1 : INT := 7;
    desiredDistanceMin AT %QW2 : INT := 13;
  END_VAR
  VAR
    minBlue : INT := 20;
    doserYellowTimer : TON;
    doserBlueTimer : TON;
    settleTimer : TON;
    settleEN : BOOL := FALSE;
  END_VAR
  VAR
    Valve AT %QX1.0 : BOOL := FALSE;
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
