#ifndef ___NODE__H___
#define ___NODE__H___

#include <math.h>
#include <string.h>
#include <stdint.h>
#include <Arduino.h>
#include <NadaMQ.h>
#include <CArrayDefs.h>
#include "RPCBuffer.h"  // Define packet sizes
#include "MrBoxPeripheralBoard/Properties.h"  // Define package name, URL, etc.
#include <BaseNodeRpc/BaseNode.h>
#include <BaseNodeRpc/BaseNodeEeprom.h>
#include <BaseNodeRpc/BaseNodeConfig.h>
#include <BaseNodeRpc/BaseNodeSerialHandler.h>
#include <BaseNodeRpc/SerialHandler.h>
#include <pb_cpp_api.h>
#include <pb_validate.h>
#include <pb_eeprom.h>
#include <FastDigital.h>
#include "mr_box_peripheral_board_config_validate.h"
#include "MrBoxPeripheralBoard/config_pb.h"
#include "PMT.h"
#include "Pump.h"
#include "ZStage.h"
#include "Max11210Adc.h"

namespace mr_box_peripheral_board {

const size_t FRAME_SIZE = (3 * sizeof(uint8_t)  // Frame boundary
                           - sizeof(uint16_t)  // UUID
                           - sizeof(uint16_t)  // Payload length
                           - sizeof(uint16_t));  // CRC


class Node;
const char HARDWARE_VERSION_[] = "0.1.0";

typedef nanopb::EepromMessage<mr_box_peripheral_board_Config,
                              config_validate::Validator<Node> > config_t;

class Node :
  public BaseNode,
  public BaseNodeEeprom,
  public BaseNodeConfig<config_t>,
#ifndef DISABLE_SERIAL
  public BaseNodeSerialHandler,
#endif  // #ifndef DISABLE_SERIAL
  public PMT,
  public Pump,
  public base_node_rpc::ZStage,
  public Max11210Adc {
public:
  typedef PacketParser<FixedPacket> parser_t;

  static const uint32_t BUFFER_SIZE = 80;  // >= longest property string

  uint8_t buffer_[BUFFER_SIZE];

  Node() : BaseNode(),
           BaseNodeConfig<config_t>(mr_box_peripheral_board_Config_fields),
           Pump(),
           base_node_rpc::ZStage(),
           Max11210Adc() {
    // XXX Turn on LED by default to indicate power is on.
    pinMode(LED_BUILTIN, OUTPUT);
  }

  UInt8Array get_buffer() { return UInt8Array_init(sizeof(buffer_), buffer_); }
  /* This is a required method to provide a temporary buffer to the
   * `BaseNode...` classes. */

  void begin();
  /****************************************************************************
   * # User-defined methods #
   *
   * Add new methods below.  When Python package is generated using the
   * command, `paver sdist` from the project root directory, the signatures of
   * the methods below will be scanned and code will automatically be generated
   * to support calling the methods from Python over a serial connection.
   *
   * e.g.
   *
   *     bool less_than(float a, float b) { return a < b; }
   *
   * See [`arduino_rpc`][1] and [`base_node_rpc`][2] for more details.
   *
   * [1]: https://github.com/wheeler-microfluidics/arduino_rpc
   * [2]: https://github.com/wheeler-microfluidics/base_node_rpc
   */
  UInt8Array hardware_version() {
    return UInt8Array_init(strlen(HARDWARE_VERSION_),
                           (uint8_t *)&HARDWARE_VERSION_[0]);
  }

  bool set_id(UInt8Array id) {
    if (id.length > sizeof(config_._.id) - 1) {
      return false;
    }
    memcpy(config_._.id, &id.data[0], id.length);
    config_._.id[id.length] = 0;
    config_._.has_id = true;
    config_.save();
    return true;
  }

  // # Callback methods
  void on_tick() {}

  /** Called periodically from the main program loop. */
  void loop() {
    pump_update();
  }

  // ##########################################################################
  // # Accessor methods
  uint16_t analog_input_to_digital_pin(uint16_t pin) { return analogInputToDigitalPin(pin); }
  uint16_t digital_pin_has_pwm(uint16_t pin) { return digitalPinHasPWM(pin); }
  uint16_t digital_pin_to_interrupt(uint16_t pin) { return digitalPinToInterrupt(pin); }
};
}  // namespace mr_box_peripheral_board


#endif  // #ifndef ___NODE__H___
