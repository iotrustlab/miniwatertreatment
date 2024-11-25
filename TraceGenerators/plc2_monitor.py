from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

def read_variables():
    # Replace 'PLC2_IP_ADDRESS' with your actual PLC2 IP address or 'localhost' if running locally
    client = ModbusTcpClient('10.120.39.1', port=502)

    try:
        # Open the connection
        connection = client.connect()
        if not connection:
            print("Failed to connect to Modbus server.")
            return

        # Open the output file in write mode
        with open('plc2_trace_output.txt', 'w') as f:
            print("Starting to collect traces for PLC2. Press Ctrl+C to stop.")
            while True:
                timestamp = time.time()

                # Read analog inputs (%IW0 to %IW3)
                iw_result = client.read_input_registers(address=0, count=4, unit=1)
                if not iw_result.isError():
                    color_red = iw_result.registers[0]
                    color_green = iw_result.registers[1]
                    color_blue = iw_result.registers[2]
                    range_sensor = iw_result.registers[3]
                else:
                    color_red = 0
                    color_green = 0
                    color_blue = 0
                    range_sensor = 0
                    print("Error reading input registers")

                # Read digital outputs (%QX1.0 to %QX1.2)
                qx_result = client.read_coils(address=8, count=3, unit=1)  # Starting at address 8 for %QX1.x
                if not qx_result.isError():
                    valve_state = int(qx_result.bits[0])         # %QX1.0
                    doser_yellow_state = int(qx_result.bits[1])  # %QX1.1
                    doser_blue_state = int(qx_result.bits[2])    # %QX1.2
                else:
                    valve_state = 0
                    doser_yellow_state = 0
                    doser_blue_state = 0
                    print("Error reading coils")

                # Write the data to the file in CSV format
                # Columns: timestamp, color_red, color_green, color_blue, range_sensor, valve_state, doser_yellow_state, doser_blue_state
                f.write(f"{timestamp},{color_red},{color_green},{color_blue},{range_sensor},{valve_state},{doser_yellow_state},{doser_blue_state}\n")
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

