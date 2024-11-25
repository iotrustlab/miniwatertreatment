# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import time
import os
import json
from datetime import datetime
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

#ip = sys.argv[1]
#duration = int(sys.argv[2])  # Duration in seconds for which the traces will be generated
ip = "10.120.39.38"
duration = int(sys.argv[1])
file_addition = sys.argv[2]
sample_time = 0.5

try:
    client = ModbusClient(ip, port=502)
    client.connect()

    path = "C:\\Users\\tardi\\OneDrive\\Documents\\Visual Studio Code Repos\\Python\\CPSWaterTestBench\\PLC3\\Traces"
    filename = os.path.join(path, f"{datetime.now().strftime("%Y-%m-%d")}_PLC3_traces_{file_addition}.json")  # Adjust filename if needed
    with open(filename, "w") as f:
        try:
            start_time = time.time()
            data = [] # List to store all trace data points
            while time.time() - start_time < duration:
                input_coils_results = client.read_discrete_inputs(0,2).bits[:2]
                pump_state = client.read_coils(6,1).bits[0]
                valve_state = client.read_coils(8, 1).bits[0]
                output_coils_results = [pump_state, valve_state]
                input_regiser_results = client.read_input_registers(3,2)
                holding_results = client.read_holding_registers(1029,1)

                processNum = 3 if input_coils_results[0] == 1 else 0

                # Create a dictionary for each data point
                data_point = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # Include milliseconds
                    "Process" : processNum,
                    "DIC": input_coils_results, # List of coil states (boolean vales)
                    "DOC": output_coils_results,  # List of coil states (boolean values)
                    "IR": input_regiser_results.registers,  # List of register values
                    "HR": holding_results.registers,  # List of register values
                }
                data.append(data_point)

                time.sleep(sample_time)

            # Write the entire data list as JSON to the file
            json.dump(data, f, indent=4)  # Indent for readability
        except KeyboardInterrupt:
            print("Collection Interrupted")
            # Write any left over data as JSON
            json.dump(data, f, indent=4)  # Indent for readability
        finally:
            client.close()
except KeyboardInterrupt:
    print("Collection interrupted before opening file")
except Exception as e:
    print(f"Unexpected error: {e}")
    