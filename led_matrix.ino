#include <Adafruit_NeoPixel.h>
#include <stdint.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

//핀 설정
#define R_LED 3
#define Y_LED 4
#define G_LED 5
#define MatrixPin  6

#define MAT_LED_COUNT  64 // 매트릭스 LED 수
#define BRIGHTNESS 15 // Set BRIGHTNESS to about 1/5 (max = 255)

Adafruit_NeoPixel pixels(MAT_LED_COUNT, MatrixPin, NEO_GRB + NEO_KHZ800);

///매트릭스 10의 자리 숫자 설정
const char lnum[2][22]{
  {2,10,18,26,34,42,50,9,16,56,57,58,59,2,2,2,2,2,2,2,2,2},   //1
  {0,1,2,3,11,19,24,25,26,27,32,40,48,56,57,58,59,2,2,2,2}    //2
};

//매트릭스 1의 자리 숫자 설정
const char rnum[10][22] ={
  {4,5,6,7,12,15,20,23,28,30,31,36,37,39,44,47,52,55,60,61,62,63},  //0
  {6,13,20,14,22,30,38,46,54,60,61,62,63,6,6,6,6,6,6,6,6,6},        //1
  {4,5,6,7,15,23,31,30,29,28,36,44,52,60,61,62,63,6,6,6,6,6},       //2
  {4,5,6,7,15,23,31,30,29,28,39,47,55,60,61,62,63,6,6,6,6,6},       //3
  {4,12,20,28,29,30,31,7,15,23,39,47,55,63,7,7,7,7,7,7,7,7},        //4
  {4,5,6,7,12,20,28,29,30,31,39,47,55,60,61,62,63,6,6,6,6,6},       //5
  {4,5,6,7,12,20,28,29,30,31,39,47,55,36,44,52,60,61,62,63,6,6},    //6
  {4,5,6,7,15,23,31,39,47,55,63,6,6,6,6,6,6,6,6,6,6,6},             //7
  {4,5,6,7,12,15,20,23,28,29,30,31,36,39,44,47,52,55,60,61,62,63},  //8
  {4,5,6,7,12,15,20,23,28,29,30,31,39,47,55,60,61,62,63,6,6,6}      //9
};

//우회전 표시
const char rArrow[18]={30,38,21,29,37,45,12,20,28,36,44,52,27,35,26,34,25,33};

//매트릭스 색상 설정
const uint32_t green = pixels.Color(0, 255, 0);

//신호등 모듈 설정
bool isRed = false; //적신호, 청신호 결정
bool rightTurnEnabled = false; //우회전 가능 여부
unsigned long prevMillis = 0;
const int redInterval = 10000; //적신호 지속 시간, 1000 = 1초
const int greenInterval = 20000; //청신호 지속 시간, 1000 = 1초
const int blinkStart = 4000; //깜빡임 시작 시간, 1000 = 1초

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

  //시리얼 통신 설정
  Serial.begin(9600);
  Serial.setTimeout(50);
  //신호등 출력 설정
  pinMode(R_LED, OUTPUT); pinMode(Y_LED, OUTPUT); pinMode(G_LED, OUTPUT);

  //매트릭스 설정
  pixels.begin();           // INITIALIZE NeoPixel pixels object (REQUIRED)
  pixels.show();            // Turn OFF all pixels ASAP
  pixels.setBrightness(BRIGHTNESS);

  //pinMode(LED_BUILTIN, OUTPUT); //테스트용
}



void loop() {
  unsigned long curMillis = millis();
  int curInterval = curMillis - prevMillis;

  //빨간불
  if(isRed && curInterval <= redInterval){
    digitalWrite(R_LED, HIGH);
    digitalWrite(G_LED, LOW);
    
    if(rightTurnEnabled){ //우회전 가능하면 우회전 표시
      showRightArrow(green);
    }
    else lightoff();
  }
  //R -> G 신호 변경
  else if(isRed && curInterval > redInterval){
    prevMillis = curMillis;
    isRed = false;
    lightoff();
  }
  //초록불
  else if(!isRed && curInterval <= greenInterval && curInterval < blinkStart){
    digitalWrite(G_LED, HIGH);
    digitalWrite(R_LED, LOW);

    if(rightTurnEnabled){ //우회전 가능하면 우회전 표시
      showRightArrow(green);
    }
  }
  //초록불 깜빡임
  else if(!isRed && curInterval <= greenInterval && curInterval > blinkStart){
    digitalWrite(G_LED, ((greenInterval - curInterval)%1000 < 500) ? HIGH : LOW);
    digitalWrite(R_LED, LOW );

    //우회전 가능하면 0.5초 간격으로 우회전 표시
    if(rightTurnEnabled && (greenInterval - curInterval)%1000 < 500){
      showCount(green, (greenInterval - curInterval)/1000);{} //카운터 출력
    }
    else if(rightTurnEnabled && (greenInterval - curInterval)%1000 >= 500){ 
      showRightArrow(green);
    }
    //우회전 불가능 시 카운터만 출력
    else{
      showCount(green, (greenInterval - curInterval)/1000);{} //카운터 출력
    }
  }
  //G -> R 신호 변경
  else if(!isRed && curInterval > greenInterval){
    prevMillis = curMillis;
    isRed = true;
    lightoff();
  }
}

//시리얼 통신 인터럽트
void serialEvent(void)
{
  char read_data;
  read_data = Serial.read();
     
  if(read_data == '1') {
    rightTurnEnabled = true;
    //digitalWrite(LED_BUILTIN, HIGH);//테스트용
  }
  else if(read_data == '0') {
    rightTurnEnabled = false;
    //digitalWrite(LED_BUILTIN, LOW);//테스트용
  }
}


//매트릭스 초기화
void lightoff(){
  for(int i=0; i<pixels.numPixels(); i++) { // For each pixel in pixels...
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
  }
  pixels.show();
}

//매트릭스 숫자 표기 (2 자리 수)
void showCount(uint32_t color, int num){
  for(int i=0; i<pixels.numPixels(); i++) { // For each pixel in pixels...
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
  }
    for(int i = 0; (i < 22) && (num/10 > 0); i++){
    pixels.setPixelColor(lnum[(num/10)-1][i], color);
  }
    for(int i = 0; i < 22; i++){
    pixels.setPixelColor(rnum[num%10][i], color);
  }
  pixels.show();
}

//매트릭스 우회전 표시
void showRightArrow(uint32_t color){
  for(int i=0; i<pixels.numPixels(); i++) { // For each pixel in pixels...
    pixels.setPixelColor(i, pixels.Color(0, 0, 0));
  }
  for(int i = 0; i < 18; i++){
    pixels.setPixelColor(rArrow[i], color);
  }  
  pixels.show();      
}




