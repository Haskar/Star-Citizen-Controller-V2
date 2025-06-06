#include <Joystick.h>
#include <Keyboard.h>

#define JOY1X A2
#define JOY1Y A3
#define JOY2X A1
#define JOY2Y A0
#define JOY3X A8
#define JOY3Y A9
#define JOYSTICK_COUNT 6
#define MAX_BUTTONS 120
#define PRIM_JOYSTICK 0
#define SEC_JOYSTICK 1
#define TER_JOYSTICK 2
#define DEBUG false
//Defining the Joystick
//The Joystick is defined in the following setup:
//Joystick(Joystick HID ID, Joystick Type, Button Count, Hat Switch Count, Include X, Include Y, Include Z, Include Rx, Include Ry, Include Rz, Include Rudder, Include Throttle, Include Accelerator, Include Brake, Include Steering
//Joystick HID ID: A Hex value identifier for HID Device Recognition (default: 0x03). DO NOT USE 0x01 or 0x02
//Joystick type: Define the type of joystick from the types supported. Types: DEFAULT Joystick (0x04 or JOYSTICK_TYPE_JOYSTICK), Gamepad (0x05 or JOYSTICK_TYPE_GAMEPAD), Multi-Axis Controller (0x08 or JOYSTICK_TYPE_MULTI_AXIS)
//Button Count: Number of Buttons shown to HID system (default: 32)
//Hat Switch Count: Number of Hat Switches, max 2. (default:2)
//Include X Axis: Determines whether the X axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Y Axis: Determines whether the Y axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Z Axis: Determines whether the Z axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Rx Axis: Determines whether the X Rotational axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Ry Axis: Determines whether the Y Rotational axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Rz Axis: Determines whether the Z Rotational axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Rudder: Determines whether a Rudder axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Throttle: Determines whether a Throttle axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Accelerator: Determines whether an Accelerator axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Brake: Determines whether a Brake axis is avalible for used by the HID system, defined as a bool value (default:true)
//Include Steering: Determines whether a Steering axis is avalible for used by the HID system, defined as a bool value (default:true)

Joystick_ Joystick[JOYSTICK_COUNT] = {
  Joystick_(0x11, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, true, true, false, false, false, false, false, false, false, false, false),
  Joystick_(0x12, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, true, true, false, false, false, false, false, false, false, false, false),
  Joystick_(0x13, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, true, true, false, false, false, false, false, false, false, false, false),
  Joystick_(0x14, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, false, false, false, false, false, false, false, false, false, false, false),
  Joystick_(0x15, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, false, false, false, false, false, false, false, false, false, false, false),
  Joystick_(0x16, JOYSTICK_TYPE_JOYSTICK, MAX_BUTTONS, 0, false, false, false, false, false, false, false, false, false, false, false)
};

const bool initAutoSendState = true;
bool acceleration_on = false;

int xAxisJ1_ = 0;
int yAxisJ1_ = 0;
int xAxisJ2_ = 0;
int yAxisJ2_ = 0;
int xAxisJ3_ = 0;
int yAxisJ3_ = 0;
int index = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); //Serial Connection to PC
  Serial1.begin(115200); //Serial Connection to Raspi
  Keyboard.begin();

  for (int index = 0; index < JOYSTICK_COUNT; index++)
  {
    delay(100);
    if (initAutoSendState)
    {
      Joystick[index].begin();
      for (int button_index = 0; button_index < MAX_BUTTONS; button_index++)
      { 
        Joystick[index].setButton(button_index, 0);
      }
    }
    else
    {
      Joystick[index].begin(false);
    }
  }

  if (acceleration_on == false)
  {
    Joystick[TER_JOYSTICK].setYAxis(128);
  }

  //Joystick.begin();
}

void loop() {

  // put your main code here, to run repeatedly:
  xAxisJ1_ = analogRead(JOY1X);
  xAxisJ1_ = map(xAxisJ1_,0,1023,256,0);
  Joystick[PRIM_JOYSTICK].setXAxis(xAxisJ1_);

  yAxisJ1_ = analogRead(JOY1Y);
  yAxisJ1_ = map(yAxisJ1_,0,1023,256,0);
  Joystick[PRIM_JOYSTICK].setYAxis(yAxisJ1_);

  xAxisJ2_ = analogRead(JOY2X);
  xAxisJ2_ = map(xAxisJ2_,0,1023,0,256);
  Joystick[SEC_JOYSTICK].setYAxis(xAxisJ2_);

  yAxisJ2_ = analogRead(JOY2Y);
  yAxisJ2_ = map(yAxisJ2_,0,1023,256,0);
  Joystick[SEC_JOYSTICK].setXAxis(yAxisJ2_);

  if (acceleration_on)
  {
    xAxisJ3_ = analogRead(JOY3X);
    xAxisJ3_ = map(xAxisJ3_,0,1023,0,128);
    Joystick[TER_JOYSTICK].setYAxis(xAxisJ3_);
  }

  yAxisJ3_ = analogRead(JOY3Y);
  yAxisJ3_ = map(yAxisJ3_,0,1023,0,128);
  Joystick[TER_JOYSTICK].setXAxis(yAxisJ3_);
  
  if (Serial.available()) // Check to see if at least one character is available
  {
    int integerValue_Serial = Serial.parseInt();
    int integerValue_Serial_Saved = integerValue_Serial;
    if (integerValue_Serial>0)
    {
      int joystick_number = 0;
      while (abs(integerValue_Serial)>MAX_BUTTONS)
      {
        joystick_number = joystick_number+1;
        if (integerValue_Serial > 0)
        {
          integerValue_Serial = integerValue_Serial-MAX_BUTTONS;
        }
        if (integerValue_Serial < 0)
        {
          integerValue_Serial = integerValue_Serial+MAX_BUTTONS;
        }
      }

      Joystick[joystick_number].setButton(integerValue_Serial-1, 1);
      delay(200);
      Joystick[joystick_number].setButton(integerValue_Serial-1, 0);
      if (DEBUG) { Serial.print("Joystick-Input from PC: Trigger: "); Serial.print(integerValue_Serial_Saved); Serial.print(" - Joystick: "); Serial.print(joystick_number); Serial.print(" - Button: "); Serial.print(integerValue_Serial); Serial.print(" - "); Serial.println("DONE"); }

      integerValue_Serial = -1;
    }
  }
  if (Serial1.available()) // Check to see if at least one character is available
  {
    int integerValue_Serial1_Saved = 0;
    int integerValue_Serial1 = Serial1.parseInt();
    integerValue_Serial1_Saved = integerValue_Serial1;

    if (integerValue_Serial1<=-1000 || integerValue_Serial1==0)
    {
      Keyboard.releaseAll(); 
      if (DEBUG) { Serial.print("Keyboard-Input from Raspi: "); Serial.print(integerValue_Serial1); Serial.println(" - Released all"); }
    }
    if (integerValue_Serial1<1000 && integerValue_Serial1>-1000)
    {
      int joystick_number = 0;
      while (abs(integerValue_Serial1)>MAX_BUTTONS)
      {
        joystick_number = joystick_number+1;
        if (integerValue_Serial1 > 0)
        {
          integerValue_Serial1 = integerValue_Serial1-MAX_BUTTONS;
        }
        if (integerValue_Serial1 < 0)
        {
          integerValue_Serial1 = integerValue_Serial1+MAX_BUTTONS;
        }
      }

      if (integerValue_Serial1 > 0)
      {
        Joystick[joystick_number].setButton(integerValue_Serial1-1, 1);
      }
      if (integerValue_Serial1 < 0)
      {
        Joystick[joystick_number].setButton((integerValue_Serial1*-1)-1, 0);
      }
      if (DEBUG) { Serial.print("Joystick-Input from Raspi: Trigger: "); Serial.print(integerValue_Serial1_Saved); Serial.print(" - Joystick: "); Serial.print(joystick_number); Serial.print(" - Button: "); Serial.print(integerValue_Serial1); Serial.print(" - "); Serial.println("DONE"); }
    }
    //Serial.println(integerValue);
    if (integerValue_Serial1>=1000 && integerValue_Serial1<1100)
    {
      if (DEBUG) { Serial.print("Keyboard-Input from Raspi: "); Serial.print(integerValue_Serial1); }
      while (Serial1.available() )
      {
        char inChar = (char)Serial1.read();
        inChar = (char)Serial1.read();
        switch (integerValue_Serial1) {
          case 1000: 
            if (DEBUG) { Serial.print(" - "); }
            break;
          case 1001: 
            if (DEBUG) { Serial.print(" - KEY_LEFT_CTRL+"); }
            Keyboard.press(KEY_LEFT_CTRL);
            break;
          case 1002: 
            if (DEBUG) { Serial.print(" - KEY_LEFT_SHIFT+"); }
            Keyboard.press(KEY_LEFT_SHIFT);
            break;
          case 1003: 
            if (DEBUG) { Serial.print(" - KEY_LEFT_ALT+"); }
            Keyboard.press(KEY_LEFT_ALT);
            break;
          case 1004: 
            if (DEBUG) { Serial.print(" - KEY_RIGHT_CTRL+"); }
            Keyboard.press(KEY_RIGHT_CTRL);
            break;
          case 1005: 
            if (DEBUG) { Serial.print(" - KEY_RIGHT_SHIFT+"); }
            Keyboard.press(KEY_RIGHT_SHIFT);
            break;
          case 1006: 
            if (DEBUG) { Serial.print(" - KEY_RIGHT_ALT+"); }
            Keyboard.press(KEY_RIGHT_ALT);
            break;
          case 1007: 
            if (DEBUG) { Serial.print(" - KEY_TAB+"); }
            Keyboard.press(KEY_TAB);
            break;
          case 1011: 
            if (DEBUG) { Serial.print(" - KEY_F1+"); }
            Keyboard.press(KEY_F1);
            break;
          case 1012: 
            if (DEBUG) { Serial.print(" - KEY_F2+"); }
            Keyboard.press(KEY_F2);
            break;
          case 1013: 
            if (DEBUG) { Serial.print(" - KEY_F3+"); }
            Keyboard.press(KEY_F3);
            break;
          case 1014: 
            if (DEBUG) { Serial.print(" - KEY_F4+"); }
            Keyboard.press(KEY_F4);
            break;
          case 1015: 
            if (DEBUG) { Serial.print(" - KEY_F5+"); }
            Keyboard.press(KEY_F5);
            break;
          case 1016: 
            if (DEBUG) { Serial.print(" - KEY_F6+"); }
            Keyboard.press(KEY_F6);
            break;
          case 1017: 
            if (DEBUG) { Serial.print(" - KEY_F7+"); }
            Keyboard.press(KEY_F7);
            break;
          case 1018: 
            if (DEBUG) { Serial.print(" - KEY_F8+"); }
            Keyboard.press(KEY_F8);
            break;
          case 1019: 
            if (DEBUG) { Serial.print(" - KEY_F9+"); }
            Keyboard.press(KEY_F9);
            break;
          case 1020: 
            if (DEBUG) { Serial.print(" - KEY_F10+"); }
            Keyboard.press(KEY_F10);
            break;
          case 1021: 
            if (DEBUG) { Serial.print(" - KEY_F11+"); }
            Keyboard.press(KEY_F11);
            break;
          case 1022: 
            if (DEBUG) { Serial.print(" - KEY_F12+"); }
            Keyboard.press(KEY_F12);
            break;
          case 1023: 
            if (DEBUG) { Serial.print(" - KEY_UP_ARROW+"); }
            Keyboard.press(KEY_UP_ARROW);
            break;
          case 1024: 
            if (DEBUG) { Serial.print(" - KEY_DOWN_ARROW+"); }
            Keyboard.press(KEY_DOWN_ARROW);
            break;
          case 1025: 
            if (DEBUG) { Serial.print(" - KEY_LEFT_ARROW+"); }
            Keyboard.press(KEY_LEFT_ARROW);
            break;
          case 1026: 
            if (DEBUG) { Serial.print(" - KEY_RIGHT_ARROW+"); }
            Keyboard.press(KEY_RIGHT_ARROW);
            break;
          case 1027: 
            if (DEBUG) { Serial.print(" - KEY_PAGE_UP+"); }
            Keyboard.press(KEY_PAGE_UP);
            break;
          case 1028: 
            if (DEBUG) { Serial.print(" - KEY_PAGE_DOWN+"); }
            Keyboard.press(KEY_PAGE_DOWN);
            break;
          case 1029: 
            if (DEBUG) { Serial.print(" - KEY_HOME+"); }
            Keyboard.press(KEY_HOME);
            break;
          case 1030: 
            if (DEBUG) { Serial.print(" - KEY_END+"); }
            Keyboard.press(KEY_END);
            break;
          case 1031: 
            if (DEBUG) { Serial.print(" - KEY_KP_1+"); }
            Keyboard.press(KEY_KP_1);
            break;
          case 1032:
            if (DEBUG) { Serial.print(" - KEY_KP_2+"); } 
            Keyboard.press(KEY_KP_2);
            break;
          case 1033: 
            if (DEBUG) { Serial.print(" - KEY_KP_3+"); }
            Keyboard.press(KEY_KP_3);
            break;
          case 1034: 
            if (DEBUG) { Serial.print(" - KEY_KP_4+"); }
            Keyboard.press(KEY_KP_4);
            break;
          case 1035: 
            if (DEBUG) { Serial.print(" - KEY_KP_5+"); }
            Keyboard.press(KEY_KP_5);
            break;
          case 1036: 
            if (DEBUG) { Serial.print(" - KEY_KP_6+"); }
            Keyboard.press(KEY_KP_6);
            break;
          case 1037: 
            if (DEBUG) { Serial.print(" - KEY_KP_7+"); }
            Keyboard.press(KEY_KP_7);
            break;
          case 1038: 
            if (DEBUG) { Serial.print(" - KEY_KP_8+"); }
            Keyboard.press(KEY_KP_8);
            break;
          case 1039: 
            if (DEBUG) { Serial.print(" - KEY_KP_9+"); }
            Keyboard.press(KEY_KP_9);
            break;
          case 1040: 
            if (DEBUG) { Serial.print(" - KEY_KP_0+"); }
            Keyboard.press(KEY_KP_0);
            break;
          case 1041: 
            if (DEBUG) { Serial.print(" - KEY_KP_MINUS+"); }
            Keyboard.press(KEY_KP_MINUS);
            break;
          case 1042: 
            if (DEBUG) { Serial.print(" - KEY_KP_PLUS+"); }
            Keyboard.press(KEY_KP_PLUS);
            break;
          case 1043: 
            if (DEBUG) { Serial.print(" - KEY_KP_ASTERISK+"); }
            Keyboard.press(KEY_KP_ASTERISK);
            break;
          default:
            break;
        }

        Keyboard.press(inChar);
        if (DEBUG) { Serial.print(inChar); Serial.print(" - "); Serial.println("DONE"); }
        //Keyboard.releaseAll(); 
      }
    }
    if (integerValue_Serial1>=1100 && integerValue_Serial1<1200)
    {
      if (DEBUG) { Serial.print("Keyboard-Input from Raspi: "); Serial.print(integerValue_Serial1); Serial.print(" - F4+"); }
      while (Serial1.available())
      {
        char inChar = (char)Serial1.read();
        inChar = (char)Serial1.read();
        switch (integerValue_Serial1) {
          case 1123:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_UP_ARROW);
            break;
          case 1124:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_DOWN_ARROW);
            break;
          case 1125:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_LEFT_ARROW);
            break;
          case 1126:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_RIGHT_ARROW);
            break;
          case 1127:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_PAGE_UP);
            break;
          case 1128:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_PAGE_DOWN);
            break;
          case 1129:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_HOME);
            break;
          case 1130:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_END);
            break;
          case 1131:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_1);
            break;
          case 1132:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_2);
            break;
          case 1133:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_3);
            break;
          case 1134:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_4);
            break;
          case 1135:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_5);
            break;
          case 1136:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_6);
            break;
          case 1137:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_7);
            break;
          case 1138:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_8);
            break;
          case 1139:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_9);
            break;
          case 1140:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_0);
            break;
          case 1141:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_MINUS);
            break;
          case 1142:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_PLUS);
            break;
          case 1143:  
            Keyboard.press(KEY_F4);
            Keyboard.press(KEY_KP_ASTERISK);
            break;
          default:
            break;
        }
        if (DEBUG) { Serial.println("DONE"); }
        //Keyboard.releaseAll(); 
      }
    }
    if (integerValue_Serial1>=2000 && integerValue_Serial1<3000)
    {
      if (DEBUG) { Serial.print("Keyboard-Input from Raspi: "); Serial.print(integerValue_Serial1); Serial.print(" - CTRL+ALT+"); }
      while (Serial1.available())
      {
        char inChar = (char)Serial1.read();
        inChar = (char)Serial1.read();
        if (DEBUG) { Serial.print(inChar); Serial.print(" - "); }
        switch (integerValue_Serial1) {
          case 2001:  
            Keyboard.press(KEY_LEFT_CTRL);
            Keyboard.press(KEY_LEFT_ALT);   
            Keyboard.press(inChar);  
            break;
          case 2002:  
            Keyboard.press(KEY_LEFT_CTRL);
            Keyboard.press(KEY_LEFT_ALT);
            Keyboard.press(inChar);
            break;
          default:
            break;
        }
        if (DEBUG) { Serial.println("DONE"); }
        //Keyboard.releaseAll(); 
      }
    }
    if (integerValue_Serial1>=3000 && integerValue_Serial1<4000)
    {
      if (DEBUG) { Serial.print("Function-Input from Raspi: "); Serial.print(integerValue_Serial1); }
      while (Serial1.available())
      {
        char inChar = (char)Serial1.read();
        inChar = (char)Serial1.read();
        switch (integerValue_Serial1) {
          case 3001:  
            acceleration_on = true;
            if (DEBUG) { Serial.print(" - set Acceleration to ON - "); }
            break;
          case 3002:  
            acceleration_on = false;
            if (DEBUG) { Serial.print(" - set Acceleration to OFF - "); }
            break;
          default:
            break;
        }
        if (DEBUG) { Serial.println("DONE"); }
        integerValue_Serial1 = -1;
      }
    }    
  }
}

