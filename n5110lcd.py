## 2020.11.26. 1st release: shows SN & Location
## 2020.12.15. 2nd release: shows SN, Order#, PN & Location

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_pcd8544

import RPi.GPIO as GPIO
import serial
import time
import os
import netifaces as ni
import urllib.request

# Set Interrupt environment
GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(21, GPIO.FALLING)

FILE='/home/pi/naver/order.csv'
SERVERS=open(FILE).readlines()

# Define 5110 LCD environment
spi = busio.SPI(board.SCK, MOSI=board.MOSI)
#dc = digitalio.DigitalInOut(board.D23)  # data/command
dc = digitalio.DigitalInOut(board.D25)  # data/command
cs = digitalio.DigitalInOut(board.CE0)  # Chip select
reset = digitalio.DigitalInOut(board.D24)  # reset

display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

# Contrast and Brightness Settings
display.bias = 4
display.contrast = 60

# Turn on the Backlight LED
backlight = digitalio.DigitalInOut(board.D13)  # backlight
backlight.switch_to_output()
backlight.value = True

# Clear display.
display.fill(0)
display.show()

## Display IP address
try:
    addrs=ni.ifaddresses('wlan0')
    IPADDR=addrs[ni.AF_INET][0]['addr']
except:
    IPADDR="No connection"

## Initialize serial port
SPORT='/dev/serial0'
BAUD=9600

ser=serial.Serial(SPORT, BAUD, timeout=1)
ser.close()
time.sleep(1)
ser.open()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (display.width, display.height))
display.image(image)
display.show()

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

## Functions

def readfile():
    global FILE
    global SERVERS
    SERVERS=open(FILE).readlines()

def clearlcd():
    display.fill(0)
#    display.show()
    image = Image.new("1", (display.width, display.height))
    draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=0, fill=0)
    display.image(image)
    display.show()

def showip():
#    draw.rectangle((0, 0, display.width, 8), outline=1, fill=255)
    draw.rectangle((0, 0, display.width, 8), outline=0, fill=255)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7)
    text = IPADDR
    (font_width, font_height) = font.getsize(text)
    draw.text((display.width // 2 - font_width // 2,0),text,font=font,fill=0)

def r2scan():
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    text = "Ready to scan!"
    (font_width, font_height) = font.getsize(text)
    draw.text((display.width // 2 - font_width //2,7),text,font=font,fill=255)

def scan():
    global SERVERS
    output = ""
    while output == "":
        SCANNED=ser.readline()
        input=SCANNED.decode('utf-8').rstrip()
        if input != "":
            for i in SERVERS:
                if input.rstrip() in i:
                    print (input.rstrip())
                    j=i.split(",")
                    output=j[2].rstrip()
                    model=j[0].rstrip()
                    order=j[3].rstrip()
                    break
                else:
                    output="No Match!!"
                    model=""
                    order=""

            return input,output,model,order
        else:
            input=""

def showsn(text):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    (font_width, font_height) = font.getsize(text)
    draw.text((display.width // 2 - font_width //2,20),text,font=font,fill=255)

def showtarget(text):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    (font_width, font_height) = font.getsize(text)
#    draw.text((display.width // 2 - font_width //2,36),text,font=font,fill=255)
    draw.text((68,37),text,font=font,fill=255)

def showmodel(text):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    (font_width, font_height) = font.getsize(text)
#    draw.text((display.width // 2 - font_width //2,27),text,font=font,fill=255)
    draw.text((2,39),text,font=font,fill=255)

def showorder(text):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7)
    (font_width, font_height) = font.getsize(text)
    draw.text((display.width // 2 - font_width //2,31),text,font=font,fill=255)
#    draw.text((3,38),text,font=font,fill=255)

# Read data file intiall

readfile()

while 1:
    showip()
    r2scan()
    display.image(image)
    display.show()

#    (sn, target)=scan()
    (sn, target, pn, on)=scan()
    clearlcd()

    showsn(sn)
    showmodel(pn)
    showorder(on)
    showtarget(target)
    display.image(image)
    display.show()

#    if GPIO.event_detected(21):
#        readfile()
#        showsn("Re-read data")

    time.sleep(1)

