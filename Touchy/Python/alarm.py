import gpiozero
import threading
from time import sleep
from random import random
from colorama import Fore

stop_alarm = False
buzzer = None
led = None
console = None

def Led(Led_Pin):
    Led = gpiozero.LED(Led_Pin)
    global stop_alarm
    while not stop_alarm:
        sleep(0.25)
        Led.on()
        sleep(0.5)
        Led.off()
        sleep(random())
    if stop_alarm:
        Led.off()

def Buzzer(Buzzer_Pin):
    Buzzer = gpiozero.Buzzer(Buzzer_Pin)
    global stop_alarm
    while not stop_alarm:
        Buzzer.on()
        sleep(1)
        Buzzer.off()
        sleep(0.5)
        Buzzer.on()
        sleep(0.5)
        Buzzer.off()
    if stop_alarm:
        Buzzer.off()

def Console(Sleep_time):
    global stop_alarm
    while not stop_alarm:
        print(Fore.RED + "ALARM!" + Fore.RESET)
        sleep(Sleep_time)

def Start_Alarm(Buzzer_Pin: int, Led_Pin: int, Sleep_Time: float):
    global stop_alarm, buzzer, led, console
    stop_alarm = False
    buzzer = threading.Thread(target=Buzzer, args=(Buzzer_Pin,))
    led = threading.Thread(target=Led, args=(Led_Pin,))
    console = threading.Thread(target=Console, args=(Sleep_Time,))
    buzzer.start()
    led.start()
    console.start()

def Stop_Alarm():
    global stop_alarm, buzzer, led, console
    stop_alarm = True
    buzzer.join()
    led.join()
    console.join()
    print(Fore.GREEN + "Stopped the Alarm!" + Fore.RESET)