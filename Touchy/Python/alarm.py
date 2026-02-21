import gpiozero
from threading import Thread
from time import sleep
from colorama import Fore

stop_alarm = False
led_thread = None
buzzer_thread = None
console_thread = None

def Led(Led_Pin, Led_Sleep):
    led = gpiozero.LED(Led_Pin)
    global stop_alarm
    while not stop_alarm:
        led.on()
        sleep(Led_Sleep)
        led.off()
        sleep(Led_Sleep)
    led.off()

def Buzzer(Buzzer_Pin, Buzzer_Sleep):
    buzzer = gpiozero.Buzzer(Buzzer_Pin)
    global stop_alarm
    while not stop_alarm:
        buzzer.on()
        sleep(Buzzer_Sleep)
        buzzer.off()
        sleep(Buzzer_Sleep)
    buzzer.off()

def Console(Sleep_time):
    global stop_alarm
    while not stop_alarm:
        print(Fore.RED + "ALARM!" + Fore.RESET)
        sleep(Sleep_time)

def Start_Alarm(Buzzer_Pin: int, Buzzer_Sleep: float, Led_Pin: int, Led_Sleep: float, Console_Sleep: float):
    global stop_alarm, buzzer_thread, led_thread, console_thread
    stop_alarm = False
    buzzer_thread = Thread(target=Buzzer, args=(Buzzer_Pin, Buzzer_Sleep))
    led_thread = Thread(target=Led, args=(Led_Pin, Led_Sleep))
    console_thread = Thread(target=Console, args=(Console_Sleep,))
    buzzer_thread.start()
    led_thread.start()
    console_thread.start()

def Stop_Alarm():
    global stop_alarm
    stop_alarm = True
    if buzzer_thread: buzzer_thread.join()
    if led_thread: led_thread.join()
    if console_thread: console_thread.join()
    print(Fore.GREEN + "Stopped the Alarm!" + Fore.RESET)