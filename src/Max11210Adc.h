#ifndef ___MR_BOX_PERIPHERAL_BOARD__MAX11210_ADC__H___
#define ___MR_BOX_PERIPHERAL_BOARD__MAX11210_ADC__H___

#include <Arduino.h>
#include <stdint.h>
#include <SPI.h>
#include "max11210.h"

namespace mr_box_peripheral_board {

class Max11210Adc {
public:
    const uint8_t ADC_CS_PIN = 6;   // MAX11210 Select Pin
    const uint8_t MOSI_PIN   = 11;  // DIN
    const uint8_t MISO_PIN   = 12;  // DOUT
    const uint8_t SCK_PIN    = 13;  // Signal Clock

    const uint8_t INPUT_RANGE_UNIPOLAR = 1;
    const uint8_t INPUT_RANGE_BIPOLAR = 2;
    const uint8_t CLOCK_SOURCE_EXTERNAL = 1;
    const uint8_t CLOCK_SOURCE_INTERNAL = 2;
    const uint8_t FORMAT_OFFSET = 1;
    const uint8_t FORMAT_TWOS_COMPLEMENT = 2;
    const uint8_t CONVERSION_MODE_SINGLE = 1;
    const uint8_t CONVERSION_MODE_CONTINUOUS = 2;

    SPISettings max_11210_adc_spi_settings_;

    Max11210Adc();

    void MAX11210_begin(void);
    void MAX11210_end(void);
    void MAX11210_selfCal(void);
    void MAX11210_sysOffsetCal(void);
    void MAX11210_sysGainCal(void);
    void MAX11210_setRate(uint8_t rate);

    //Read 8 bit for STAT1, CTRL1, CTRL2, CTRL3
    uint8_t  MAX11210_readReg8(uint8_t reg);
    //Read 24 bit for DATA, SOC, SGC, SCOC, SCGC
    uint32_t  MAX11210_readReg24(uint8_t reg);
    //Write 8 bit for CTRL1, CTRL2, CTRL3
    void  MAX11210_writeReg8(uint8_t reg, uint8_t data);
    //Write 24 bit for SOC, SGC, SCOC, SCGC
    void  MAX11210_writeReg24(uint8_t reg, uint32_t data);
    //Send a single command
    void MAX11210_send_command(uint8_t cmd);
    //Read Data from ADC
    uint32_t MAX11210_getData(void);
    //Read STAT1 Registry
    uint8_t MAX11210_getSTAT1();
    uint8_t MAX11210_getCTRL1();
    uint8_t MAX11210_getCTRL2();
    uint8_t MAX11210_getCTRL3();
    void MAX11210_setDefault(void);
    //CTRL1 Commands
    uint8_t MAX11210_setLineFreq(uint8_t frequency);
    uint8_t MAX11210_setInputRange(uint8_t value);
    uint8_t MAX11210_setClockSource(uint8_t value);
    void MAX11210_setEnableRefBuf(bool state);
    void MAX11210_setEnableSigBuf(bool state);
    uint8_t MAX11210_setFormat(uint8_t value);
    uint8_t MAX11210_setConvMode(uint8_t value);
    //CTRL2 Commands (GPIO)
    void MAX11210_pinModeGpio(uint8_t pin, uint8_t mode);
    void MAX11210_digitalWriteGpio(uint8_t pin, bool value);
    bool MAX11210_digitalReadGpio(uint8_t pin);
    //CTRL3 Commands
    void MAX11210_setGain(uint8_t value);
    void MAX11210_setDisableSysGain(bool state);
    void MAX11210_setDisableSysOffset(bool state);
    void MAX11210_setDisableSelfCalGain(bool state);
    void MAX11210_setDisableSelfCalOffset(bool state);
    //Read from 24bit Registries (SGC, SOC, SCGC, SCOC)
    uint32_t MAX11210_getSysGainCal(void);
    uint32_t MAX11210_getSysOffsetCal(void);
    uint32_t MAX11210_getSelfCalGain(void);
    uint32_t MAX11210_getSelfCalOffset(void);
    //24 bit Commands (SGC, SOC, SCGC, SCOC)
    void MAX11210_setSysGainCal(uint32_t value);
    void MAX11210_setSysOffsetCal(uint32_t value);
    void MAX11210_setSelfCalGain(uint32_t value);
    void MAX11210_setSelfCalOffset(uint32_t value);
};

}  // namespace mr_box_peripheral_board {

#endif  // #ifndef ___MR_BOX_PERIPHERAL_BOARD__MAX11210_ADC__H___
