#include "Arduino.h"
#include "EEPROM.h"
#include "FastDigital.h"
#include "Memory.h"  // Memory utility functions, e.g., ram_free()
#include "ArduinoRpc.h"
#include "nanopb.h"
#include "NadaMQ.h"  // Required replacing `#ifndef AVR` with `#if !defined(AVR) && !defined(__arm__)`
#include "CArrayDefs.h"
#include "RPCBuffer.h"
#include "BaseNodeRpc.h"  // Check for changes (may have removed some include statements...
#include "MrBoxPeripheralBoard.h"
#include "NodeCommandProcessor.h"
#include "Node.h"

mr_box_peripheral_board::Node node_obj;
mr_box_peripheral_board::CommandProcessor<mr_box_peripheral_board::Node> command_processor(node_obj);

// Parse any new serial data using `SerialHandler` for `Node` object.
void serialEvent() { node_obj.serial_handler_.receiver()(Serial.available()); }


void setup() {
  node_obj.begin();
}


void loop() {
  if (node_obj.serial_handler_.packet_ready()) {
    /* A complete packet has successfully been parsed from data on the serial
     * interface.
     * Pass the complete packet to the command-processor to process the request.
     * */
    node_obj.serial_handler_.process_packet(command_processor);
  }

  // XXX Call user defined `loop` code.
  node_obj.loop();
}
