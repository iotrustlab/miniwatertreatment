import sys
import time
import json
import os
from datetime import datetime
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

ip = "10.120.39.1"
duration = int(sys.argv[1])
file_addition = sys.argv[2]
sample_time = 0.5

try:
    client = ModbusClient(ip, port=502)
    client.connect()

    path = "C:\\Users\\tardi\\OneDrive\\Documents\\Visual Studio Code Repos\\Python\\CPSWaterTestBench\\PLC2\\Traces"
    filename = os.path.join(path, f"{datetime.now().strftime("%Y-%m-%d")}_PLC2_traces_{file_addition}.json")  # Adjust filename if needed
    with open(filename, "w") as f:
        try:
            start_time = time.time()
            data = []  # List to store all trace data points
            while time.time() - start_time < duration:
                # Read Modbus data (same logic as before)
                input_coils_results = []
                treatment_and_underFlow = client.read_coils(0, 2).bits[:2]
                doser_and_valve = client.read_coils(8, 3).bits[:3]
                output_coils_results = treatment_and_underFlow + doser_and_valve
                input_regiser_results = client.read_input_registers(0, 4)
                holding_results = client.read_holding_registers(0, 3)

                # Check valve state
                if client.read_coils(8,1).bits[0] == 1:
                    processNum = 1
                # Check treatmentCompleted State
                elif client.read_coils(0,1).bits[0] == 1:
                    processNum = 3
                # Treatment still inprogress
                else:
                    processNum = 2 

                # Create a dictionary for each data point
                data_point = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # Include milliseconds
                    "Process" : processNum,
                    "DIC": input_coils_results,
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

