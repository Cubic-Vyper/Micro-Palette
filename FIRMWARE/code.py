import board
import busio
import time
import neopixel
import adafruit_tcs34725
import adafruit_ssd1306
import digitalio  


#define pins

# Sensor I2C pins
SENSOR_SCL = board.D0
SENSOR_SDA = board.D1

#sensor led (illuminates object in dark case)
SENSOR_LED = board.D2

# oled I2C pins
OLED_SCL = board.D3
OLED_SDA = board.D4

#SK6812 pin
LED_DATA = board.D5

#start sensor i2c 
sensor_i2c = busio.I2C(SENSOR_SCL, SENSOR_SDA)

#start color sensor
sensor = adafruit_tcs34725.TCS34725(sensor_i2c)
sensor.integration_time = 50  #sensor collection time
sensor.gain = 4  #amplify signal 

#turn on sensor LED 
sensor_led = digitalio.DigitalInOut(SENSOR_LED)
sensor_led.direction = digitalio.Direction.OUTPUT
sensor_led.value = True  
print("sensor LED on")

#start oled i2c 
oled_i2c = busio.I2C(OLED_SCL, OLED_SDA)

#start oled display
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, oled_i2c)   

#start SK6812 LEDs
Pixels = neopixel.NeoPixel(LED_DATA, 2, brightness=0.3, auto_write=True)

#color codes
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128)
}

def convert_to_8bit(r, g, b):
    r8 = r * 255 // 65535
    g8 = g * 255 // 65535
    b8 = b * 255 // 65535
    return r8, g8, b8

def find_closest_color(r8, g8, b8):
    closest_name = "unknown"
    smallest_distance = 999999

    #compare color
    for name, (cr, cg, cb) in COLORS.items():
        #calculate color difference
        distance = (r8 - cr) ** 2 + (g8 - cg) ** 2 + (b8 - cb) ** 2
        
        if distance < smallest_distance:
            smallest_distance = distance
            closest_name = name

    #only return color name if it's close enough 
    if smallest_distance > 20000: 
        return "unknown"
    else:
        return closest_name  

def update_oled(color_name, r16, g16, b16):
    #clear display 
    oled.fill(0)
    
    #show color name 
    oled.text(color_name, 0, 0, 1)
    
    #show raw 16-bit RG values 
    oled.text(f"R:{r16:4d} G:{g16:4d}", 0, 12, 1)
    
    #show raw 16-bit blue value
    oled.text(f"B:{b16:4d}", 0, 22, 1)
    
    #update display
    oled.show()

def update_leds(r8, g8, b8):
    Pixels.fill((r8, g8, b8))

#main loop
update_oled("scanning...", 0, 0, 0)

while True:
    try:
        #read 16-bit values
        r16, g16, b16 = sensor.color_raw

        #convert to 8-bit
        r8, g8, b8 = convert_to_8bit(r16, g16, b16)

        #find closest color
        color_name = find_closest_color(r8, g8, b8)

        #update oled with color name and 16-bit values
        update_oled(color_name, r16, g16, b16)
        
        #update leds 
        update_leds(r8, g8, b8)

        #0.5 second delay before next scan -- this will prevent accidental scans
        time.sleep(0.5)

    except Exception as e:
        #show error
        print("Error:", e)
        update_oled("Error", 0, 0, 0)
        time.sleep(1)