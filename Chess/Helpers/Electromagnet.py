import RPi.GPIO as GPIO
import time

class Electromagnet:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def activate(self):
        """Turns on the electromagnet"""
        GPIO.output(self.pin, GPIO.HIGH)

    def deactivate(self):
        """Turns off the electromagnet"""
        GPIO.output(self.pin, GPIO.LOW)
