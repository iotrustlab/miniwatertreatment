from pylogix import PLC
import time
import RPi.GPIO as GPIO

#Python script that treats the raspberry pi as a bridge between the physical sensors and the Compact logix PLC

compactLogixIP = '192.168.1.10'

#GPIO Mode
GPIO.setmode(GPIO.BCM)

GPIO_FlowSensor = 4            #GPIO pin 4 connected to flow sensor's (YF-S201) data
GPIO_PumpControl = 14          #GPIO pin 14 connected to pump's relay
GPIO_RangeEcho = 15            #GPIO pin 15 connected to range's echo pin
GPIO_RangeTrigger = 18         #GPIO pin 18 connected to rang'es trigger pin

#controller tags
range_sensor_tag = 'Program:MainProgram.RangeSensor'
pump_tag = 'Program:MainProgram.Pump'
flow_sensor_tag = 'Program:MainProgram.FlowSensor'
desired_distance_fill_tag = 'Program:MainProgram.desiredDistanceFill'

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
        pulse = 0
        startTime = currentTime  # Reset the start time  
        return flowRate
    return 0

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

def hardware_init():
    #Insert your hardware initialization code in here
    #set GPIO direciton (IN / OUT)
    GPIO.setup(GPIO_FlowSensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_PumpControl, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GPIO_RangeEcho, GPIO.IN)
    GPIO.setup(GPIO_RangeTrigger, GPIO.OUT)

    global startTime
    startTime = 0.000 
    global pulse


    pulse = 0  # Freqeuncy of pulse from flow sensor
    GPIO.add_event_detect(GPIO_FlowSensor, GPIO.RISING, callback=handle_flow_interrupt)


def update_inputs():
    comm.Write(flow_sensor_tag, int(update_flow()))

    #average distance readings for debouncing
    total = 0
    for i in range(100):
        distance = get_distance()
        total = total + distance if distance is not None else total
    if total is not None:
        ret = comm.Write(range_sensor_tag, int(total / 100))

def update_outputs():
    pumpState = GPIO.HIGH if comm.Read(pump_tag).Value else GPIO.LOW
    GPIO.output(GPIO_PumpControl, pumpState)

if __name__ == '__main__':
    hardware_init()
    with PLC() as comm:
        comm.IPAddress = compactLogixIP
        while 1:
            update_inputs()
            time.sleep(0.1)
            update_outputs()
            print(comm.Read(pump_tag))
            print(comm.Read(range_sensor_tag))
