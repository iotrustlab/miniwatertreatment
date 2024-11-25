from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import threading
import time

def read_plc1_variables():
    # PLC1 IP Address
    client = ModbusTcpClient('10.120.39.75', port=502)

    try:
        # Open the connection
        client.connect()

        # Open the output file in write mode
        with open('plc1_trace_output.txt', 'w') as f:
            print("Starting to collect traces for PLC1.")

            # Write the header to the file
            f.write('timestamp,flow_sensor,range_sensor,pump_state\n')

            while not stop_event.is_set():
                timestamp = time.time()

                # Read analog inputs (%IW0 and %IW1)
                iw_result = client.read_input_registers(address=0, count=2, unit=1)
                if not iw_result.isError():
                    flow_sensor = iw_result.registers[0]
                    range_sensor = iw_result.registers[1]
                else:
                    flow_sensor = 0
                    range_sensor = 0
                    print("PLC1: Error reading input registers")

                # Read digital output (%QX0.0)
                qx_result = client.read_coils(address=0, count=1, unit=1)
                if not qx_result.isError():
                    pump_state = int(qx_result.bits[0])  # Convert boolean to integer (0 or 1)
                else:
                    pump_state = 0
                    print("PLC1: Error reading coils")

                # Write the data to the file in CSV format
                f.write(f"{timestamp},{flow_sensor},{range_sensor},{pump_state}\n")
                f.flush()  # Ensure data is written to the file immediately

                # Wait before the next read
                time.sleep(0.1)

    except Exception as e:
        print(f"PLC1: Exception occurred: {e}")

    finally:
        # Close the connection
        client.close()
        print("PLC1: Modbus connection closed.")

def read_plc2_variables():
    # PLC2 IP Address
    client = ModbusTcpClient('10.120.39.1', port=502)

    try:
        # Open the connection
        client.connect()

        # Open the output file in write mode
        with open('plc2_trace_output.txt', 'w') as f:
            print("Starting to collect traces for PLC2.")

            # Write the header to the file
            f.write('timestamp,color_red,color_green,color_blue,range_sensor,valve_state,doser_yellow_state,doser_blue_state\n')

            while not stop_event.is_set():
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
                    print("PLC2: Error reading input registers")

                # Read digital outputs (%QX1.0 to %QX1.2)
                qx_result = client.read_coils(address=8, count=3, unit=1)
                if not qx_result.isError():
                    valve_state = int(qx_result.bits[0])         # %QX1.0
                    doser_yellow_state = int(qx_result.bits[1])  # %QX1.1
                    doser_blue_state = int(qx_result.bits[2])    # %QX1.2
                else:
                    valve_state = 0
                    doser_yellow_state = 0
                    doser_blue_state = 0
                    print("PLC2: Error reading coils")

                # Write the data to the file in CSV format
                f.write(f"{timestamp},{color_red},{color_green},{color_blue},{range_sensor},"
                        f"{valve_state},{doser_yellow_state},{doser_blue_state}\n")
                f.flush()  # Ensure data is written to the file immediately

                # Wait before the next read
                time.sleep(0.1)

    except Exception as e:
        print(f"PLC2: Exception occurred: {e}")

    finally:
        # Close the connection
        client.close()
        print("PLC2: Modbus connection closed.")

def read_plc3_variables():
    # PLC3 IP Address
    client = ModbusTcpClient('10.120.39.38', port=502)

    try:
        # Open the connection
        client.connect()

        # Open the output file in write mode
        with open('plc3_trace_output.txt', 'w') as f:
            print("Starting to collect traces for PLC3.")

            # Write the header to the file
            f.write('timestamp,color_red,color_green,color_blue,range_sensor,flow_sensor,treatment_complete,underflow_t2,pump_state,valve_state\n')

            while not stop_event.is_set():
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
                    print("PLC3: Error reading input registers")

                # Read digital inputs (%IX0.0 and %IX0.1)
                ix_result = client.read_discrete_inputs(address=0, count=2, unit=1)
                if not ix_result.isError():
                    treatment_complete = int(ix_result.bits[0])  # %IX0.0
                    underflow_t2 = int(ix_result.bits[1])        # %IX0.1
                else:
                    treatment_complete = 0
                    underflow_t2 = 0
                    print("PLC3: Error reading discrete inputs")

                # Read digital outputs (%QX0.6 and %QX1.0)
                qx_result = client.read_coils(address=6, count=1, unit=1)
                qx_result2 = client.read_coils(address=8, count=1, unit=1)
                if not qx_result.isError() and not qx_result2.isError():
                    pump_state = int(qx_result.bits[0])    # %QX0.6
                    valve_state = int(qx_result2.bits[0])  # %QX1.0
                else:
                    pump_state = 0
                    valve_state = 0
                    print("PLC3: Error reading coils")

                # Write the data to the file in CSV format
                f.write(f"{timestamp},{color_red},{color_green},{color_blue},{range_sensor},{flow_sensor},"
                        f"{treatment_complete},{underflow_t2},{pump_state},{valve_state}\n")
                f.flush()  # Ensure data is written to the file immediately

                # Wait before the next read
                time.sleep(0.1)

    except Exception as e:
        print(f"PLC3: Exception occurred: {e}")

    finally:
        # Close the connection
        client.close()
        print("PLC3: Modbus connection closed.")

if __name__ == "__main__":
    # Event to signal threads to stop
    stop_event = threading.Event()

    # Create threads for each PLC
    plc1_thread = threading.Thread(target=read_plc1_variables, name='PLC1_Thread')
    plc2_thread = threading.Thread(target=read_plc2_variables, name='PLC2_Thread')
    plc3_thread = threading.Thread(target=read_plc3_variables, name='PLC3_Thread')

    # Start the threads
    plc1_thread.start()
    plc2_thread.start()
    plc3_thread.start()

    print("All PLC threads started. Press Ctrl+C to stop.")

    try:
        # Keep the main thread alive to listen for KeyboardInterrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all PLC threads...")
        # Signal all threads to stop
        stop_event.set()

        # Wait for all threads to finish
        plc1_thread.join()
        plc2_thread.join()
        plc3_thread.join()

        print("All PLC threads stopped.")

