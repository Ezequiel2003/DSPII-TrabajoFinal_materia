import cv2
import numpy as np
from RC_lib import encontrar_bordes
import serial
import RPi.GPIO as GPIO
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
#fourcc = cv2.VideoWriter_fourcc(*'DIVX') 
#out = cv2.VideoWriter('Seguidor_90.avi',fourcc, 30, (640,480))
#---------- configuración texto en imagen
font = cv2.FONT_HERSHEY_SIMPLEX
position = (0,100)
position2 = (0,150)
position3 = (0,50)
fontScale = 1
fontColor = (255,255,0)
thick = 3
#----------
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

pausa = 1
vel_izq = 0
vel_der = 0
brusco_izq = 0
brusco_der = 0
curva_90_izq = 0
curva_90_der = 0
ancho_aprox = 200 #con valores medidos respecto a las distancias de los bordes, ancho de la línea

alto = 480
ancho = 640
        
pts1 = np.float32([[0,alto-100], [ancho-640,alto-350], [ancho-0, alto-350], [ancho,alto-100]]) #puntos de la imagen de entrada
#pts1 = np.float32([[10,alto-100], [ancho-630,alto-380], [ancho-10, alto-380], [ancho-10,alto-100]]) #puntos de la imagen de entrada
pts2 = np.float32([[0,alto], [0,0], [ancho,0], [ancho,alto]]) #puntos de la imagen de salida, deben tener coherencia con los puntos elegidos en la imagen de entrada
M = cv2.getPerspectiveTransform(pts1, pts2) #matriz 3x3 con la transformación

def motores(izq,der):
    #motor izquierda
    if(izq >= 0): #velocidades positivas
        GPIO.output(MOT_A1,True)
        GPIO.output(MOT_A2,False)
        pwm_a.ChangeDutyCycle(izq)
    
    if(izq < 0): #velocidades negativas
        GPIO.output(MOT_A1,False)
        GPIO.output(MOT_A2,True)
        pwm_a.ChangeDutyCycle(abs(izq))
        
    #motor derecha
    if(der >= 0): #velocidades positivas
        GPIO.output(MOT_B1,True)
        GPIO.output(MOT_B2,False)
        pwm_b.ChangeDutyCycle(der)
    
    if(der < 0): #velocidades negativas
        GPIO.output(MOT_B1,False)
        GPIO.output(MOT_B2,True)
        pwm_b.ChangeDutyCycle(abs(der))

def seguidor_lineas():
    global vel_izq,vel_der,brusco_izq,brusco_der
    vel_izq_ant = vel_izq
    vel_der_ant = vel_der
    
    if(not curva_90_izq and not curva_90_der):
    
        if(cont_izq == 1 and cont_der == 1 and not brusco_der and not brusco_izq): #si están dentro de la línea negra
            vel_izq = 25 - int((dist_izq-dist_der)*0.02)
            vel_der = 25 - int((dist_der-dist_izq)*0.02)
        
        #elif(cont_izq == 0 and cont_der == 1 and dist_der < ancho_aprox):#si se pasó del borde izquierdo
        elif(cont_izq == 0 and cont_der == 1):#si se pasó del borde izquierdo
            vel_izq = 15 + int(dist_der*0.01)
            vel_der = -5 - int(dist_der*0.01)
            brusco_izq = 1
            
        #elif(cont_izq == 1 and cont_der == 0 and dist_izq < ancho_aprox):#si se pasó del borde derecho
        elif(cont_izq == 1 and cont_der == 0):#si se pasó del borde derecho
            vel_izq = -5 - int(dist_izq*0.01)
            vel_der = 15 + int(dist_izq*0.01)
            brusco_der = 1
        
        if(vel_der == 0 and vel_izq == 0): #para evitar los casos bordes, tomo el valor anterior
            vel_der = vel_der_ant
            vel_izq = vel_izq_ant
        #if(brusco and ((dist_izq > 35 and dist_der > 0 and ancho_aprox-dist_der > 35) or (dist_der > 35 and dist_izq > 0 and ancho_aprox-dist_izq > 35))):
        if(brusco_izq and cont_izq and cont_der): #cuando vuelve de pasar el borde izquierdo, disminuye la velocidad lentamente hasta que se acerca al centro de la linea
            #print("Brusco izquierdo")
            vel_izq = 15 - int((dist_izq)*0.3)
            vel_der = -5 + int((dist_izq)*0.3)    
            if(dist_izq >= 50):
                brusco_izq = 0
        
        elif(brusco_der and cont_izq and cont_der): #cuando vuelve de pasar el borde derecho, disminuye la velocidad lentamente hasta que se acerca al centro de la linea
            #print("Brusco izquierdo")
            vel_izq = -5 + int((dist_der)*0.3)
            vel_der = 15 - int((dist_der)*0.3)    
            if(dist_der >= 50):
                brusco_der = 0        
            

def curvas_90():
    global curva_90_izq,curva_90_der,vel_izq,vel_der
    #if(cont_izq and not cont_der and cont_adelante and dist_adelante <= 170 and not curva_90_der): #detecta una curva a 90 grados a la derecha
    #if(dist_der >= ancho_aprox and dist_izq < ancho_aprox and dist_adelante <= ancho_aprox and not curva_90_der): #detecta una curva a 90 grados a la derecha
    if(dist_der >= ancho_aprox and dist_izq < ancho_aprox and not curva_90_der): #detecta una curva a 90 grados a la derecha
        print("Se detecto una curva de 90 grados a la derecha")
        curva_90_der = 1
        motores(0,0)
        #time.sleep(3)
            
    #if(not cont_izq and cont_der and cont_adelante and dist_adelante <= 170 and not curva_90_izq): #detecta una curva a 90 grados a la derecha
    #elif(dist_izq >= ancho_aprox and dist_der < ancho_aprox and dist_adelante <= ancho_aprox and not curva_90_izq): #detecta una curva a 90 grados a la derecha
    elif(dist_izq >= ancho_aprox and dist_der < ancho_aprox and not curva_90_izq): #detecta una curva a 90 grados a la derecha        curva_90_izq = 1
        print("Se detecto una curva de 90 grados a la izquierda")
        curva_90_izq = 1
        motores(0,0)
        #time.sleep(3)
            
    if(curva_90_der):
        print("girando derecha")
        vel_izq = 15
        vel_der = -10
        #motores(20,-20)
        if(cont_izq and cont_der and dist_adelante >= ancho_aprox): #si se encuentra en el medio de la linea luego de girar
            curva_90_der = 0
            brusco = 1
    
    elif(curva_90_izq):
        print("girando izquierda")
        vel_izq = -10
        vel_der = 15
        #motores(-20,20)
        if(cont_izq and cont_der and dist_adelante >= ancho_aprox): #si se encuentra en el medio de la linea luego de girar
            curva_90_izq = 0
            brusco = 1


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True: 
        imagen_final,bordes,thresh = encontrar_bordes(frame,"binv","ext","r",5,105) #buscar bordes
        
        cv2.line(imagen_final, (int(ancho/2),int(alto/2)-20),(int(ancho/2),int(alto/2)+20),(0,255,0),thickness=5) #dibujar la linea verde en el centro de la imagen
                        
        dist_izq = 0 #distancia al borde izquierdo de la línea
        dist_der = 0 #distancia al borde derecho de la línea
        dist_adelante = 0
        cont_izq = 0
        cont_der = 0
        cont_adelante = 0
                
        for i in range(0,int(ancho/2)-1):
            
            if(imagen_final[int(alto/2)-1,int(ancho/2)-1-i , 2] == 255 and cont_izq == 0 and imagen_final[int(alto/2)-1,int(ancho/2)-1-i, 0:1] == 0): #este contador es para que detecte una sola línea
                dist_izq = i
                cont_izq += 1
            if(imagen_final[int(alto/2)-1,int(ancho/2)-1+i , 2] == 255 and cont_der == 0 and imagen_final[int(alto/2)-1,int(ancho/2)-1+i, 0:1] == 0):
                dist_der = i
                cont_der += 1
            if(i < int(alto/2) and imagen_final[int(alto/2)-1-i,int(ancho/2)-1 , 2] == 255 and cont_adelante == 0 and imagen_final[int(alto/2)-1-i,int(ancho/2)-1, 0:1] == 0):
                dist_adelante = i
                cont_adelante += 1
                
        #con el for, recorro la mitad de la imagen en todo el ancho, y busco aquellos 
        #puntos que estén en rojo, esto significa que son los bordes, de ahí sacar la distancia, similar para adelante
        
        curvas_90()
        seguidor_lineas()
                
        #print("dist_izq:",dist_izq)
        #print("dist_der:",dist_der)
        #print("dist_adelante:",dist_adelante)
        #print("vel_izq:",vel_izq)
        #print("vel_der:",vel_der)
        #print("thresh:",thresh)
        #print("\n")
        tecla = cv2.waitKey(1)
        
        if tecla == ord('q'): #terminar de ejecutar
            motores(0,0)
            break
        
        elif tecla == ord('p'): #si se presiona la letra 'p' en el teclado, se pone en pausa o reanuda
            pausa = not pausa
            print("pausa:",pausa)
            
        elif(pausa):
            motores(0,0)
            cv2.putText(imagen_final,'Pausa',position3,font,fontScale,fontColor,thick)
        else:
            cv2.putText(imagen_final,'Avanzar',position3,font,fontScale,fontColor,thick)
            cv2.putText(imagen_final,'Der:'+str(vel_der),position2,font,fontScale,fontColor,thick)
            cv2.putText(imagen_final,'Izq:'+str(vel_izq),position,font,fontScale,fontColor,thick)
            motores(vel_izq,vel_der)
        #out.write(imagen_final)
        #cv2.imshow('Bordes y perspectiva', cv2.hconcat([imagen_final, img_perspectiva])) #muestra las imágenes juntas
        cv2.imshow('Bordes', imagen_final) #muestra las imágenes juntas        
    else:
        break
 
#Libera todo si la tarea ha terminado
cap.release()
#out.release()
cv2.destroyAllWindows() 
pwm_a.stop()
pwm_b.stop()
GPIO.cleanup()