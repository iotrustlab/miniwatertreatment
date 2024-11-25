#                  - OpenPLC Python SubModule (PSM) -
# 
# PSM is the bridge connecting OpenPLC core to Python programs. PSM allows
# you to directly interface OpenPLC IO using Python and even write drivers 
# for expansion boards using just regular Python.
#
# PSM API is quite simple and just has a few functions. When writing your
# own programs, avoid touching on the "__main__" function as this regulates
# how PSM works on the PLC cycle. You can write your own hardware initialization
# code on hardware_init(), and your IO handling code on update_inputs() and
# update_outputs()
#
# To manipulate IOs, just use PSM calls psm.get_var([location name]) to read
# an OpenPLC location and psm.set_var([location name], [value]) to write to
# an OpenPLC location. For example:
#     psm.get_var("QX0.0")
# will read the value of %QX0.0. Also:
#     psm.set_var("IX0.0", True)
# will set %IX0.0 to true.
#
# Below you will find a simple example that uses PSM to switch OpenPLC's
# first digital input (%IX0.0) every second. Also, if the first digital
# output (%QX0.0) is true, PSM will display "QX0.0 is true" on OpenPLC's
# dashboard. Feel free to reuse this skeleton to write whatever you want.

#import all your libraries here
import psm
import time
import RPi.GPIO as GPIO
import board
import adafruit_tcs34725

#GPIO Mode
GPIO.setmode(GPIO.BCM)

GPIO_RangeEcho = 24         #GPIO pin 24 connected to range's echo
GPIO_RangeTrigger = 23      #GPIO pin 23 connected to range's trigger    
GPIO_DoserYellow = 20       #GPIO pin 20 connected to doser yellow's relay
GPIO_DoserBlue = 21         #GPIO pin 21 connected to doser blue's relay
GPIO_Valve = 16             #GPIO pin 16 connected to valve's relay

def hardware_init():
    #Insert your hardware initialization code in here
    psm.start()
    global i2c
    i2c = board.I2C()  # uses board.SCL and board.SDA
    global rgbSensor
    rgbSensor = adafruit_tcs34725.TCS34725(i2c)
    global prev_distance # Previous distance from range sensor
    prev_distance = None
    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_RangeEcho, GPIO.IN)
    GPIO.setup(GPIO_RangeTrigger, GPIO.OUT)
    GPIO.setup(GPIO_DoserYellow, GPIO.OUT)
    GPIO.setup(GPIO_DoserBlue, GPIO.OUT)
    GPIO.setup(GPIO_Valve, GPIO.OUT)

def get_distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_RangeTrigger,True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_RangeTrigger,False)

    # Initialize start and stop times
    StartTime = time.time()
    StopTime = time.time()

     #Define timeout duration (in seconds) 
     #Should try to stay within 20 ms cycle task time
    timeout = 0.01

    start_timeout = time.time()
    # save StartTime
    while GPIO.input(GPIO_RangeEcho) == 0:
        StartTime = time.time()
        if StartTime - start_timeout > timeout:
            return None

    stop_time = time.time()
    # save time of arrival
    while GPIO.input(GPIO_RangeEcho) == 1:
        StopTime = time.time()
        if StopTime - stop_time > timeout:
            return None

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    return (TimeElapsed * 34300) / 2 # Return Distance

def update_inputs():
    #place here your code to update inputs
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
            print (f"Measurment Failed, using last = {prev_distance}")
            psm.set_var("IW3", int(round(prev_distance)))
        else:
            print ("Measurement Failed, no previous value")
    psm.set_var("IW0", color_rgb[0])  #red value
    psm.set_var("IW1", color_rgb[1])  #green value
    psm.set_var("IW2", color_rgb[2])  #blue value
    #psm.set_var("IW3", int(round(distance)))
            
def update_outputs():
    #place here your code to work on outputs
    GPIO.output(GPIO_DoserYellow, GPIO.HIGH * psm.get_var("QX1.1"))
    GPIO.output(GPIO_DoserBlue, GPIO.HIGH * psm.get_var("QX1.2"))
    GPIO.output(GPIO_Valve, GPIO.HIGH * psm.get_var("QX1.0"))

if __name__ == "__main__":
    hardware_init()
    while (not psm.should_quit()):
        #print("Updating inputs...")
        update_inputs()
        #print("Updating outputs...")
        update_outputs()
        time.sleep(0.1) #You can adjust the psm cycle time here
    psm.stop()

