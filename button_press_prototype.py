import time
import board
import RPi.GPIO as GPIO
from gpiozero import OutputDevice
from gpiozero import Button
from time import sleep

sendAddress = OutputDevice(18)
button = Button(27)

sendAddress.off()
record_time = 60
addressAssignTime = 10
count = 0


t_stop = time.time()+record_time # How much time is being recorded
t_stop2 = time.time()+addressAssignTime # How much time is being recorded
#while we have read a value. 


while time.time() < t_stop:
    #read in button
    if button.is_pressed:
        while time.time() < t_stop2:
            if button.is_pressed:
                count += 1
                print (count)
                sleep(.5)
    if time.time() > t_stop2:
        count = count +1
        for val in range(count):
            sendAddress.off()
            sleep(.75)
            sendAddress.on()
            sleep(.25)
            
        