import board
import busio
import time
import neopixel
import adafruit_tcs34725
import adafruit_ssd1306
import digitalio  


#define pins

# I2C pins (sensor and oled)
I2C_SDA = board.D4
I2C_SCL = board.D5

#sensor led (illuminates object)
SENSOR_LED = board.D8

#SK6812 pin
LED_DATA = board.D3

#Switch pin
SWITCH_PIN = board.D6

# start i2c 
i2c = busio.I2C(I2C_SCL, I2C_SDA)

#start color sensor
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50  #sensor collection time
sensor.gain = 4  

#turn on sensor LED 
sensor_led = digitalio.DigitalInOut(SENSOR_LED)
sensor_led.direction = digitalio.Direction.OUTPUT
sensor_led.value = True  
print("sensor LED on")

#Switch setup
switch = digitalio.DigitalInOut(SWITCH_PIN)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

#start oled display
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)   

#start SK6812 LEDs
pixels = neopixel.NeoPixel(LED_DATA, 2, brightness=0.3, auto_write=True)

#color codes
COLORS = {
    "red":     (255,  80, 107),
    "green":   (111, 255, 160),
    "blue":    ( 75, 149, 255),
    "yellow":  (255, 197, 122),
    "cyan":    (100, 232, 255),
    "pink": (255, 112, 172),
    "orange":  (255, 129, 103),
    "purple":  (190, 154, 255),
    "white":   (255, 253, 253),
    "gray": (212, 253, 255),
    "black":   (  0,   0,   0),
}


def find_closest_color(r8, g8, b8, r16, g16, b16):
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
    if closest_name == "white" and max(r16, g16, b16) < 2500:
        return "gray"

    return closest_name

def update_oled(color_name, r8, g8, b8):
    #clear display 
    oled.fill(0)
    
    #show color name 
    oled.text(color_name, 0, 0, 1)
    
    #show 8-bit RG values 
    oled.text(f"R:{r8:3d} G:{g8:3d}", 0, 12, 1)
    
    #show 8-bit blue value
    oled.text(f"B:{b8:3d}", 0, 22, 1)
    
    #update display
    oled.show()

def update_leds(r8, g8, b8):
    pixels.fill((r8, g8, b8))

# normalize color

WB_R = 4607
WB_G = 3628
WB_B = 2082


def normalize_color(r, g, b):

    r_bal = r / WB_R
    g_bal = g / WB_G
    b_bal = b / WB_B

    if max(r_bal, g_bal, b_bal) < 0.08:
        return (0, 0, 0)

    max_bal = max(r_bal, g_bal, b_bal)
    r8 = min(255, int((r_bal / max_bal) * 255))
    g8 = min(255, int((g_bal / max_bal) * 255))
    b8 = min(255, int((b_bal / max_bal) * 255))

    return r8, g8, b8


#main loop
update_oled("Press Button...", 0, 0, 0)

#turn off LEDs
pixels.fill((0, 0, 0))

while True:
    try:
        if not switch.value:  # button pressed

            #values
            r16, g16, b16, _ = sensor.color_raw
            r8, g8, b8 = normalize_color(r16, g16, b16)
            
            #find closest
            color_name = find_closest_color(r8, g8, b8, r16, g16, b16)

            #update oled
            update_oled(color_name, r8, g8, b8)
        
            #update leds    
            update_leds(r8, g8, b8)

            #Prevent mutiple scans in one press
            time.sleep(0.2)
            
            while not switch.value:
                time.sleep(0.05)
            
            time.sleep(0.1)
            
            
            
        else:
            time.sleep(0.05)

    except Exception as e:
        #show error
        print("Error:", e)
        update_oled("Error", 0, 0, 0)
        time.sleep(1)
