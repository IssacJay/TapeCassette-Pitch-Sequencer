# PITCH MOD
import machine
from machine import Pin
from machine import ADC
from machine import UART
import time
import math
import _thread
import ustruct
from rotary import Rotary
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf


#SET UP VARIABLES
#VOLUME 
vol = machine.PWM(machine.Pin(14)) #Volume PWM
vol.freq(1000) #Frequency of PWM

#PWM
motor = machine.PWM(machine.Pin(15)) #Motor Speed PWM
motor.freq(1000) #Frequency of PWM

#OLED
i2c=I2C(1,sda=Pin(6), scl=Pin(7), freq=400000) #Initiate paramers for the OLED-SSD1036 display
oled = SSD1306_I2C(128, 64, i2c) #Create instance of  OLED-SSD1036 display using the MicroPython OLED-SSD1036 module

#ROTARY ENCODER
rotary = Rotary(18,17,19) #DT (Direction), CK(Clock),SW(Switch)switch
switch = Pin(19, mode=Pin.IN, pull = Pin.PULL_UP) # Inbuilt switch on the rotary encoder
val = 60 #Starting value for the Pitch
freq = pow(2, ((val-69)/12)) * 440  
rotStep = 1 #Each step of the rotary encoder +- 1

#MOTOR PWM SETTINGS 
K = 4427.6
a = 0.002
line_offset = [] #how many characters in each line
Start = True

#OTHER VARIABLES
endtask = False

#READ SETTINGS FOR EXPONENTIAL CONVERTION EQUATION
def read_settings(): #Read Constant and Power Values from Settings File
    global K, a #access power law settings variables
    with open('lib/settings.txt', 'r') as settings:
        offset = 0 #how many charcters in current line
        for line in settings: #for each line in file
            line_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        settings.seek(0) #rewind to position zero 

        settings.seek(line_offset[0]) #seek to selected line
        constant = settings.readline() #read the constant variable
        K = constant.strip() #Remove String components
        K = float(K) #Convert to float
        settings.seek(line_offset[1]) #seek to selected line
        power = settings.readline() #read the power variable
        a = power.strip() #Remove String Components
        a = float(a) #Convert to float
        current_settings = [constant, power] #Add settings into array
        print('Current Settings are: ' + str(current_settings)) #Print current settings
        settings.close() #Close the settings .txt file

        return(current_settings) #Return the settings array
    
#ROTARY ENCODER
def rotary_changed(change): #Pass through state 
    global val, K, a, endtask
    if change == Rotary.ROT_CW: # If rotation is clockwise
        if val < 88: #And value is < 88
            val = val + rotStep #Add 1 to note value
            freq = pow(2, ((val-69)/12)) * 440  #Calculate frequency from midi note
        oled.fill(0) #Clear display
        FreqValue = 'Freq = ' + str(int(freq)) + "Hz" #String for Frequency 
        oled.text(FreqValue, 1, 20) #Add frequency value to display
        MidiValue = 'MIDI = ' + str(val) #Sting for MIDI
        oled.text(MidiValue, 1, 30) ´#Add MIDI note text to display
        oled.text("PITCH CONTROL", 1, 1) #Add title
        oled.text("Click for menu", 1, 55) #Add menu text
        oled.show() #Refresh Screen
    elif change == Rotary.ROT_CCW: #If rotation is anti-clockwise
        if val > 1: #And value is > 1
            val = val - rotStep # - 1 from midi value
            freq = pow(2, ((val-69)/12)) * 440 #Calculate frequency
        oled.fill(0) #Clear display
        FreqValue = 'Freq = ' + str(int(freq)) + "Hz" #String for frequency
        oled.text(FreqValue, 1, 20) #Add frequency text to display
        MidiValue = 'MIDI = ' + str(val) #String for MIDI
        oled.text(MidiValue, 1, 30) #Add midi note text to display
        oled.text("PITCH CONTROL", 1, 1) #title
        oled.text("Click for menu", 1, 55) #Menu text
        oled.show()#Refresh Screen
        
    elif change == Rotary.SW_PRESS: #If button pressed
        endtask = True #Change end task bool to true
        
    elif change == Rotary.SW_RELEASE: #If button released
        print("Do Nothing")
        
    duty = K * math.exp(a * freq) #Calculate duty cycle
    print('MIDI Note is ' + str(val) + ' PWM Duty is ' + str(int(duty))) #Print note and PWM values             

#PWM MOTOR CONTROL
def motor_Speed(): 
    global val, K, a

    freq = pow(2, ((val-69)/12)) * 440 #Calculate Frequency
    duty = K * math.exp(a * freq) #Calulcate Duty Cycle (from expnential equation) 
    
    motor.duty_u16(int(duty)) #Update Motor Duty Cycle
    vol.duty_u16(int(65535)) #Set volume duty cycle to 100%
    time.sleep(0.1) #Sleep for 0.1 second
    
    
#CALL INITIAL FUNCTIONS
read_settings() #Read Settings

oled.fill(0) #Clear Display
FreqValue = 'Freq = ' + str(int(freq)) + "Hz" #Frequency text
oled.text(FreqValue, 1, 20) #Show Frequency Text
MidiValue = 'MIDI = ' + str(val) #MIDI Text 
oled.text(MidiValue, 1, 30) #Show MIDI Text
oled.text("PITCH CONTROL", 1, 1) #Title Text
oled.text("Click for menu", 1, 55) #Menu Text
oled.show() #Show Display

rotary.add_handler(rotary_changed) #Interupt handler for rotary encoder

#LOOP
while True:
    motor_Speed() #Update Motor Speed

    if endtask == True: #If 'return to menu' selected
        break #Break loop (finish execution)


