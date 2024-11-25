# Import necessary libraries
import psm
import time
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory

from pymodbus.client.sync import ModbusTcpClient
# Create a client instance
print("Creating a client instance: ")
client = ModbusTcpClient('10.120.39.1', port=502)
print("Client instance created...")

# Initialize GPIO mode
GPIO.setmode(GPIO.BCM)

# Define GPIO pins
GPIO_FlowSensor = 4           # GPIO pin 4 connected to flow sensor's (YF-S201) data
GPIO_PumpControl = 14          # GPIO pin 14 connected to pump's relay
GPIO_RangeEcho = 15            # GPIO pin 15 connected to range sensor's echo pin
GPIO_RangeTrigger = 18         # GPIO pin 18 connected to range sensor's trigger pin

# Create a PiGPIOFactory instance
pigpio_factory = PiGPIOFactory()

# Distance sensor using gpiozero
distance_sensor = DistanceSensor(echo=GPIO_RangeEcho, trigger=GPIO_RangeTrigger, pin_factory=pigpio_factory)

def update_flow():
    global pulse
    global startTime
    currentTime = time.time()
    elapsedTime = currentTime - startTime
    print(elapsedTime)
    if elapsedTime >= 1:  # Check if one second has passed
        flowRate = (pulse / 7.5) * 60
        psm.set_var("IW0", int(flowRate))
        pulse = 0
        startTime = currentTime  # Reset the start time      

def hardware_init():
    # Initialize PSM and set GPIO direction
    psm.start()
    GPIO.setup(GPIO_FlowSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_PumpControl, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GPIO_RangeEcho, GPIO.IN)
    GPIO.setup(GPIO_RangeTrigger, GPIO.OUT)
    GPIO.add_event_detect(GPIO_FlowSensor, GPIO.RISING, callback=handle_flow_interrupt)
    global startTime
    startTime = 0.000 
    global StartTime 
    StartTime = time.time()
    global pulse
    pulse = 0

# Handle when flow sensor detects rising edge
def handle_flow_interrupt(channel):
    global pulse
    pulse += 1
    
def get_distance():
    try:
        distance = distance_sensor.distance * 100  # convert to cm
        return distance
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None
    
def get_valveStatus():
    global valveStatus
    valveStatus = 0
    
    try:
        # Connect to the PLC
        connection = client.connect()
        if connection:  
        # Read the coil at address QX1.0 (address 0 in Modbus terms)
            result = client.read_coils(8, 1)
            print(f"Result: {result}")
            if not result.isError():
            # Print the value of the coil
                valveStatus = result.bits[0]
                print(f"valveStatus: {valveStatus}")
            else:
                print(f"Error reading %QX1.0: {result}")
        else:
            print("Failed to connect to the PLC")
            # Sleep for a short duration before polling again
            time.sleep(.05) #50ms
           
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
     #Close the connection to the PLC
        client.close()
 

def update_inputs():
    global StartTime
    #place here your code to update inputs
    update_flow()
    #Prevent trigger signal to the echo signal (>60ms)
    #time.sleep(0.07)
    distance = get_distance()
    if distance is not None:
        global prev_distance 
        prev_distance = distance
        print ("Measured Distance = %.1f cm" % distance)
        #psm.set_var("IW1", int(round(distance)))
    else:
        if prev_distance is not None:
            print (f"Measurment Failed, using last = {prev_distance}")
            distance = prev_distance
            #psm.set_var("IW1", int(round(prev_distance)))
        else:
            print ("Measurement Failed, no previous value")
    currentTime = time.time()
    ElapsedTime = currentTime - StartTime
    #print(ElapsedTime)
    if ElapsedTime >=10:
        psm.set_var("IW1", 2)
    else:
        psm.set_var("IW1", int(round(distance)))
    get_valveStatus()
    psm.set_var("IX0.0", valveStatus)
    #print(f"Distance: {distance} and {type(distance)}")
    #psm.set_var("IW1", int(round(distance)))
    #print(psm.get_var("IW1"))

def update_outputs():
    pumpState = GPIO.HIGH if psm.get_var("QX0.0") else GPIO.LOW
    GPIO.output(GPIO_PumpControl, pumpState)

if __name__ == "__main__":
    hardware_init()
    while not psm.should_quit():
        update_inputs()
        update_outputs()
        time.sleep(0.1)
    psm.stop()
