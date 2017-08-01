#ifndef ___BASE_NODE_RPC__Z_STAGE__H___
#define ___BASE_NODE_RPC__Z_STAGE__H___

#include <Arduino.h>
#include <stdint.h>

namespace base_node_rpc {


class ZStage {
private:
  const int PIN_MICRO_STEPPING = 2;
  const int PIN_STEP = A2;
  const int PIN_DIRECTION = A1;
  const int PIN_ENABLE = A3;

  /* XXX End-stops are connected to ADC inputs 6 and 7, which are **only**
   * analog inputs and may not be configured as outputs (see [here][1]).  This
   * also means that these pins **DO NOT** have internal pull-up resistors.
   *
   * TODO Modify MR-Box peripheral board PCB design to incorporate pull-up
   * resistors for both end stops.
   *
   * [1]: http://forum.arduino.cc/index.php?topic=166232.msg1239671#msg1239671 */
  const int PIN_END_STOP_1 = 6;  // ADC6
  const int PIN_END_STOP_2 = 7;  // ADC7

  class ZStageState {
    public:
        float position;
        bool motor_enabled;
        bool micro_stepping;
        uint32_t RPM;
        bool home_stop_enabled;
        bool engaged_stop_enabled;
  };

  ZStageState state_;

public:
  ZStage() {
    pinMode(PIN_MICRO_STEPPING, OUTPUT);
    pinMode(PIN_STEP, OUTPUT);
    pinMode(PIN_DIRECTION, OUTPUT);
    pinMode(PIN_ENABLE, OUTPUT);

    digitalWrite(PIN_DIRECTION, LOW);

    zstage_reset();
  }

  void zstage_reset() {
    state_.position = 0;
    state_.motor_enabled = false;
    state_.micro_stepping = true;
    state_.RPM = 50;
    state_.home_stop_enabled = true;
    state_.engaged_stop_enabled = false;
  }

  bool zstage_set_position(float position) {
    if (state_.motor_enabled) {
      state_.position = position;
      zstage_move_to(position);
      return true;
    }
    return false;
  }

  void zstage_enable_motor() {
    state_.motor_enabled = true;
    digitalWrite(PIN_ENABLE, LOW);  // Enable
  }

  void zstage_disable_motor() {
    state_.motor_enabled = false;
    digitalWrite(PIN_ENABLE, HIGH);  // Disable
  }

  void zstage_enable_micro_stepping() {
    digitalWrite(PIN_MICRO_STEPPING, HIGH);
  }

  void zstage_disable_micro_stepping() {
    digitalWrite(PIN_MICRO_STEPPING, LOW);
  }

  bool zstage_at_home() {
    return state_.home_stop_enabled && (analogRead(PIN_END_STOP_1) < (1023 / 4));
  }

  void zstage_home() {
    if (!state_.home_stop_enabled) return;

    state_.position = 100;
    while (!zstage_at_home()) { zstage_move(1., 25., false); }
    state_.position = 0;
  }

  void zstage_move_to(float new_position) {
    float distance = new_position - state_.position;
    bool direction = true;

    if (distance < 0) {
      direction = 0;
      distance = -distance;
    }
    zstage_move(distance, state_.RPM, direction);
  }

  float zstage_move(float distance, int RPM, bool direction) {
    /*
     * Parameters
     * ----------
     * distance
     *   Distance (in mm)
     * RPM
     * direction
     *   Direction (true -> Up)
     *
     * Returns
     * -------
     * float
     *     New position.
     */
    float position = state_.position;
    if (direction){
      digitalWrite(PIN_DIRECTION, HIGH);
      position += distance;
    } else{
      digitalWrite(PIN_DIRECTION, LOW);
      position -= distance;
    }

    if (position < 0){
      distance += position;
      position = 0;
    }

    int pulse = 150000 / RPM / state_.micro_stepping;
    float steps = distance * 25. * float(state_.micro_stepping);

    for (int x = 0; x < steps; x++) {
      digitalWrite(PIN_STEP, HIGH);
      delayMicroseconds(pulse);
      digitalWrite(PIN_STEP, LOW);
      delayMicroseconds(pulse);
      if (zstage_at_home() && !direction) {
        break;
      }
    }

    state_.position = position;
    return position;
  }
};

}  // namespace base_node_rpc {

#endif  // #ifndef ___BASE_NODE_RPC__Z_STAGE__H___
