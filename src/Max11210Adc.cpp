#include "Max11210Adc.h"

namespace mr_box_peripheral_board {

Max11210Adc::Max11210Adc() {
    //SPI CLK set to 4MHz, ADC max 5MHz
    max_11210_adc_spi_settings_ = SPISettings(3000000, MSBFIRST, SPI_MODE0);
}

void Max11210Adc::MAX11210_begin(void){
    MAX11210_setDefault();
    MAX11210_setLineFreq(60);  // 60 Hz
    MAX11210_setInputRange(INPUT_RANGE_UNIPOLAR);
    MAX11210_setClockSource(CLOCK_SOURCE_INTERNAL);
    MAX11210_setEnableRefBuf(true);
    MAX11210_setEnableSigBuf(true);
    MAX11210_setFormat(FORMAT_OFFSET);
    MAX11210_setConvMode(CONVERSION_MODE_SINGLE);
    MAX11210_selfCal();
    MAX11210_sysOffsetCal();
    MAX11210_sysGainCal();
}

void Max11210Adc::MAX11210_end(void){
    MAX11210_send_command(POWER_DOWN);
    delay(100);
    SPI.end();
}

void Max11210Adc::MAX11210_selfCal(void){
    //Reset Calibration Values
    MAX11210_setSysGainCal(0x00);
    MAX11210_setSysOffsetCal(0x00);
    MAX11210_setSelfCalGain(0x00);
    MAX11210_setSelfCalOffset(0x00);
    //Enable Self Calibration Registers
    MAX11210_setDisableSelfCalGain(false);
    MAX11210_setDisableSelfCalOffset(false);
    //Start Self Calibration
    MAX11210_send_command(SELF_CALIB);
    delay(300); // A self-calibration requires 200 ms to complete
}

void Max11210Adc::MAX11210_sysOffsetCal(void){
    //Enable Offset Calibration Register
    MAX11210_setDisableSysOffset(false);
    //Start Offset Calibration (Zero Scale)
    MAX11210_send_command(SYS_OFFSET_CALIB);
    delay(300); // A zero-scale calibration requires 100 ms to complete
}

void Max11210Adc::MAX11210_sysGainCal(void){
    //Enable Gain Calibration Register
    MAX11210_setDisableSysGain(false);
    //Start Gain Calibration (Full Scale)
    MAX11210_send_command(SYS_GAIN_CALIB);
    delay(300); // A full-scale calibration requires 100 ms to complete
}

void Max11210Adc::MAX11210_setRate(uint8_t rate){
    if (rate == 1){rate = MEASURE_1_SPS;}
    else if ((rate == 2) | (rate == 3)){rate = MEASURE_2p5_SPS;}
    else if (rate == 5){rate = MEASURE_5_SPS;}
    else if (rate == 10){rate = MEASURE_10_SPS;}
    else if (rate == 15){rate = MEASURE_15_SPS;}
    else if (rate == 30){rate = MEASURE_30_SPS;}
    else if (rate == 60){rate = MEASURE_60_SPS;}
    else if (rate == 120){rate = MEASURE_120_SPS;}
    else {rate = MEASURE_120_SPS;}
    MAX11210_send_command(rate);
    delay(150); // A full-scale calibration requires 100 ms to complete
}

//Read 8 bit for STAT1, CTRL1, CTRL2, CTRL3
uint8_t  Max11210Adc::MAX11210_readReg8(uint8_t reg){
    uint8_t read_command = START | reg | READ;
    uint8_t register_value = 0x00;

    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(read_command);
    register_value = SPI.transfer(0);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
    return register_value;
}
//Read 24 bit for DATA, SOC, SGC, SCOC, SCGC
uint32_t  Max11210Adc::MAX11210_readReg24(uint8_t reg){
    uint8_t read_command = START | reg | READ;
//  uint32_t register_value = 0x00;

    union {
    uint8_t uint8[4];
    uint32_t uint32;
    } register_value;

    register_value.uint32 = 0x00;
    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(read_command);
    register_value.uint8[2] = SPI.transfer(0);
    register_value.uint8[1] = SPI.transfer(0);
    register_value.uint8[0] = SPI.transfer(0);
//  register_value = ((reg_val1 << 16) |(reg_val2 << 8)| reg_val3);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
    return register_value.uint32;
}

//Write 8 bit for CTRL1, CTRL2, CTRL3
void  Max11210Adc::MAX11210_writeReg8(uint8_t reg, uint8_t data){
    uint8_t write_command = START | reg;
    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(write_command);
    SPI.transfer(data);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
}
//Write 24 bit for SOC, SGC, SCOC, SCGC
void  Max11210Adc::MAX11210_writeReg24(uint8_t reg, uint32_t data){
    uint8_t write_command = START | reg;
    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(write_command);
    SPI.transfer((data >> 16));
    SPI.transfer((data >> 8));
    SPI.transfer(data);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
}
//Send a single command
void Max11210Adc::MAX11210_send_command(uint8_t cmd){
    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(cmd);

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
}
//Read Data from ADC
uint32_t Max11210Adc::MAX11210_getData(void){
    SPI.beginTransaction(max_11210_adc_spi_settings_);
    digitalWrite(ADC_CS_PIN, LOW);

    SPI.transfer(START | STAT1 | READ);
    while ((SPI.transfer(0)& RDY) != 1){
    SPI.transfer(START | STAT1 | READ);
    }

    digitalWrite(ADC_CS_PIN, HIGH);
    SPI.endTransaction();
    uint32_t adc_out = MAX11210_readReg24(DATA_);

    return adc_out;
}

//Read STAT1 Registry
uint8_t Max11210Adc::MAX11210_getSTAT1(){ return MAX11210_readReg8(STAT1); }
uint8_t Max11210Adc::MAX11210_getCTRL1(){ return MAX11210_readReg8(CTRL1); }
uint8_t Max11210Adc::MAX11210_getCTRL2(){ return MAX11210_readReg8(CTRL2); }
uint8_t Max11210Adc::MAX11210_getCTRL3(){ return MAX11210_readReg8(CTRL3); }
void Max11210Adc::MAX11210_setDefault(void){
    //Set CTRL1, CTRL2 & CTRL3 Registries to default values
    MAX11210_writeReg8(CTRL1, CTRL1_DEFAULT);
    MAX11210_writeReg8(CTRL2, CTRL2_DEFAULT);
    MAX11210_writeReg8(CTRL3, CTRL3_DEFAULT);
}
//CTRL1 Commands
uint8_t Max11210Adc::MAX11210_setLineFreq(uint8_t frequency){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (frequency == 50) { data = reg | LINEF; }
    else if (frequency == 60){ data = reg & ~ LINEF; }
    else { return (reg & LINEF) ? 50 : 60; }
    MAX11210_writeReg8(CTRL1, data);
    return frequency;
}

uint8_t Max11210Adc::MAX11210_setInputRange(uint8_t value){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (value == INPUT_RANGE_UNIPOLAR){data = reg | U_B;}
    else if (value == INPUT_RANGE_BIPOLAR){data = reg & ~ U_B;}
    else { return (reg & U_B) ? INPUT_RANGE_UNIPOLAR : INPUT_RANGE_BIPOLAR; }
    MAX11210_writeReg8(CTRL1, data);
    return value;
}
uint8_t Max11210Adc::MAX11210_setClockSource(uint8_t value){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (value == CLOCK_SOURCE_EXTERNAL){data = reg | EXTCLK;}
    else if (value == CLOCK_SOURCE_INTERNAL){data = reg & ~ EXTCLK;}
    else { return (reg & EXTCLK) ? CLOCK_SOURCE_EXTERNAL : CLOCK_SOURCE_INTERNAL; }
    MAX11210_writeReg8(CTRL1, data);
    return value;
}
void Max11210Adc::MAX11210_setEnableRefBuf(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (state){data = reg | REFBUF;}
    else{data = reg & ~ REFBUF;}
    MAX11210_writeReg8(CTRL1, data);
}
void Max11210Adc::MAX11210_setEnableSigBuf(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (state){data = reg | SIGBUF;}
    else{data = reg & ~ SIGBUF;}
    MAX11210_writeReg8(CTRL1, data);
}
uint8_t Max11210Adc::MAX11210_setFormat(uint8_t value){
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (value == FORMAT_OFFSET){data = reg | FORMAT;}
    else if (value == FORMAT_TWOS_COMPLEMENT){data = reg & ~ FORMAT;}
    else { return (reg & FORMAT) ? FORMAT_OFFSET : FORMAT_TWOS_COMPLEMENT; }
    MAX11210_writeReg8(CTRL1, data);
    return value;
}
uint8_t Max11210Adc::MAX11210_setConvMode(uint8_t value) {
    uint8_t reg = MAX11210_readReg8(CTRL1);
    uint8_t data = 0x00;
    if (value == CONVERSION_MODE_SINGLE) { data = reg | SCYCLE; }
    else if (value == CONVERSION_MODE_CONTINUOUS) { data = reg & ~ SCYCLE; }
    else { return (reg & SCYCLE) ? CONVERSION_MODE_SINGLE : CONVERSION_MODE_CONTINUOUS; }
    MAX11210_writeReg8(CTRL1, data);
    return value;
}
//CTRL2 Commands (GPIO)
void Max11210Adc::MAX11210_pinModeGpio(uint8_t pin, uint8_t mode){
    if (pin < 1 || pin > 4) return;
    uint8_t reg = MAX11210_readReg8(CTRL2);
    uint8_t data = 0x00;
    if (mode == OUTPUT){data = reg | (DIR1 << (pin-1));}
    else if (mode == INPUT){data = reg & ~ (DIR1 << (pin-1));}
    MAX11210_writeReg8(CTRL2, data);
}
void Max11210Adc::MAX11210_digitalWriteGpio(uint8_t pin, bool value){
    if (pin < 1 || pin > 4) return;
    uint8_t reg = MAX11210_readReg8(CTRL2);
    uint8_t data = 0x00;
    if (value){data = reg | (DIO1 << (pin-1));}
    else{data = reg & ~ (DIO1 << (pin-1));}
    MAX11210_writeReg8(CTRL2, data);
}
bool Max11210Adc::MAX11210_digitalReadGpio(uint8_t pin){
    if (pin < 1 || pin > 4) return false;
    uint8_t reg = MAX11210_readReg8(CTRL2);
    uint8_t stat = reg & (DIO1 << (pin-1));
    return (stat > 0x00);
}
//CTRL3 Commands
void Max11210Adc::MAX11210_setGain(uint8_t value){
    uint8_t reg = MAX11210_readReg8(CTRL3) & 0b00011111; //Reset the first 3 bits (gain bits)
    uint8_t data = 0x00;
    if (value == 1){data = reg | GAIN_1;}
    else if (value == 2){data = reg | GAIN_2;}
    else if (value == 4){data = reg | GAIN_4;}
    else if (value == 8){data = reg | GAIN_8;}
    else if (value >= 16){data = reg | GAIN_16;}
    MAX11210_writeReg8(CTRL3, data);
}
void Max11210Adc::MAX11210_setDisableSysGain(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL3);
    uint8_t data = 0x00;
    if (state){data = (reg | NOSYSG);}
    else{data = (reg & ~NOSYSG);}
    MAX11210_writeReg8(CTRL3, data);
}
void Max11210Adc::MAX11210_setDisableSysOffset(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL3);
    uint8_t data = 0x00;
    if (state){data = (reg | NOSYSO);}
    else{data = (reg & ~NOSYSO);}
    MAX11210_writeReg8(CTRL3, data);
}
void Max11210Adc::MAX11210_setDisableSelfCalGain(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL3);
    uint8_t data = 0x00;
    if (state){data = (reg | NOSCG);}
    else{data = (reg & ~NOSCG);}
    MAX11210_writeReg8(CTRL3, data);
}
void Max11210Adc::MAX11210_setDisableSelfCalOffset(bool state){
    uint8_t reg = MAX11210_readReg8(CTRL3);
    uint8_t data = 0x00;
    if (state){data = (reg | NOSCO);}
    else{data = (reg & ~NOSCO);}
    MAX11210_writeReg8(CTRL3, data);
}
//Read from 24bit Registries (SGC, SOC, SCGC, SCOC)
uint32_t Max11210Adc::MAX11210_getSysGainCal(void) {return MAX11210_readReg24(SGC);}
uint32_t Max11210Adc::MAX11210_getSysOffsetCal(void) {return MAX11210_readReg24(SOC);}
uint32_t Max11210Adc::MAX11210_getSelfCalGain(void) {return MAX11210_readReg24(SCGC);}
uint32_t Max11210Adc::MAX11210_getSelfCalOffset(void) {return MAX11210_readReg24(SCOC);}
//24 bit Commands (SGC, SOC, SCGC, SCOC)
void Max11210Adc::MAX11210_setSysGainCal(uint32_t value) {MAX11210_writeReg24(SGC, value);}
void Max11210Adc::MAX11210_setSysOffsetCal(uint32_t value) {MAX11210_writeReg24(SOC, value);}
void Max11210Adc::MAX11210_setSelfCalGain(uint32_t value) {MAX11210_writeReg24(SCGC, value);}
void Max11210Adc::MAX11210_setSelfCalOffset(uint32_t value) {MAX11210_writeReg24(SCOC, value);}

}  // namespace mr_box_peripheral_board {
