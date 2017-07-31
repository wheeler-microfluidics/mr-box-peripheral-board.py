#ifndef ___FAST_ANALOG_WRITE__H___
#define ___FAST_ANALOG_WRITE__H___

#include <Arduino.h>
#include <stdint.h>
#include <SPI.h>
#include <FastDigital.h>

namespace base_node_rpc {

class FastAnalogWrite {
protected:
  bool period_pin_state_;  // Active pin state for `fast_analog_write`.
  uint8_t period_pin_;  // Pin to toggle for `fast_analog_write`.
  uint32_t period_off_us_;  // Duration of "off" state.
  uint32_t period_on_us_;  // Duration of "on" state.
  uint32_t period_start_us_;  // Start time of current period.

public:
  FastAnalogWrite(uint8_t pin)
      : period_pin_state_(false), period_pin_(pin), period_off_us_(0),
        period_on_us_(0), period_start_us_(0) {
    reset();
  }

  FastAnalogWrite(uint8_t pin, uint8_t duty_cycle, uint32_t period_us)
      : period_pin_state_(false), period_pin_(pin), period_off_us_(0),
        period_on_us_(0), period_start_us_(0) {
    reset();
    configure(duty_cycle, period_us);
  }

  void reset() {
    /*
     * Disable pulsing and set pin low.
     */
    pinMode(period_pin_, OUTPUT);
    digitalWriteFast(period_pin_, LOW);
    period_off_us_ = 0;
    period_on_us_ = 0;
  }

  void configure(uint8_t duty_cycle, uint32_t period_us) {
    /*
     * Parameters
     * ----------
     * duty_cycle : uint8_t
     *     Duty cycle as 0-255.
     * period_us : uint32_t
     *     Length of pulse-width modulation period in microseconds.
     */
    period_on_us_ = (duty_cycle / 255.) * period_us;
    period_off_us_ = period_us - period_on_us_;
    period_pin_state_ = HIGH;
    period_start_us_ = micros();
  }

  void update() {
    /*
     * Update state of PWM pin based on elapsed time.
     */
    if (period_on_us_ > 0 || period_off_us_ > 0) {
      uint32_t elapsed_us = micros() - period_start_us_;
      if (period_pin_state_ && elapsed_us > period_on_us_) {
        // Update pin state
        period_pin_state_ = LOW;
        // Turn off pwm pin.
        digitalWriteFast(period_pin_, period_pin_state_);
        // Reset start time for transition.
        period_start_us_ = micros();
      } else if (!period_pin_state_ && elapsed_us > period_off_us_) {
        // Update pin state
        period_pin_state_ = HIGH;
        // Turn on pwm pin.
        digitalWriteFast(period_pin_, period_pin_state_);
        // Reset start time for transition.
        period_start_us_ = micros();
      }
    }
  }
};

}  // namespace base_node_rpc {

#endif  // #ifndef ___MR_BOX_PERIPHERAL_BOARD__PMT__H___
