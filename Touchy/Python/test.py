import alarm
from gpiozero import Button
from waiting import wait

button = Button(4)

while True:
    wait(lambda: not button.is_active)
    alarm.Start_Alarm(3, 2, 0.5)
    wait(lambda: button.is_active)
    alarm.Stop_Alarm()