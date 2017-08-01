#ifndef ___MR_BOX_PERIPHERAL_BOARD__PUMP__H___
#define ___MR_BOX_PERIPHERAL_BOARD__PUMP__H___

#include <Arduino.h>
#include <stdint.h>
#include "FastAnalogWrite.h"

namespace mr_box_peripheral_board {

using base_node_rpc::FastAnalogWrite;

class Pump {
    /*
     * API to Interface with [mp6-OEM][1] [mp6 micropump][2] controller.
     *
     * See also: [mp6-oem Datasheet][3].
     *
     * [1]: http://bartels-mikrotechnik.de/index.php/22-electronic/70-mp6-oem-controller
     * [2]: http://bartels-mikrotechnik.de/index.php/en/products/micropumps
     * [3]: https://www.servoflo.com/download-archive/data-sheets/272-mp6-data-sheets/1074-mp6-manual
     */
protected:
    FastAnalogWrite pump_frequency_;

public:
    const uint8_t PIN_AMPLITUDE = 3;
    const uint8_t PIN_FREQUENCY = 4;

    Pump() : pump_frequency_(PIN_FREQUENCY) {
        // XXX Although it **SEEMS** redundant, without the following line,
        // `pump_frequency_` is not initialized properly.
        //
        // TODO Is this a complier issue??
        pump_frequency_ = FastAnalogWrite(PIN_FREQUENCY);

        pinMode(PIN_AMPLITUDE, OUTPUT);
    }

    void pump_frequency_configure(uint8_t duty_cycle, uint32_t period_us) {
        /*
         * Configure pump frequency and set frequency pin low.
         */
        pump_frequency_.configure(duty_cycle, period_us);
    }

    void pump_frequency_set(float frequency_hz) {

        /* From section 6.6.3 in the mp6-oem [Datasheet][1]:
         *
         * > Using a microcontroller to operate the micropump, a quadruplicated
         * > frequency of the final micropumps frequency has to be connected to
         * > the `CLOCK` Pin. With this procedure, single-digit frequencies can
         * > be achieved.
         * >
         * > Please take into account to set the pulse-width of the frequency
         * > duty cycle at a level of 95% when operating at frequencies lower
         * > than 25 Hz.
         *
         * [1]: https://www.servoflo.com/download-archive/data-sheets/272-mp6-data-sheets/1074-mp6-manual
         */
        pump_frequency_configure(0.95 * 255., 4e6 / frequency_hz);
    }

    void pump_frequency_reset() {
        /*
         * Disable frequency and set frequency pin low.
         */
        pump_frequency_.reset();
    }

    void pump_update() {
        /*
         * Update state of frequency pin based on elapsed time since last pin
         * state change.
         */
        pump_frequency_.update();
    }

    void pump_activate() { digitalWrite(PIN_AMPLITUDE, HIGH); }
    void pump_deactivate() { digitalWrite(PIN_AMPLITUDE, LOW); }
};

}  // namespace mr_box_peripheral_board {

#endif  // #ifndef ___MR_BOX_PERIPHERAL_BOARD__PUMP__H___
