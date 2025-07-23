import network
import socket
import neopixel
import machine
import ure

# Configuración de red WiFi
SSID = 'TECNO'
PASSWORD = 'BalatroBalatrez'

# Pines
PIN_NEOPIXEL = 18  # GPIO donde está conectado el anillo
NUM_LEDS = 16
PIN_UV = 19        # GPIO para LED UV

# Inicializa LED UV
led_uv = machine.Pin(PIN_UV, machine.Pin.OUT)
led_uv.off()

# Inicializa anillo NeoPixel
np = neopixel.NeoPixel(machine.Pin(PIN_NEOPIXEL), NUM_LEDS)

# Conexión WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Conectando al WiFi...")
while not wlan.isconnected():
    pass

ip = wlan.ifconfig()[0]
print("Conectado. IP:", ip)

# Servidor HTTP
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
print("Servidor listo en http://%s" % ip)

def set_color(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write()

while True:
    conn, addr = s.accept()
    print("Conexión desde", addr)
    request = conn.recv(1024).decode('utf-8')
    print("Petición:", request)

    # Busca comandos
    match_color = ure.search(r'GET\s+/color\?r=(\d+)&g=(\d+)&b=(\d+)', request)
    match_uv_on = ure.search(r'GET\s+/uv\?state=on', request)
    match_uv_off = ure.search(r'GET\s+/uv\?state=off', request)

    if match_color:
        r = int(match_color.group(1))
        g = int(match_color.group(2))
        b = int(match_color.group(3))
        print("Color recibido:", r, g, b)
        set_color(r, g, b)
        response = "Color actualizado"

    elif match_uv_on:
        led_uv.on()
        print("LED UV encendido")
        response = "UV ON"

    elif match_uv_off:
        led_uv.off()
        print("LED UV apagado")
        response = "UV OFF"

    else:
        response = "Comando no reconocido"

    conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n')
    conn.send(response)
    conn.close()