# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import psm
import time
#from pymodbus.client import ModbusTcpClient as ModbusClient
#from pymodbus.exceptions import ConnectionException

psm.start()
target = sys.argv[1]
value = sys.argv [2]
duration = [int](sys.argv[3])

try:
    start_time = time.time()
    while time.time() - start_time < duration:
        psm.set_var(target, value)
except KeyboardInterrupt:
    # If Ctrl+C is pressed, clean up the GPIO settings
    print("Stopping attack ")
finally:
    print("Attack complete")