import gpiozero
from threading import Thread
from time import sleep
from colorama import Fore

stop_alarm = False
led_thread = None
buzzer_thread = None
console_thread = None
led = None
buzzer = None

def Led(led_obj, Led_Sleep):
    global stop_alarm
    while not stop_alarm:
        led_obj.on()
        sleep(Led_Sleep)
        led_obj.off()
        sleep(Led_Sleep)
    led_obj.off()

def Buzzer(buzzer_obj, Buzzer_Sleep):
    global stop_alarm
    while not stop_alarm:
        buzzer_obj.on()
        sleep(Buzzer_Sleep)
        buzzer_obj.off()
        sleep(Buzzer_Sleep)
    buzzer_obj.off()

def Console(Sleep_time):
    global stop_alarm
    while not stop_alarm:
        print(Fore.RED + "ALARM!" + Fore.RESET)
        sleep(Sleep_time)

def Start_Alarm(Buzzer_Pin: int, Buzzer_Sleep: float, Led_Pin: int, Led_Sleep: float, Console_Sleep: float):
    global stop_alarm, buzzer_thread, led_thread, console_thread, led, buzzer
    stop_alarm = False
    led = gpiozero.LED(Led_Pin)
    buzzer = gpiozero.Buzzer(Buzzer_Pin)
    buzzer_thread = Thread(target=Buzzer, args=(buzzer, Buzzer_Sleep))
    led_thread = Thread(target=Led, args=(led, Led_Sleep))
    console_thread = Thread(target=Console, args=(Console_Sleep,))
    buzzer_thread.start()
    led_thread.start()
    console_thread.start()

def Stop_Alarm():
    global stop_alarm, led, buzzer
    stop_alarm = True
    if buzzer_thread: buzzer_thread.join()
    if led_thread: led_thread.join()
    if console_thread: console_thread.join()
    if led:
        led.close()
        led = None
    if buzzer:
        buzzer.close()
        buzzer = None
    print(Fore.GREEN + "Stopped the Alarm!" + Fore.RESET)