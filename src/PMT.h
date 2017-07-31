#ifndef ___MR_BOX_PERIPHERAL_BOARD__PMT__H___
#define ___MR_BOX_PERIPHERAL_BOARD__PMT__H___

#include <Arduino.h>
#include <stdint.h>
#include <SPI.h>

namespace mr_box_peripheral_board {

class PMT {
public:
    const uint8_t MCP41050_CS_PIN        = 5;  // MCP41050 digipot select Pin
    const uint8_t MCP41050_COMMAND_CODE = 0x11;  // Command code to set value
    const uint8_t REFERENCE_ANALOG_PIN   = 14;  // Reference voltage pin
    const uint8_t SHUTTER_PIN            = 2;  //Shutter Pin (**active low**)

    float pmt_set_pot(uint8_t value) {
        /*
         * Parameters
         * ----------
         * value : uint8_t
         *     Digital potentiometer value, 0-255.
         */
        // take the SS pin low to select the chip:
        digitalWrite(MCP41050_CS_PIN, LOW);
        // send Command to write value and enable the pot:
        SPI.transfer(MCP41050_COMMAND_CODE);
        // send in the value:
        SPI.transfer(value);
        // take the SS pin high to de-select the chip:
        digitalWrite(MCP41050_CS_PIN, HIGH);

        // read the adc value
        int sensorValue = analogRead(REFERENCE_ANALOG_PIN);
        // convert the adc value
        return sensorValue * (3.3 / 1023.0);
    }

    void pmt_activate_shutter() { digitalWrite(SHUTTER_PIN, LOW); }
    void pmt_deactivate_shutter() { digitalWrite(SHUTTER_PIN, HIGH); }
};

}  // namespace mr_box_peripheral_board {

#endif  // #ifndef ___MR_BOX_PERIPHERAL_BOARD__PMT__H___
