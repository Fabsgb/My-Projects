from gpiozero import LED
from time import sleep

wave_periode = input("Enter the wave periode in seconds (float): ")
pin1 = input("Enter the firts pin (int): ")
pin2 = input("Enter the second pin (int): ")
try:
    wave_periode = float(wave_periode)
    pin1 = int(pin1)
    pin2 = int(pin2)
except ValueError:
    raise ValueError("Please enter valid numbers! Exiting!")
    exit()


pin_one = LED(pin1)
pin_two = LED(pin2)

try:
    while True:
        pin_one.on()
        sleep(wave_periode/2)
        pin_one.off()
        pin_two.on()
        sleep(wave_periode/2)
        pin_two.off()
except KeyboardInterrupt:
    print("Programm stoped by User!")