from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

def read_variables():
    # Replace 'PLC3_IP_ADDRESS' with your actual PLC3 IP address or 'localhost' if running locally
    client = ModbusTcpClient('10.120.39.38', port=502)

    try:
        # Open the connection
        connection = client.connect()
        if not connection:
            print("Failed to connect to Modbus server.")
            return

        # Open the output file in write mode
        with open('plc3_trace_output.txt', 'w') as f:
            print("Starting to collect traces for PLC3. Press Ctrl+C to stop.")
            while True:
                timestamp = time.time()

                # Read analog inputs (%IW0 to %IW4)
                iw_result = client.read_input_registers(address=0, count=5, unit=1)
                if not iw_result.isError():
                    color_green = iw_result.registers[0]   # %IW0
                    color_blue = iw_result.registers[1]    # %IW1
                    color_red = iw_result.registers[2]     # %IW2
                    range_sensor = iw_result.registers[3]  # %IW3
                    flow_sensor = iw_result.registers[4]   # %IW4
                else:
                    color_green = 0
                    color_blue = 0
                    color_red = 0
                    range_sensor = 0
                    flow_sensor = 0
                    print("Error reading input registers")

                # Read digital inputs (%IX0.0 and %IX0.1)
                ix_result = client.read_discrete_inputs(address=0, count=2, unit=1)
                if not ix_result.isError():
                    treatment_complete = int(ix_result.bits[0])  # %IX0.0
                    underflow_t2 = int(ix_result.bits[1])        # %IX0.1
                else:
                    treatment_complete = 0
                    underflow_t2 = 0
                    print("Error reading discrete inputs")

                # Read digital outputs (%QX0.6 and %QX1.0)
                # %QX0.6 at address 6, %QX1.0 at address 8
                qx_result = client.read_coils(address=6, count=1, unit=1)
                qx_result2 = client.read_coils(address=8, count=1, unit=1)
                if not qx_result.isError() and not qx_result2.isError():
                    pump_state = int(qx_result.bits[0])    # %QX0.6
                    valve_state = int(qx_result2.bits[0])  # %QX1.0
                else:
                    pump_state = 0
                    valve_state = 0
                    print("Error reading coils")

                # Write the data to the file in CSV format
                # Columns: timestamp, color_red, color_green, color_blue, range_sensor, flow_sensor,
                # treatment_complete, underflow_t2, pump_state, valve_state
                f.write(f"{timestamp},{color_red},{color_green},{color_blue},{range_sensor},{flow_sensor},"
                        f"{treatment_complete},{underflow_t2},{pump_state},{valve_state}\n")
                f.flush()  # Ensure data is written to the file immediately

                # Wait before the next read (adjust the interval as needed)
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Trace collection stopped by user.")

    except ModbusException as e:
        print(f"Modbus exception occurred: {e}")

    finally:
        # Close the connection
        client.close()
        print("Modbus connection closed.")

if __name__ == "__main__":
    read_variables()

