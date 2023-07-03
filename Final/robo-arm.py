import network
import socket
from time import sleep
import machine
from machine import Pin, PWM

ssid = 'Totalplay-CBA4'
password = 'Burrito guinda 2019'

Motor_A_Adelante = Pin(18, Pin.OUT)
Motor_A_Atras = Pin(19, Pin.OUT)
Motor_B_Adelante = Pin(20, Pin.OUT)
Motor_B_Atras = Pin(21, Pin.OUT)

servo1 = PWM(Pin(15))
servo1.freq(50)
servo2 = PWM(Pin(16))
servo1.freq(50)
servo3 = PWM(Pin(17))
servo1.freq(50)

def adelante():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)
    
def atras():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(1)
    Motor_B_Atras.value(1)

def detener():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(0)

def izquierda():
    Motor_A_Adelante.value(1)
    Motor_B_Adelante.value(0)
    Motor_A_Atras.value(0)
    Motor_B_Atras.value(1)

def derecha():
    Motor_A_Adelante.value(0)
    Motor_B_Adelante.value(1)
    Motor_A_Atras.value(1)
    Motor_B_Atras.value(0)

def set_servo_angle(servo, angle):
    duty = int(40 + (angle / 180) * 115)
    servo.duty(duty)

detener()
    
def conectar():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(ssid, password)
    while not red.isconnected():
        print('Conectando ...')
        sleep(1)
    ip = red.ifconfig()[0]
    print(f'Conectado con IP: {ip}')
    return ip
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def pagina_web():
    html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
            <script>
            function setServoAngle(servo, angle) {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/set_servo?servo=" + servo + "&angle=" + angle, true);
                xhr.send();
            }
            </script>
            </head>
            <body>
            <center>
            <form action="/adelante">
            <input type="submit" value="Adelante" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"  />
            </form>
            <table><tr>
            <td><form action="/izquierda">
            <input type="submit" value="Izquierda" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form></td>
            <td><form action="/detener">
            <input type="submit" value="Detener" style="background-color: #FF0000; border-radius: 50px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px" />
            </form></td>
            <td><form action="/derecha">
            <input type="submit" value="Derecha" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form></td>
            </tr></table>
            <form action="/atras">
            <input type="submit" value="Atras" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form>
            <br>
            <h3>Giro (180°):</h3>
            <input type="range" min="0" max="180" value="90" oninput="setServoAngle(1, this.value);">
            <br><br>
            <h3>Altura (180°):</h3>
            <input type="range" min="0" max="180" value="90" oninput="setServoAngle(2, this.value);">
            <br><br>
            <h3>Gripper (90°):</h3>
            <input type="range" min="0" max="90" value="45" oninput="setServoAngle(3, this.value);">
            </body>
            </html>
            """
    return html

def serve(connection):
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            path = request.split()[1]
        except IndexError:
            pass
        if path == '/adelante?':
            adelante()
        elif path == '/izquierda?':
            izquierda()
        elif path == '/detener?':
            detener()
        elif path == '/derecha?':
            derecha()
        elif path == '/atras?':
            atras()
        elif path.startswith('/set_servo?'):
            servo, angle = path.split('=')[1].split('&')
            servo = int(servo)
            angle = int(angle)
            if servo == 1:
                set_servo_angle(servo1, angle)
            elif servo == 2:
                set_servo_angle(servo2, angle)
            elif servo == 3:
                set_servo_angle(servo3, angle)
        html = pagina_web()
        client.send(html)
        client.close()

try:
    ip = conectar()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
