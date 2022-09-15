import serial


COM = 'COM6' #puerto com del duino bot, en windows
#COM = '/dev/nombre' #en linux, se obtiene el nombre del dispositivo con el comando dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1
arduinoSerial = serial.Serial(COM,9600)
arduinoSerial.close()
if(not(arduinoSerial.isOpen())): #si el puerto está cerrado, lo abre
    arduinoSerial.open()

#arduinoSerial.open()
#arduinoSerial.close()
arduinoSerial.write("a".encode())
vel_izq = 30
vel_der = -34
while True:
#     #print(arduinoSerial.readline().strip()) #leyendo del arduino
#     arduinoSerial.write("a".encode())
#for i in range(0,4):
    aux_izq = "i"+str(vel_izq)
    aux_der = "d"+str(vel_der)
    arduinoSerial.write("d".encode())
    #arduinoSerial.write(aux_izq.encode('utf-8')) #Le dice a la otra placa que velocidad debe tomar
    #arduinoSerial.write(aux_der.encode())     
    #a = arduinoSerial.readline().strip()
    #print(a)

arduinoSerial.close()