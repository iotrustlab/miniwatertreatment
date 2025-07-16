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

#GPIO Mode
GPIO.setmode(GPIO.BCM)

GPIO_FlowSensor = 4            #GPIO pin 4 connected to flow sensor's (YF-S201) data
GPIO_PumpControl = 14          #GPIO pin 14 connected to pump's relay
GPIO_RangeEcho = 15            #GPIO pin 15 connected to range's echo pin
GPIO_RangeTrigger = 18         #GPIO pin 18 connected to rang'es trigger pin

def hardware_init():
    #Insert your hardware initialization code in here
    psm.start()
    global startTime # Timing for flow sensor
    startTime = 0.000 
    global pulse
    pulse = 0  # Freqeuncy of pulse from flow sensor
    global prev_distance # Previous distance from range sensor 
    prev_distance = None
    #set GPIO direciton (IN / OUT)
    GPIO.setup(GPIO_FlowSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_PumpControl, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GPIO_RangeEcho, GPIO.IN)
    GPIO.setup(GPIO_RangeTrigger, GPIO.OUT)
    GPIO.add_event_detect(GPIO_FlowSensor, GPIO.RISING, callback=handle_flow_interrupt)

#Handle when flow sensor detects rising edge
def handle_flow_interrupt(channel):
    global pulse
    pulse += 1
    
def update_flow():
    global pulse
    global startTime
    currentTime = time.time()
    elapsedTime = currentTime - startTime
    if elapsedTime >= 1:  # Check if one second has passed
        flowRate = (pulse / 7.5) * 60
        #print(f"Flow Rate: {flowRate} L/Hr")
        #print(f"Pulse: {pulse}")
        psm.set_var("IW0", int(flowRate))
        pulse = 0
        startTime = currentTime  # Reset the start time      
    

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

    # save StartTime
    start_timeout = time.time()
    while GPIO.input(GPIO_RangeEcho) == 0:
        StartTime = time.time()
        if StartTime - start_timeout > timeout:
            return None

    # save time of arrival
    stop_time = time.time()
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
    update_flow()
    #Prevent trigger signal to the echo signal (>60ms)
    #time.sleep(0.07)
    distance = get_distance()
    if distance is not None:
        global prev_distance 
        prev_distance = distance
        #print ("Measured Distance = %.1f cm" % distance)
        psm.set_var("IW1", int(round(distance)))
    else:
        if prev_distance is not None:
            print (f"Measurment Failed, using last = {prev_distance}")
            psm.set_var("IW1", int(round(prev_distance)))
        else:
            print ("Measurement Failed, no previous value")
    #print(f"Distance: {distance} and {type(distance)}")
    #psm.set_var("IW1", int(round(distance)))
    #print(psm.get_var("IW1"))
    
def update_outputs():
    #place here your code to work on outputs
    pumpState = GPIO.HIGH if psm.get_var("QX0.0") else GPIO.LOW
    GPIO.output(GPIO_PumpControl, pumpState)

if __name__ == "__main__":
    hardware_init()
    while (not psm.should_quit()):
        update_inputs()
        update_outputs()
        time.sleep(0.1) #You can adjust the psm cycle time here
    psm.stop()