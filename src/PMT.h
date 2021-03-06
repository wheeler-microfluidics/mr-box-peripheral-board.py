#ifndef ___MR_BOX_PERIPHERAL_BOARD__PMT__H___
#define ___MR_BOX_PERIPHERAL_BOARD__PMT__H___

#include <Arduino.h>
#include <stdint.h>
#include <SPI.h>

namespace mr_box_peripheral_board {

class PMT {
public:
    const uint8_t MCP41050_CS_PIN        = 8;  // MCP41050 digipot select Pin
    const uint8_t MCP41050_COMMAND_CODE = 0x11;  // Command code to set value
    const uint8_t REFERENCE_ANALOG_PIN   = A0;  // Reference voltage pin
    const uint8_t SHUTTER_PIN            = 9;  //Shutter Pin (**active low**)

    void PMT_begin() {
        // Set shutter pin to output.
        pinMode(SHUTTER_PIN, OUTPUT);
        // Set MCP41050 digipot CS pin to output.
        pinMode(MCP41050_CS_PIN, OUTPUT);
        // XXX Set shutter closed by default.
        pmt_close_shutter();
        // Set MCP41050 digipot to 0;
        pmt_set_pot(0);
    }


    float pmt_reference_voltage() const {
        // read the adc value
        int sensorValue = analogRead(REFERENCE_ANALOG_PIN);
        // convert the adc value
        return sensorValue * (3.3 / 1023.0);
    }

    float pmt_set_pot(uint8_t value) {
        /*
         * Parameters
         * ----------
         * value : uint8_t
         *     Digital potentiometer value, 0-255.
         */
        SPI.beginTransaction(SPISettings(3000000, MSBFIRST, SPI_MODE0));
        // take the SS pin low to select the chip:
        digitalWrite(MCP41050_CS_PIN, LOW);
        // send Command to write value and enable the pot:
        SPI.transfer(MCP41050_COMMAND_CODE);
        // send in the value:
        SPI.transfer(value);
        // take the SS pin high to de-select the chip:
        digitalWrite(MCP41050_CS_PIN, HIGH);
        SPI.endTransaction();

        return pmt_reference_voltage();
    }

    void pmt_open_shutter() { digitalWrite(SHUTTER_PIN, LOW); }
    void pmt_close_shutter() { digitalWrite(SHUTTER_PIN, HIGH); }
};

}  // namespace mr_box_peripheral_board {

#endif  // #ifndef ___MR_BOX_PERIPHERAL_BOARD__PMT__H___
