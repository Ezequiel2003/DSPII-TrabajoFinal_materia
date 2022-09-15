#include <DCMotor.h>

DCMotor mot_izq(M0_EN, M0_D0, M0_D1);
DCMotor mot_der(M1_EN, M1_D0, M1_D1);

String lectura;
int vel = 0;
void setup(){
  Serial.begin(9600);
  mot_izq.brake();
  mot_der.brake();
}

void loop(){
  if(Serial.available()){
    //Serial.println(Serial.read());
    //char lectura = Serial.read();
    
    int izq = Serial.readStringUntil(',').toInt();
    mot_izq.setSpeed(izq);
    Serial.print(izq);
    
    int der = Serial.readStringUntil('\n').toInt();
    Serial.print(",");
    Serial.println(der);
    mot_der.setSpeed(der);
    

    Serial.flush();
  }  
}




