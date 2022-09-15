import cv2
import numpy as np
from RC_lib import encontrar_bordes
import serial


#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
#fourcc = cv2.VideoWriter_fourcc(*'DIVX') 
#out = cv2.VideoWriter('output.avi',fourcc, 30.0, (1280,480))
#---------- configuración texto en imagen
font = cv2.FONT_HERSHEY_SIMPLEX
position = (0,100)
position2 = (0,150)
position3 = (0,50)
fontScale = 1
fontColor = (255,255,0)
thick = 3
#----------

#---------configuración comunicación serie con el Arduino
#COM = 'COM6' #puerto com del duino bot, en windows
#COM = '/dev/ttyACM0' #en linux, se obtiene el nombre del dispositivo con el comando dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1
#arduinoSerial = serial.Serial(COM,9600)
#if(not(arduinoSerial.isOpen())): #si el puerto está cerrado, lo abre
#    arduinoSerial.open()

#arduinoSerial.reset_input_buffer()
#arduinoSerial.flushOutput()
pausa = 1
vel_izq = 0
vel_der = 0

#arduinoSerial.write("i0".encode()) #Le dice a la otra placa que se debe apagar
#arduinoSerial.write("d0".encode()) #Le dice a la otra placa que se debe apagar
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True: 
        imagen_final,bordes = encontrar_bordes(frame,"binv","ext","r",5) #buscar bordes
        alto,ancho = imagen_final.shape[:2]
        
        #pts1 = np.float32([[0,alto-100], [ancho-600,alto-350], [ancho-40, alto-350], [ancho,alto-100]]) #puntos de la imagen de entrada
        pts1 = np.float32([[0,alto-100], [ancho-640,alto-350], [ancho-0, alto-350], [ancho,alto-100]]) #puntos de la imagen de entrada
        pts2 = np.float32([[0,alto], [0,0], [ancho,0], [ancho,alto]]) #puntos de la imagen de salida, deben tener coherencia con los puntos elegidos en la imagen de entrada
        M = cv2.getPerspectiveTransform(pts1, pts2) #matriz 3x3 con la transformación
        img_perspectiva = cv2.warpPerspective(imagen_final, M, (ancho,alto)) #aplicar la matriz de transformación a la imagen original
        
        #cv2.line(imagen_final, (0,alto-100), (ancho-600,alto-350), (255,0,0),thickness = 5) #linea izquierda
        cv2.line(imagen_final, (0,alto-100), (ancho-640,alto-350), (255,0,0),thickness = 5) #linea izquierda
        cv2.line(imagen_final, (0,alto-100), (ancho,alto-100), (255,0,0),thickness = 5) #linea inferior
        #cv2.line(imagen_final, (ancho,alto-100), (ancho-40,alto-350), (255,0,0),thickness = 5) #linea derecha
        cv2.line(imagen_final, (ancho,alto-100), (ancho-0,alto-350), (255,0,0),thickness = 5) #linea derecha
        #cv2.line(imagen_final, (ancho-600,alto-350), (ancho-40,alto-350), (255,0,0),thickness = 5) #linea superior
        cv2.line(imagen_final, (ancho-640,alto-350), (ancho-00,alto-350), (255,0,0),thickness = 5) #linea superior
        
        #cv2.imshow('bordes',imagen_final)
        #cv2.imshow('perspectiva',img_perspectiva)
        
        cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)-20),(int(ancho/2),int(alto/2)+20),(0,255,0),thickness=5)
        #cv2.imwrite('perspectiva.png', img_perspectiva)
                
        dist_izq = 0 #distancia al borde izquierdo de la línea
        dist_der = 0 #distancia al borde derecho de la línea
        cont_izq = 0
        cont_der = 0
        
        
        ancho_aprox = 95+112 #con valores medidos respecto a las distancias de los bordes, ancho de la línea
        for i in range(0,int(ancho/2)-1):
            
            if(img_perspectiva[int(alto/2)-1,int(ancho/2)-1-i , 2] == 255 and cont_izq == 0 and img_perspectiva[int(alto/2)-1,int(ancho/2)-1-i, 0:1] == 0): #este contador es para que detecte una sola línea
                dist_izq = i
                cont_izq +=1
            if(img_perspectiva[int(alto/2)-1,int(ancho/2)-1+i , 2] == 255 and cont_der == 0 and img_perspectiva[int(alto/2)-1,int(ancho/2)-1+i, 0:1] == 0):
                dist_der = i
                cont_der +=1
                
        #con el for, recorro la mitad de la imagen en todo el ancho, y busco aquellos 
        #puntos que estén en rojo, esto significa que son los bordes, de ahí sacar la distancia
        
        
        vel_izq_ant = vel_izq
        vel_der_ant = vel_der
        #cv2.imshow('perspectiva',img_perspectiva)
        #out.write(cv2.hconcat([imagen_final, img_perspectiva]))
        #cv2.imshow('Bordes y perspectiva', cv2.hconcat([imagen_final, img_perspectiva])) #muestra las imágenes juntas
        
        if(cont_izq == 1 and cont_der == 1): #si están dentro de la línea negra
            vel_izq = 37 - int((dist_izq-dist_der)*0.2)
            vel_der = 35 - int((dist_der-dist_izq)*0.2)
        
        elif(cont_izq == 0 and cont_der == 1 and dist_der < 140):#si se pasó del borde izquierdo
            vel_izq = 37 + int(dist_der*0.2)
            vel_der = -10 - int(dist_der*0.2)
            
        elif(cont_izq == 1 and cont_der == 0 and dist_izq < 140):#si se pasó del borde derecho
            vel_izq = -10 - int(dist_izq*0.2)
            vel_der = 37 + int(dist_izq*0.2) 
        
        if(vel_der == 0 and vel_izq == 0): #para evitar los casos bordes, tomo el valor anterior
            vel_der = vel_der_ant
            vel_izq = vel_izq_ant
        
        print("vel_izq:",vel_izq)
        print("vel_der:",vel_der)
        print("\n")
        tecla = cv2.waitKey(1)
        
        if tecla == ord('q'): #terminar de ejecutar
            velocidad = "0,0\n"
            #arduinoSerial.write(velocidad.encode('utf-8')) #Le dice a la otra placa que debe parar los motores
            break
        
        elif tecla == ord('p'): #si se presiona la letra 'p' en el teclado, se pone en pausa o reanuda
            pausa = not pausa
            print("pausa:",pausa)
            
        elif(pausa):
            #letra = "z"
            cv2.putText(img_perspectiva,'Pausa',position3,font,fontScale,fontColor,thick)
            velocidad = "0,0\n"
            #arduinoSerial.write(velocidad.encode('utf-8')) #Le dice a la otra placa que debe parar los motores
        
        else:
            #letra = "no z"
            velocidad = str(vel_izq) + "," + str(vel_der) + "\n"
            cv2.putText(img_perspectiva,'Avanzar',position3,font,fontScale,fontColor,thick)
            cv2.putText(img_perspectiva,'Der:'+str(vel_der),position2,font,fontScale,fontColor,thick)
            cv2.putText(img_perspectiva,'Izq:'+str(vel_izq),position,font,fontScale,fontColor,thick)
            
            #arduinoSerial.write(velocidad.encode('utf-8')) #Le dice a la otra placa que velocidad debe tomar
            ##arduinoSerial.write(aux_der.encode('utf-8')) #Le dice a la otra placa que velocidad debe tomar
            #a = #arduinoSerial.read_all().decode('utf-8')
            #print(a)
        cv2.imshow('Bordes y perspectiva', cv2.hconcat([imagen_final, img_perspectiva])) #muestra las imágenes juntas
    else:
        break
 
#Libera todo si la tarea ha terminado
cap.release()
#out.release()
cv2.destroyAllWindows() 
#arduinoSerial.close()

