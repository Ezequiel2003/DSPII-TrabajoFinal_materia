import RPi.GPIO as GPIO
import time

MOT_A1 = 17 #GPIO17 dir
MOT_A2 = 27 #GPIO27 dir
MOT_AE = 22 #GPIO22 enable

MOT_B1 = 25 #GPIO25 dir
MOT_B2 = 8  #GPIO8  dir
MOT_BE = 7  #GPIO7  enable

GPIO.setmode(GPIO.BCM) #le estamos indicando que el pin x que pondremos, será el que está etiquetado como GPIOx
GPIO.setup(MOT_A1,GPIO.OUT) #configurar de salida
GPIO.setup(MOT_A2,GPIO.OUT) #configurar de salida
GPIO.setup(MOT_AE,GPIO.OUT) #configurar de salida
GPIO.setup(MOT_B1,GPIO.OUT) #configurar de salida
GPIO.setup(MOT_B2,GPIO.OUT) #configurar de salida
GPIO.setup(MOT_BE,GPIO.OUT) #configurar de salida

#definir salidas pwm
pwm_a = GPIO.PWM(MOT_AE,100) # dividir en 100 trozos el segundo
pwm_b = GPIO.PWM(MOT_BE,100) # configuring Enable pin for PWM

#inicializar los enable con duty cycle de 0
pwm_a.start(0)
pwm_b.start(0)

def motores(vel_izq,vel_der):
    #motor izquierda
    if(vel_izq >= 0): #velocidades positivas
        GPIO.output(MOT_A1,True)
        GPIO.output(MOT_A2,False)
        pwm_a.ChangeDutyCycle(vel_izq)
    
    if(vel_izq < 0): #velocidades negativas
        GPIO.output(MOT_A1,False)
        GPIO.output(MOT_A2,True)
        pwm_a.ChangeDutyCycle(abs(vel_izq))
        
    #motor derecha
    if(vel_der > 0): #velocidades positivas
        GPIO.output(MOT_B1,True)
        GPIO.output(MOT_B2,False)
        pwm_b.ChangeDutyCycle(vel_der)
    
    if(vel_der < 0): #velocidades negativas
        GPIO.output(MOT_B1,False)
        GPIO.output(MOT_B2,True)
        pwm_b.ChangeDutyCycle(abs(vel_der))

while True:
    #avanzar a mitad del ciclo ambos
    motores(50,50)
    time.sleep(5)
    
    #retroceder ambos
    motores(-50,-50)
    time.sleep(5)
    
    #uno gira
    motores(50,-50)
    time.sleep(5)
    
    #el otro gira
    motores(-50,50)
    time.sleep(5)
    
    #ambos frenan
    motores(-50,50)
    time.sleep(5)
    break

pwm_a.stop()
pwm_b.stop()
GPIO.cleanup()