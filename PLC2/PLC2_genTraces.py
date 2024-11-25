# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import time
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

#ip = sys.argv[1]
#duration = int(sys.argv[2])  # Duration in seconds for which the traces will be generated
ip = "10.120.39.1"
duration = 60
sample_time = 0.5

client = ModbusClient(ip, port=502)
client.connect()

with open("PLC2_traces_v1.txt", "w") as f:
    start_time = time.time()
    while time.time() - start_time < duration:
        #input_coils_results = client.read_discrete_inputs(0,2)

        # treatmentComplete (QX0.0), underFlowt2 (QX0.1)
        treatment_and_underFlow = client.read_coils(0,2).bits[:2]
        doser_and_valve = client.read_coils(8,3).bits[:3]
        # Combine results into a new list
        output_coils_results = treatment_and_underFlow + doser_and_valve
        # RGB Sensor (IW0-IW2), RangeSensor (IW3) 
        input_regiser_results = client.read_input_registers(0,4)
        # stage (QW0), desiredDistanceFill (OW1), desiredDistanceMin (QW2)
        holding_results = client.read_holding_registers(0,3)

        #input_coils_bits = [int(bit) for bit in input_coils_results.bits[:2]]
        output_coils_bits = [int(bit) for bit in output_coils_results]
        elapsed_time = time.time() - start_time
        #f.write("DIC: " + str(elapsed_time) + "," + ",".join(map(str,  input_coils_bits)) + "\n")
        f.write("DOC: " + str(elapsed_time) + "," + ",".join(map(str, output_coils_bits)) + "\n")
        f.write("IR:  " + str(elapsed_time) + "," + ",".join(map(str, input_regiser_results.registers)) + "\n")
        f.write("HR:  " + str(elapsed_time) + "," + ",".join(map(str, holding_results.registers)) + "\n")
        time.sleep(sample_time)  