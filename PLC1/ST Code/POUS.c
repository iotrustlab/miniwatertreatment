void LOGGER_init__(LOGGER *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->TRIG,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->MSG,__STRING_LITERAL(0,""),retain)
  __INIT_VAR(data__->LEVEL,LOGLEVEL__INFO,retain)
  __INIT_VAR(data__->TRIG0,__BOOL_LITERAL(FALSE),retain)
}

// Code part
void LOGGER_body__(LOGGER *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  if ((__GET_VAR(data__->TRIG,) && !(__GET_VAR(data__->TRIG0,)))) {
    #define GetFbVar(var,...) __GET_VAR(data__->var,__VA_ARGS__)
    #define SetFbVar(var,val,...) __SET_VAR(data__->,var,__VA_ARGS__,val)

   LogMessage(GetFbVar(LEVEL),(char*)GetFbVar(MSG, .body),GetFbVar(MSG, .len));
  
    #undef GetFbVar
    #undef SetFbVar
;
  };
  __SET_VAR(data__->,TRIG0,,__GET_VAR(data__->TRIG,));

  goto __end;

__end:
  return;
} // LOGGER_body__() 





void PLC1_init__(PLC1 *data__, BOOL retain) {
  __INIT_VAR(data__->COLORSENSOR_RED,0,retain)
  __INIT_VAR(data__->COLORSENSOR_GREEN,0,retain)
  __INIT_VAR(data__->COLORSENSOR_BLUE,0,retain)
  __INIT_VAR(data__->RANGESENSOR,0,retain)
  __INIT_VAR(data__->PUMP,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->TREATMENTCOMPLETE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->DESIREDDISTANCEFILL,7.0,retain)
  __INIT_VAR(data__->MEASUREDDISTANCE,0,retain)
  __INIT_VAR(data__->SHUTDOWN,__BOOL_LITERAL(FALSE),retain)
}

// Code part
void PLC1_body__(PLC1 *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,MEASUREDDISTANCE,,(INT_TO_REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (INT)__GET_VAR(data__->RANGESENSOR,)) / 100.0));
  __SET_VAR(data__->,DESIREDDISTANCEFILL,,7.0);
  if (__GET_VAR(data__->SHUTDOWN,)) {
    __SET_VAR(data__->,PUMP,,__BOOL_LITERAL(FALSE));
  } else {
    if (__GET_VAR(data__->TREATMENTCOMPLETE,)) {
      if ((__GET_VAR(data__->MEASUREDDISTANCE,) > __GET_VAR(data__->DESIREDDISTANCEFILL,))) {
        __SET_VAR(data__->,PUMP,,__BOOL_LITERAL(TRUE));
      } else {
        __SET_VAR(data__->,PUMP,,__BOOL_LITERAL(FALSE));
        __SET_VAR(data__->,SHUTDOWN,,__BOOL_LITERAL(TRUE));
      };
    };
  };

  goto __end;

__end:
  return;
} // PLC1_body__() 





