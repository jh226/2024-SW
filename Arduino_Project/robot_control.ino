#include <SoftwareSerial.h>
SoftwareSerial mySerial(2, 3); // RX, TX

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  mySerial.begin(115200); // for robot  
  pinMode(A2,INPUT);
  pinMode(9,OUTPUT);
  Serial.println("Program Started");

}
void sendPacketMRTEXE(unsigned char exeIndex){
  unsigned char exeCmd[15] = {0xff, 0xff, 0x4c, 0x53, 0x00, 
                              0x00, 0x00, 0x00, 0x30, 0x0c, 0x03, // 0x0c=동작 실행 명령 0x03=파라메타수 
                              0x01, 0x00, 100, 0x00};             // Index 01 명령어 샘플
/*                             |      |    |    `---Check sum
                               |      |    `--------속도      파라1
                               |      `-------------지연시간  파라2
                               `--------------------Index    파라3
*/
  exeCmd[11] = exeIndex;
  exeCmd[14] = 0x00;    // checksum
    
  for (int i=6;i<14;i++){
    exeCmd[14]+=exeCmd[i];    
  }
  mySerial.write(exeCmd,15);   
}
void loop() {
  // put your main code here, to run repeatedly:
  int cdsVal = 0;
  while(1)
  {
    cdsVal = analogRead(A2);
    Serial.println(cdsVal);
    if (cdsVal < 600){
      digitalWrite(9,HIGH);
      sendPacketMRTEXE(22);
      delay(7000);
      sendPacketMRTEXE(1);
      delay(7000);
    }
    else{
      digitalWrite(9,LOW);
    }
    delay(50);
    
  }
}
