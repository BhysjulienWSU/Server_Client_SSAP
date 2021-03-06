#!/usr/bin/env python3
import time
import board
import busio   # also used for the max31855 temperature sensor
import adafruit_ads1x15.ads1015 as ADS
import queue
import threading
import urllib
from gpiozero import OutputDevice
from time import sleep
from serial import Serial
import csv
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import digitalio  # for temperature circuit
import adafruit_max31855  # for the temperature sensor circuit
from gpiozero import Button

sleep(30)
record_time =10 

RS485_direction = OutputDevice(17)
# address assign vrbls

address = b'Z'
sendAddress = OutputDevice(23)
sendAddress.off()
button = Button(22)
#sendAddress.on()
total_rec = 20
addressAssignTime = 5
count = 0

# enable reception mode. This bit controls the RS485 direction. "off" puts it in recieve mode. 
RS485_direction.off() #Start with read onlly

flag = True

#declare FIFO for buffer. 
q0 = queue.Queue()
q1 = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()
qt = queue.Queue()

#Set up i2c ports 
i2c = busio.I2C(board.SCL, board.SDA) 

#Create teh ADC object and point it towards the correct ports 
#adc0 = ADS.ADS1015(i2c)
adc1 = ADS.ADS1015(i2c, address=0x49) #49 ADDR tied to VCC
#0x48 ADDR tied to ground. 

#Setup chan x4 for each of the analog reads on the ADDR 0x49
chan0_0x49 = AnalogIn(adc1, ADS.P0);  
chan1_0x49 = AnalogIn(adc1, ADS.P1);
chan2_0x49 = AnalogIn(adc1, ADS.P2); 
chan3_0x49 = AnalogIn(adc1, ADS.P3);
#G

##### Servo Setup #####
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
servo1_pin = 26  # does not need to be PWM pin, the GPIO generates PWM signal
servo2_pin = 20

# Set servo pin as output for servo
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
servo1 = GPIO.PWM(servo1_pin, 50)  # 50 = 50Hz pulse
servo2 = GPIO.PWM(servo2_pin, 50)

#start PWM run, but with value of 0 (pulse off)
servo1.start(0)  # servo1 is male endcap
servo2.start(0)  # servo2 is female endcap

# define variable duty
duty = 2  # 2 equals 0 degrees, 12 equals 180, linear inbetween

# Setup for the max31855 temperature sensing circuit 
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
max31855 = adafruit_max31855.MAX31855(spi, cs)

temp_offset = -2.7  # linearly adjust temperature offset (degree C) for circuit temperature conversion
temp_flag = False   # when temperature reading command request recieved, set flag to true
def addressAssign(myAddress):
    count = 0
    address = myAddress
    print ("myAddress was = " + address.decode("utf-8"))
    t_stop = time.time()+total_rec # How much time is being recorded
    print (count)
    
    
    while time.time() < t_stop:
    #read in button
        if button.is_pressed:
            t_stop2 = time.time()+addressAssignTime # How much time is being recorded
            while time.time() < t_stop2:
                if button.is_pressed:
                    sleep(.5)
                    count = count +1
                    print (count)
            print("the value of count is now ")
            print(count)
            temp = count
            for val in range(temp):
                print(temp)
                sendAddress.on()
                sleep(.75)
                sendAddress.off()
                sleep(.25)
    print (count)
    if (count == 1):
        address = b'A'
    elif (count == 2):
        address = b'B'
    elif (count == 3):
        address = b'C'
    elif (count == 4):
        address = b'D'
    elif (count == 5):
        address = b'E'
    elif (count == 6):
        address = b'F'
    elif (count == 7):
        address = b'H'
    elif (count == 8):
        address = b'J'
    elif (count == 9):
        address = b'K'
    elif (count == 10):
        address = b'L'
    elif (count == 11):
        address = b'Z'
    elif (count == 15):
        address = b'B'
    elif (count == 16):
        address = b'N'
    elif (count == 17):
        address = b'M'
    elif (count == 18):
        address = b'N'
    else:
        address = b'X'
    
    print ("myAddress is now = " + address.decode("utf-8"))
    return address


def servoAng(servo, angDeg):
    '''
    Set angle of servo. Angles from 0 to 180 degrees.
    '''
    print("Move to angle " + str(angDeg))
    angDeg = int(angDeg)
    duty = float((angDeg / 180) * 10 + 2)  # range of 2 to 12 for 0 to 180 degrees (0 is servo off)
    servo.ChangeDutyCycle(duty)
    time.sleep(1.5)  # allow ample time to move servo
    servo.ChangeDutyCycle(0)  # stops sending the pulse signals, preventing twitching 
    

def servoOff(servo):
    '''
    Disables / turns-off servo. Stops sending the pulse signals.
    '''
    print("Turning off servo...")
    servo.ChangeDutyCycle(0)
    servo.stop()


while(True):
    with Serial('/dev/serial0',115200) as s:
        # waits for a single character
            rx = s.read(1)
            if (rx == b'A'): #Then a singal to start recording has been sent.
             #   print("RX: {0}".format(rx))
                print("Recording Data: Start")
                t_start = time.time()
                t_stop = time.time()+record_time # How much time is being recorded
                while time.time() < t_stop:
                    t_start = time.time() 
                    q1.put("{:>5.3f}".format(chan1_0x49.voltage))                   
                    
                    q2.put("{:>5.3f}".format(chan2_0x49.voltage))

                    q3.put("{:>5.3f}".format(chan3_0x49.voltage))
                    
                print("Recording Data: Stop")
                s.flush();
                
            if (rx == b'S'):  # servo anchor activated
                print("Activating servo anchors.")
                servoAng(servo1, 70)  # estimate angle to set anchor - will need physical testing
                servoAng(servo2, 110)
                # angles different becasue the endcaps are mirrored from each other, not exactly the same
                
            elif (rx == b'R'):  # servo anchor deactivated
                print("Deactivating servo anchors.")
                servoAng(servo1, 180)  # angle for arm to be retracted inward
                servoAng(servo2, 0)
                
            elif (rx == b'T'):  # servo anchor deactivated
                print("Getting temperature reading.")
                for j in range(10):
                    tempC = max31855.temperature
                    tempC = tempC + temp_offset
                    tempF = tempC * 9 / 5 + 32
                    qt.put("{:>5.3f}".format(tempC))
                    sleep(0.02)
                    temp_flag = True
            elif(rx == b'G'):
                print("Calling address assignment")
                address = addressAssign(address)
                
    with Serial('/dev/serial0', 115200) as s2:
        while not q1.empty():
            if(flag == False):              
                #Unload buffer
                
                RS485_direction.on()
                delim = ','
                
                value = q1.get()
                s2.write(value.encode())
                s2.write(delim.encode())
                sleep(0.001)
                value1 = q2.get()
                s2.write(value1.encode())
                s2.write(delim.encode())
                sleep(0.001)
                value2 = q3.get()
                s2.write(value2.encode())
                s2.write(delim.encode())
                sleep(0.001)                
                if(q1.empty()):
                    print("Serial Data Transmission from B is complete")
                    RS485_direction.off()
                    flag = True
            else:
                rx = s2.read(1)
                if rx == address:
                    flag = False
                    print("RX: {0}".format(rx))
                s2.flush()

        s2.flush()
        if(temp_flag):
            # check if recieved "ready for tamperature data" signal
            rx = s2.read(1)
            if rx == address:
                print("RX: {0}".format(rx))
                for j in range(10):
                    RS485_direction.on()
                    delim = ','
    
                            # prepare data to transmit 
                    value = qt.get()
                    s2.write(value.encode())
                    s2.write(delim.encode())
                    sleep(0.02)
                    temp_flag = False
            RS485_direction.off()
            s2.flush()
            
            

servoOff(servo1)
servoOff(servo2)
GPIO.cleanup()
