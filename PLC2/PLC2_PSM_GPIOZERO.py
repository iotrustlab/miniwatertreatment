# Import all your libraries here
import psm
import time
import RPi.GPIO as GPIO
from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import board
import adafruit_tcs34725

# GPIO Mode
GPIO.setmode(GPIO.BCM)

GPIO_RangeEcho = 24         # GPIO pin 24 connected to range's echo
GPIO_RangeTrigger = 23      # GPIO pin 23 connected to range's trigger    
GPIO_DoserYellow = 20       # GPIO pin 20 connected to doser yellow's relay
GPIO_DoserBlue = 21         # GPIO pin 21 connected to doser blue's relay
GPIO_Valve = 16             # GPIO pin 16 connected to valve's relay

# Use PiGPIOFactory to set pigpio as the backend
pigpio_factory = PiGPIOFactory()

# Initialize the DistanceSensor with the pigpio factory
range_sensor = DistanceSensor(echo=GPIO_RangeEcho, trigger=GPIO_RangeTrigger, pin_factory=pigpio_factory)

def hardware_init():
    # Insert your hardware initialization code in here
    psm.start()
    global i2c
    i2c = board.I2C()  # uses board.SCL and board.SDA
    global rgbSensor
    rgbSensor = adafruit_tcs34725.TCS34725(i2c)
    global prev_distance  # Previous distance from range sensor
    prev_distance = None
    # Set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_DoserYellow, GPIO.OUT)
    GPIO.setup(GPIO_DoserBlue, GPIO.OUT)
    GPIO.setup(GPIO_Valve, GPIO.OUT)

def get_distance():
    try:
        # Get distance in meters and convert to centimeters
        distance = range_sensor.distance * 100
        print(f"Measured Distance = {distance} cm, {range_sensor.distance} m")
        return distance
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_inputs():
    # Place here your code to update inputs
    global rgbSensor
    color_rgb = rgbSensor.color_rgb_bytes
    distance = get_distance()
    if distance is not None:
        global prev_distance
        prev_distance = distance
        #print ("Measured Distance = %.1f cm" % distance)
        psm.set_var("IW3", int(round(distance)))
    else:
        if prev_distance is not None:
            print(f"Measurement Failed, using last = {prev_distance}")
            psm.set_var("IW3", int(round(prev_distance)))
        else:
            print("Measurement Failed, no previous value")
    psm.set_var("IW0", color_rgb[0])  # Red value
    psm.set_var("IW1", color_rgb[1])  # Green value
    psm.set_var("IW2", color_rgb[2])  # Blue value
            
def update_outputs():
    # Place here your code to work on outputs
    GPIO.output(GPIO_DoserYellow, GPIO.HIGH if psm.get_var("QX1.1") else GPIO.LOW)
    GPIO.output(GPIO_DoserBlue, GPIO.HIGH if psm.get_var("QX1.2") else GPIO.LOW)
    GPIO.output(GPIO_Valve, GPIO.HIGH if psm.get_var("QX1.0") else GPIO.LOW)

if __name__ == "__main__":
    hardware_init()
    while not psm.should_quit():
        #print("Updating inputs...")
        update_inputs()
        #print("Updating outputs...")
        update_outputs()
        time.sleep(0.1)  # You can adjust the psm cycle time here
    psm.stop()
