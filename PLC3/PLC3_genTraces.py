# generate_traces_with_timestamp.py
#!/usr/bin/env python3

import sys
import time
from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException

#ip = sys.argv[1]
#duration = int(sys.argv[2])  # Duration in seconds for which the traces will be generated
ip = "10.120.39.38"
duration = 60
sample_time = 0.5

client = ModbusClient(ip, port=502)
client.connect()

with open("PLC3_traces_v1.txt", "w") as f:
    start_time = time.time()
    while time.time() - start_time < duration:
        # treatmentComplete (IX0.0), UnderFlowT2 (IX0.1)
        input_coils_results = client.read_discrete_inputs(0,2)
        # Pump (QX0.6) 
        pump_state = client.read_coils(6,1).bits[0]
        #print(pump_state)
        # Valve (OX1.0)
        valve_state = client.read_coils(8, 1).bits[0]
        #print(valve_state)
        # Combine results into a new list
        output_coils_results = {pump_state, valve_state}
        # RangeSensor (IW3), FlowSensor (IW4)
        input_regiser_results = client.read_input_registers(3,2)
        # maxWaterLevel (MW5)
        holding_results = client.read_holding_registers(1029,1)

   

        input_coils_bits = [int(bit) for bit in input_coils_results.bits[:2]]
        output_coils_bits = [int(bit) for bit in output_coils_results]
        elapsed_time = time.time() - start_time
        print(len(input_coils_bits))
        f.write("DIC: " + str(elapsed_time) + "," + ",".join(map(str,  input_coils_bits)) + "\n")
        f.write("DOC: " + str(elapsed_time) + "," + ",".join(map(str, output_coils_bits)) + "\n")
        f.write("IR:  " + str(elapsed_time) + "," + ",".join(map(str, input_regiser_results.registers)) + "\n")
        f.write("HR:  " + str(elapsed_time) + "," + ",".join(map(str, holding_results.registers)) + "\n")
        time.sleep(sample_time)  