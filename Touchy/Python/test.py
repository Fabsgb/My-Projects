import alarm
from gpiozero import Button
from waiting import wait

button = Button(4)

try:
    while True:
        wait(lambda: not button.is_active)
        alarm.Start_Alarm(3, 0.5, 2, 0.66, 0.25)
        wait(lambda: button.is_active)
        alarm.Stop_Alarm()
except KeyboardInterrupt:
    alarm.Stop_Alarm()