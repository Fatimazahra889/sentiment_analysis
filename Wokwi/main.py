"""you could check the code on wokwi following the link below
     https://wokwi.com/projects/423397511758760961
     
                                                    """

from machine import Pin, SPI, PWM
import time
import network
import umqtt.simple as mqtt
from ili9341 import ILI9341, color565

# WiFi Credentials
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

# MQTT Broker & Topic
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "flaskapp"

# Initialize SPI for ILI9341 Display
spi = SPI(1, baudrate=10000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
display = ILI9341(spi, dc=Pin(21), cs=Pin(5), rst=Pin(22))

# Buzzer Setup (on Pin 17)
buzzer = PWM(Pin(17))
buzzer.duty_u16(0)  # Volume set to 0 initially

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 10  # Timeout after 10 seconds
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        print(".", end="")

    if wlan.isconnected():
        print("\n Connected to WiFi!")
        print("IP Address:", wlan.ifconfig()[0])
    else:
        print("\n WiFi Connection Failed! Retrying in 5 seconds...")
        time.sleep(5)
        connect_wifi()

# Play Tones
def play_tone(freq, duration):
    if freq > 0:
        buzzer.freq(freq)
        buzzer.duty_u16(20000)  # Moderate volume
    else:
        buzzer.duty_u16(0)
    time.sleep_ms(duration)

# Happy & Sad Sounds
def play_sad_sound():
    """Plays the sad sound sequence."""
    play_tone(622, 300)
    play_tone(587, 300)
    play_tone(554, 300)

    # Wobbling effect
    for _ in range(10):
        for pitch in range(-10, 11):
            play_tone(523 + pitch, 5)

    # Stop sound
    buzzer.duty_u16(0)
    time.sleep_ms(500)

def play_happy_sound():
    """Plays a level-up sound instead of the current happy sound."""
    play_tone(330, 150)  
    play_tone(392, 150)  
    play_tone(659, 150)  
    play_tone(523, 150)  
    play_tone(587, 150)  
    play_tone(784, 150)  
    buzzer.duty_u16(0)  
    time.sleep_ms(500)

def draw_glowing_crescent(display, x, y, radius, glow_radius, color):
    """
    Draws a crescent shape with a glow effect at position (x, y) faster.
    """
    # Speed up by using a larger step in the loop
    for i in range(glow_radius, radius, -3):  # Faster drawing
        glow_color = color565(int(98 * (i / glow_radius)), int(35 * (i / glow_radius)), int(204 * (i / glow_radius)))
        display.fill_arc(x, y, i, i-3, 200, 340, glow_color)  

    # Main crescent
    display.fill_arc(x, y, radius, radius-5, 200, 340, color)

# Display Expressions
def draw_eyes(display, mood="neutral"):
    display.fill_screen(0x0000)  # Black background
    eye_color = color565(98, 35, 204)

    if mood == "neutral":
        display.fill_rect(60, 120, 50, 80, eye_color)
        display.fill_rect(130, 120, 50, 80, eye_color)
        print(" Neutral Face Displayed")

    elif mood == "sad":
        display.fill_rect(60, 120, 50, 50, eye_color)
        display.fill_rect(130, 120, 50, 50, eye_color)
        display.fill_triangle(60, 170, 110, 170, 85, 200, 0x0000)
        display.fill_triangle(130, 170, 180, 170, 155, 200, 0x0000)
        print("Sad Face Displayed")
        play_sad_sound()

    elif mood == "happy":
        draw_glowing_crescent(display, 85, 140, 25, 30, eye_color)   # Left crescent
        draw_glowing_crescent(display, 155, 140, 25, 30, eye_color)  # Right crescent
        print("Happy Face Displayed")
        play_happy_sound()

#  MQTT Message Handling
def on_message(topic, msg):
    mood = msg.decode().strip().lower()
    print(f" Received MQTT Message: '{mood}' on Topic: '{topic.decode()}'")

    if mood == "positive":
        draw_eyes(display, "happy")
    elif mood == "negative":
        draw_eyes(display, "sad")
    else:
        draw_eyes(display, "neutral")

#  MQTT Setup
def setup_mqtt():
    client = mqtt.MQTTClient("esp32_client", MQTT_BROKER, MQTT_PORT)
    client.set_callback(on_message)

    print(f" Connecting to MQTT Broker {MQTT_BROKER}...")
    try:
        client.connect()
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to Topic: '{MQTT_TOPIC}'")
    except Exception as e:
        print(f"MQTT Connection Failed: {e}")
        time.sleep(5)
        setup_mqtt()

    return client

#  Main Program
connect_wifi()  # Connect to WiFi
mqtt_client = setup_mqtt()  # Setup MQTT

#  Main Loop
while True:
    try:
        mqtt_client.check_msg()  # Check for new MQTT messages
        time.sleep(0.5)  # Prevent excessive CPU usage
    except Exception as e:
        print(f"Error in MQTT Loop: {e}")
        time.sleep(2)
