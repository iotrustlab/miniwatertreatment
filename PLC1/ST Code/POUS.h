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
// PROGRAM PLC1
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(INT,COLORSENSOR_RED)
  __DECLARE_VAR(INT,COLORSENSOR_GREEN)
  __DECLARE_VAR(INT,COLORSENSOR_BLUE)
  __DECLARE_VAR(INT,RANGESENSOR)
  __DECLARE_VAR(BOOL,PUMP)
  __DECLARE_VAR(BOOL,TREATMENTCOMPLETE)
  __DECLARE_VAR(REAL,DESIREDDISTANCEFILL)
  __DECLARE_VAR(REAL,MEASUREDDISTANCE)
  __DECLARE_VAR(BOOL,SHUTDOWN)

} PLC1;

void PLC1_init__(PLC1 *data__, BOOL retain);
// Code part
void PLC1_body__(PLC1 *data__);
#endif //__POUS_H
