
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 
#define SCREEN_HEIGHT 32 

#define OLED_RESET     4  
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);  


int Volume = A0;
int Button = 9;
int LED_R = A1;
int LED_G = 10;
int LED_B = 11;

int ex_arr[10];
int player1[10];
int player2[10];
int mode = 0;


void setup() {
  Serial.begin(9600);

  randomSeed(analogRead(2));

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();

  pinMode(Volume,INPUT);
  pinMode(Button,INPUT);
  pinMode(LED_R,OUTPUT);
  pinMode(LED_G,OUTPUT);
  pinMode(LED_B,OUTPUT);
}

void loop() {
  // 게임 시작
  PrintLED("     Start Game? \n    Press Button");
  wait_input();

  delay(1000);

  // 모드 선택
  while(true){
    int value = analogRead(A0) +1;    

    if(value < (1024*0.5)){
      PrintLED("[MODE]\nEasy    <<<<<\nHard");
      mode = 1;
    }
    else{
      PrintLED("[MODE]\nEasy\nHard    <<<<<");
      mode = 2;
    }

    if(digitalRead(Button)==HIGH){
      break;
    }

  }
  if(mode == 1){
    PrintLED("Start Easy Mode");
  }
  else if(mode == 2){
    PrintLED("Start Hard Mode");
  }
  
  delay(1000);

  Led_control(true);
  Led_control(false);

  //게임 진행 시작
  while(true){
    PrintLED("Start!");
    delay(1000);

    Play_example(mode);
    Led_control(true);

    while(true){
      PrintLED("Press Botton for \nStart Player1");
      
      wait_input();
      
      for(int i=0; i<10; i++){
        player1[i] = Vol_Led(1, i);
      }

      PrintLED("Press Botton for \nStart Player2");

      wait_input();

      PrintLED("Player 2's Turn\nPress Button for Done");
      for(int i=0; i<10; i++){
        player2[i] = Vol_Led(2, i);
      }        

      PrintLED("Finish!");
      delay(2000);

      cal_winner();

      wait_input();

      break;
    }
    break;
  }

  PrintLED("Loading...");
  delay(2000);
}

void PrintLED(char Array[]){
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,5);
  display.println(Array);
  display.display();
}

void Led_control(bool status){
  digitalWrite(LED_R,status);
  digitalWrite(LED_G,status);
  digitalWrite(LED_B,status);
}

int Vol_Led(int player, int num){
  int choice = 0;
  unsigned long startTime = millis();
   while(millis() - startTime < 1500){
    int value = analogRead(A0) +1;
    choice = 0;

    if(value > (1023*0.6) && value <= 1023){
      Led_control(false);
      digitalWrite(LED_R,true);
      choice = 1;
    }
    else if(value > (1023*0.3) && value <= (1023*0.6)){
      Led_control(false);
      digitalWrite(LED_G,true);
      choice = 2;
    }
    else if(value <= (1023*0.3)){
      Led_control(false);
      digitalWrite(LED_B,true);
      choice = 3;
    }

    char str[50];
    sprintf(str, "Player %d's Turn\n %d choice : %d", player, num+1, choice);
    PrintLED(str);
  }
  return choice;
}

void Play_example(int mode){
  int pre_rand;
  int rand;

  int delay_t1;
  int delay_t2;

  if(mode == 1){
    delay_t1 = 500;
    delay_t2 = 700;
  }
  else if(mode == 2){
    delay_t1 = 300;
    delay_t2 = 500;
  }

  PrintLED("Remember the Lighting Order");
  delay(500);

  for(int i=0; i<10; i++){
    rand = random(3)+1;

    switch(rand){
      case(1):{ Led_control(false); delay(delay_t1); digitalWrite(LED_R,true); delay(delay_t2); break; }
      case(2):{ Led_control(false); delay(delay_t1); digitalWrite(LED_G,true); delay(delay_t2); break; }
      case(3):{ Led_control(false); delay(delay_t1); digitalWrite(LED_B,true); delay(delay_t2); break; }
    }

    ex_arr[i] = rand;
    pre_rand = rand;
  }
}

void cal_winner(){
  int score1 = 0;
  int score2 = 0;

  for(int i=0; i<10; i++){
    if(ex_arr[i] == player1[i]){
      score1 += 1;
    }
    else if(ex_arr[i] == player2[i]){
      score2 += 1;
    }
  }

  char str[50];
  if(score1 > score2){
    sprintf(str, "Player1 Win \n[score] %d vs %d",score1, score2);
    PrintLED(str);
  }
  else if(score1 < score2){
    sprintf(str, "Player2 Win \n[score] %d vs %d",score1, score2);
    PrintLED(str);
  }
  else if(score1 == score2){
    sprintf(str, "Draw \n[score] %d vs %d",score1, score2);
    PrintLED(str);
  }
}

void wait_input(){
  while(true){
    if(digitalRead(Button)==HIGH){
      break;
    }
  }
}