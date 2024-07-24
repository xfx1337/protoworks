// settings
#define NUMBER_OF_SHIFT_CHIPS   2 // количество регистров
#define DATA_WIDTH NUMBER_OF_SHIFT_CHIPS * 8 // количество входов
#define PULSE_WIDTH_USEC   5 // задержка при считывании данных 
#define LONG_PRESS_TIME 500
#define PLAY_AT_BOOTUP 1

// pins
#define PIEZO_PIN 7
#define PLOAD_PIN 8
#define CE_PIN 9
#define DATA_PIN 11
#define CLOCK_PIN 12


int button_pressed_times[DATA_WIDTH];
int button_released_times[DATA_WIDTH];

#define BYTES_VAL_T unsigned long 

BYTES_VAL_T pinValues; // текущее значение пинов 
BYTES_VAL_T oldPinValues; // предыдущее значение пинов


BYTES_VAL_T read_shift_regs() {
    long bitVal;
    BYTES_VAL_T bytesVal = 0;
 
    // опрашиваем регистр о состоянии пинов
    digitalWrite(CE_PIN, HIGH);
    digitalWrite(PLOAD_PIN, LOW);
    delayMicroseconds(PULSE_WIDTH_USEC);
    digitalWrite(PLOAD_PIN, HIGH);
    digitalWrite(CE_PIN, LOW);
 
    // считываем полученные данные о пинах
    for(int i = 0; i < DATA_WIDTH; i++){
        bitVal = digitalRead(DATA_PIN);
        bytesVal |= (bitVal << ((DATA_WIDTH-1) - i));
        digitalWrite(CLOCK_PIN, HIGH);
        delayMicroseconds(PULSE_WIDTH_USEC);
        digitalWrite(CLOCK_PIN, LOW);
    }
     
    // возвращяем результат опроса регистра
    return(bytesVal);
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

// функция для вывода состояния пинов
void display_pin_values(){
    // перебор всех пинов 
    for(int i = 0; i < DATA_WIDTH; i++){
        Serial.print("  Button-");
        Serial.print(i);
        Serial.print(": ");
        if((pinValues >> i) & 1){
          Serial.print("ON");
        }else{
          Serial.print("OFF"); 
        }   
        Serial.println();
    }
    Serial.println();
}
 
void setup(){
    Serial.begin(115200);

    pinMode(PLOAD_PIN, OUTPUT);
    pinMode(CE_PIN, OUTPUT);
    pinMode(CLOCK_PIN, OUTPUT);
    pinMode(DATA_PIN, INPUT);
    digitalWrite(CLOCK_PIN, LOW);
    digitalWrite(PLOAD_PIN, HIGH);
 
    // считываем значения с пинов
    pinValues = read_shift_regs();
    oldPinValues = pinValues;
    if (PLAY_AT_BOOTUP) {
      tone(PIEZO_PIN, 600, 100);
    }
    Serial.println("boot up");
}

void loop(){
    pinValues = read_shift_regs();

    if(pinValues != oldPinValues){
      for (int i=0; i<DATA_WIDTH; i++) {
        if(((pinValues >> i) & 1) != ((oldPinValues >> i) & 1)) {
          if ((pinValues >> i) & 1) {
            button_pressed_times[i] = millis();
          }
          else {
            button_released_times[i] = millis();
          }
        }
      }
      
      for (int i=0; i<DATA_WIDTH; i++) {
        if ((button_released_times[i] - button_pressed_times[i] > LONG_PRESS_TIME) && (button_released_times[i] != 0)) {
          Serial.println("btn" + String(i) + " long pressed");
          button_released_times[i] = 0;
        }
        else if ((button_released_times[i] - button_pressed_times[i] <= LONG_PRESS_TIME) && (button_released_times[i] != 0)) {
          Serial.println("btn" + String(i) + " short pressed");
          button_released_times[i] = 0;
        } else {
        
        }
      }

        // сохраняем текущее значение
        oldPinValues = pinValues;
    }
    delay(50);

    if (Serial.available() > 0) {
        String input = Serial.readString();
        if (input.indexOf("tone") > -1) {
          int freq = getValue(input, ' ', 1).toInt();
          int time = getValue(input, ' ', 2).toInt();
          tone(PIEZO_PIN, freq, time);
          Serial.println("ok");
        }
        else if (input.indexOf("stop_tone") > -1) {
          noTone(PIEZO_PIN);
          Serial.println("ok");
        }

        else if (input.indexOf("indent_hub") > -1) {
          Serial.println("hub indent");
          Serial.println("ok");
        }

        else {
          Serial.println("invalid command");
        }
    }
}