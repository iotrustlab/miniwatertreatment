#include "beremiz.h"
#ifndef __POUS_H
#define __POUS_H

#include "accessor.h"
#include "iec_std_lib.h"

__DECLARE_ENUMERATED_TYPE(LOGLEVEL,
  LOGLEVEL__CRITICAL,
  LOGLEVEL__WARNING,
  LOGLEVEL__INFO,
  LOGLEVEL__DEBUG
)
// FUNCTION_BLOCK LOGGER
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,TRIG)
  __DECLARE_VAR(STRING,MSG)
  __DECLARE_VAR(LOGLEVEL,LEVEL)

  // FB private variables - TEMP, private and located variables
  __DECLARE_VAR(BOOL,TRIG0)

} LOGGER;

void LOGGER_init__(LOGGER *data__, BOOL retain);
// Code part
void LOGGER_body__(LOGGER *data__);
// PROGRAM PLC3
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(INT,RANGESENSOR)
  __DECLARE_VAR(INT,FLOWSENSOR)
  __DECLARE_VAR(BOOL,PUMP)
  __DECLARE_VAR(BOOL,VALVE)
  __DECLARE_VAR(BOOL,TREATMENTCOMPLETE)
  __DECLARE_VAR(BOOL,UNDERFLOWT2)
  __DECLARE_VAR(INT,MAXWATERLEVEL)

} PLC3;

void PLC3_init__(PLC3 *data__, BOOL retain);
// Code part
void PLC3_body__(PLC3 *data__);
#endif //__POUS_H
