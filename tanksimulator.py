from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder
import time
import random

# Connect to OpenPLC
client = ModbusTcpClient('localhost', port=502)  # Adjust the IP and port as needed

# Constants
TANK_VOLUME_ML = 900  # (32floz ~ 946mL) # ~72s to fill @ 45000/3600=12.5mL/sec rate (not incl. dosing)
DOSE_VOLUME_ML = 5  # Adjust the dose volume as needed

# Mapping based on https://autonomylogic.com/docs/2-5-modbus-addressing/
# may change based on hardware target
# Actuator mapping
ACT = {
        "red_doser": 6, # QX0.6
        "blue_doser": 7, # QX0.7
        "pump": 4, # QX0.4
}
# Sensor mapping
SENS = {
        "water_level": -1,
        "red_RGB": 0,   # IW0 Program assumes RGB are sequential
        "green_RGB": 1, # IW1
        "blue_RGB": 2,  # IW2
        "range_sensor": 3 # IW3 

}

# Initial state
water_volume_ml = 0
range_sensor = 100 # 100% range = empty container, min is 94% full (range sense = 6)
red_ml = 0
blue_ml = 0
red_concentration = 0
blue_concentration = 0
fill_rate_mlph = 45000  # Assuming an average fill rate of 45 Liters per Hour
step = 0

try:
    while True:
        # Simulate the filling of the tank
        step += 1
        range_sensor = 100*(1 - water_volume_ml/TANK_VOLUME_ML)
        pump_result = client.read_coils(ACT['pump'])
        print(f"{pump_result=}", f"{pump_result.bits=}")
        if not pump_result.isError() and pump_result.bits[0]: # pump is on TODO: read pump var
            water_volume_ml += fill_rate_mlph / 3600  # Increment the water volume (convert GPH to GPM)

        # Read the state of the dosers from OpenPLC
        #response = client.read_holding_registers(4, 2)  # Assuming addresses 4 and 5 for the red and blue dosers
        #response = client.read_holding_registers(ACT["red_doser"], 2) # also gets blue doser in this case
        response = client.read_coils(ACT["red_doser"], 2) # also gets blue doser in this case
        print(response.bits)
        if not response.isError():
            red_dose, blue_dose = response.bits[0], response.bits[1]
            ## not sure if this dosing logic is correct
            #if red_dose: #    # Simulate the dosing of red color #    red_concentration += DOSE_VOLUME_ML / water_volume_ml
            #if blue_dose:
            #    # Simulate the dosing of blue color
            #    blue_concentration += DOSE_VOLUME_ML / water_volume_ml
            if red_dose:
                # Simulate the dosing of red color
                red_ml += DOSE_VOLUME_ML
                water_volume_ml += DOSE_VOLUME_ML # accounting for dose volume
            if blue_dose:
                # Simulate the dosing of blue color
                blue_ml += DOSE_VOLUME_ML
                water_volume_ml += DOSE_VOLUME_ML # accounting for dose volume

            if water_volume_ml > TANK_VOLUME_ML:
                # assuming uniform mixing (semi-realistic overflow concentration losses)
                overflow = water_volume_ml - TANK_VOLUME_ML
                red_ml -= .5 * overflow * red_concentration
                blue_ml -= .5 * overflow * blue_concentration
                water_volume_ml = TANK_VOLUME_ML  # Cap the water volume at the tank capacity

            if water_volume_ml > 0:
                red_concentration = red_ml / water_volume_ml
                blue_concentration = blue_ml / water_volume_ml

            # Write the simulated sensor readings to OpenPLC
            client.write_registers(SENS["red_RGB"], [int(red_concentration*255), 0, int(blue_concentration*255)])
            client.write_registers(SENS["range_sensor"],int(range_sensor*100))
            #builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            #builder.add_32bit_float(range_sensor)
            #payload = builder.build()
            #payload = client.convert_to_registers(range_sensor, float)
            #print(payload)
            #client.write_register(SENS["range_sensor"], range_sensor)
            #client.write_registers(SENS["range_sensor"], payload, skip_encode=True)
            #@client.write_register(0, int(water_volume_ml))  # Assuming address 0 for the water volume sensor
            #@client.write_registers(1, [int(red_concentration * 255), 0, int(blue_concentration * 255)])  # Assuming addresses 1, 2, and 3 for the RGB sensor

            print(f'Water Vol: {water_volume_ml:.2f} ml (range={range_sensor:.2f}), Red Conc: {red_concentration:.2f}, Blue Conc: {blue_concentration:.2f}, ([{int(red_dose)},{int(blue_dose)}],t={step},r={red_ml:.2f},b={blue_ml:.2f})')
        else:
            print(f'Error reading from OpenPLC: {response}')

        time.sleep(1)  # Adjust the sleep time as needed

except KeyboardInterrupt:
    pass  # Exit the loop on Ctrl-C

client.close()
