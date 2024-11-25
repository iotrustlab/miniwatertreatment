from pymodbus.client.sync import ModbusTcpClient
import time

def read_variables():
    # Create a Modbus TCP client to connect to OpenPLC
    client = ModbusTcpClient('10.120.39.75', port=502)  # Replace 'localhost' with your PLC IP if different

    try:
        # Open the connection
        client.connect()

        # Open the output file in write mode
        with open('trace_output.txt', 'w') as f:
            print("Starting to collect traces. Press Ctrl+C to stop.")
            while True:
                timestamp = time.time()

                # Read analog inputs (%IW0 and %IW1)
                iw_result = client.read_input_registers(address=0, count=2, unit=1)
                if not iw_result.isError():
                    flow_sensor = iw_result.registers[0]
                    range_sensor = iw_result.registers[1]
                else:
                    flow_sensor = 0
                    range_sensor = 0
                    print("Error reading input registers")

                # Read digital output (%QX0.0)
                qx_result = client.read_coils(address=0, count=1, unit=1)
                if not qx_result.isError():
                    pump_state = int(qx_result.bits[0])  # Convert boolean to integer (0 or 1)
                else:
                    pump_state = 0
                    print("Error reading coils")

                # Write the data to the file in CSV format
                # Columns: timestamp, flow_sensor, range_sensor, pump_state
                f.write(f"{timestamp},{flow_sensor},{range_sensor},{pump_state}\n")
                f.flush()  # Ensure data is written to the file immediately

                # Wait before the next read (adjust the interval as needed)
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Trace collection stopped by user.")

    finally:
        # Close the connection
        client.close()
        print("Modbus connection closed.")

if __name__ == "__main__":
    read_variables()

