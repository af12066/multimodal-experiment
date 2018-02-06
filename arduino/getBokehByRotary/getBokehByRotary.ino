volatile int rot_state; // 状態 0~3
const int rot_pins[] = {2, 3};  // ロータリーエンコーダに接続 (attachInterrupt の都合上 2, 3 ピンに限定)
const int rot_pinNum = sizeof(rot_pins) / sizeof(rot_pins[0]);  // ロータリーエンコーダに使用するピンの個数
const int trig_pin = 13;
int incomingByte = 0;
volatile bool ChangeTrig = false;  // ロータリー切り替え時に反転してデジタル出力

void setup()
{
  Serial.begin(9600);
  for (int i = 0; i < rot_pinNum; i++){
    pinMode(rot_pins[i], INPUT);
  }
  pinMode(trig_pin, OUTPUT);
  rot_state = rotary_getState(rot_pins[0], rot_pins[1]); // 現在の状態を保存しておく

  /* 割り込み処理は以下に記述 */
  attachInterrupt(0, evalState, CHANGE);
  attachInterrupt(1, evalState, CHANGE);
}

/* キャリブレーションタスク時は loop() でトリガ処理を行なう */
void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 49) {
      digitalWrite(trig_pin, HIGH);
    } else {
      digitalWrite(trig_pin, LOW);
    }
  }
  delayMicroseconds(30);
}

/* 割り込みでロータリーの回転方向を決定 */
void evalState() {
  volatile int rot_past = rot_state;
  rot_state = rotary_getState(rot_pins[0], rot_pins[1]);  // 現在の状態
  volatile int rot_dir = rotary_getDir(rot_state, rot_past);  // 回転方向
  switch(rot_dir) {
    case 2:
      Serial.print("R");
      ChangeTrig = !ChangeTrig;
      digitalWrite(trig_pin, ChangeTrig);
      break;
    case 1:
      Serial.print("L");
      ChangeTrig = !Cha;
      digitalWrite(trig_pin, ChangeTrig);
      break;
    default:
      break;
  }
}

/* ロータリーエンコーダの状態番号を取得する */
int rotary_getState(int pinA, int pinB) {
  if (digitalRead(pinA)) {
    if (digitalRead(pinB)) {
      return 2;  // 左回り
    } else {
      return 0;  // 変化なし
    }
  } else {
    if (digitalRead(pinB)) {
      return 1;  // 右回り
    } else {
      return 3;
    }
  }
}

/* 1つ前の状態と比較して，回転方向を取得する */
int rotary_getDir(int state, int past_state) {
  if ((state == 2) && (past_state == 0)) {
    return 2;  // 左回り
  } else if ((state == 2) && (past_state == 1)) {
    return 1;  // 右回り
  }
  return 0;  // 変化なし
}
