import datetime as dt

import pandas as pd

import logging
from collections import OrderedDict

SYSOR = 0b10000000
OR_ = 0b00001000
UR = 0b00000100
MSTAT = 0b00000010
RDY = 0b00000001

# SAMPLIG SPEED
MEASURE_1_SPS = 0b10000000
MEASURE_2p5_SPS = 0b10000001
MEASURE_5_SPS = 0b10000010
MEASURE_10_SPS = 0b10000011
MEASURE_15_SPS = 0b10000100
MEASURE_30_SPS = 0b10000101
MEASURE_60_SPS = 0b10000110
MEASURE_120_SPS = 0b10000111

# CTRL3 COMMAND BYTES (Gain & Calibration)
GAIN_1 = 0b00000000
GAIN_2 = 0b00100000
GAIN_4 = 0b01000000
GAIN_8 = 0b01100000
GAIN_16 = 0b10000000
NOSYSG = 0b00010000  #      //Disables the use of the system gain
NOSYSO = 0b00001000  #      //Disables the use of the system offset
NOSCG = 0b00000100  #      //Disables the use of the self-calibration gain
NOSCO = 0b00000010  #      //Disables the use of the self-calibration offset
CTRL3_DEFAULT = 0b00011110

# CTRL1 COMMAND BYTES
LINEF = 0b10000000  # 50 Hz
U_B = 0b01000000  # Unipolar
EXTCLK = 0b00100000  # External Clock
REFBUF = 0b00010000  # Reference Buffer
SIGBUF = 0b00001000  # Signal Buffer
FORMAT = 0b00000100  # Offset binary format
SCYCLE = 0b00000010  # Single-conversion mode
CTRL1_DEFAULT = 0b00000010



def format_CTRL3(CTRL3):
     adc_status = CTRL3
     if ((adc_status & GAIN_2) > 0x00):
         dgain = "X2\n";
     elif ((adc_status & GAIN_4) > 0x00):
         dgain = "X4\n";
     elif ((adc_status & GAIN_8) > 0x00):
         dgain = "X8\n";
     elif ((adc_status & GAIN_16) > 0x00):
         dgain = "X16\n";
     else:
         dgain = "X1\n";
     if ((adc_status & NOSYSG) > 0x00):
         nosysg = "Disabled\n";
     else:
         nosysg = "Enabled\n";
     if ((adc_status & NOSYSO) > 0x00):
         nosyso = "Disabled\n";
     else:
         nosyso = "Enabled\n";
     if ((adc_status & NOSCG) > 0x00):
         noscg = "Disabled\n";
     else:
         noscg = "Enabled\n";
     if ((adc_status & NOSCO) > 0x00):
         nosco = "Disabled\n";
     else:
         nosco = "Enabled\n";
     return ("Digital Gain: "+dgain+"System Gain: "+nosysg+"System Offset: "+nosyso+"Self-calibration Gain: "+noscg+"Self-calibration Offset: "+nosco)


def format_CTRL1(CTRL1):
    adc_status = CTRL1
    if ((adc_status & LINEF) > 0x00):
        lfreq = "50Hz\n";
    else:
        lfreq = "60Hz\n";
    if ((adc_status & U_B) > 0x00):
        inprange = "Unipolar (Positive Only)\n";
    else:
        inprange = "Bipolar (+/-)\n";
    if ((adc_status & EXTCLK) > 0x00):
        clk = "External\n";
    else:
        clk = "Internal\n";
    if ((adc_status & REFBUF) > 0x00):
        rbuf = "On\n";
    else:
        rbuf = "Off\n";
    if ((adc_status & SIGBUF) > 0x00):
        sbuf = "On\n";
    else:
        sbuf = "Off\n";
    if ((adc_status & FORMAT) > 0x00):
        format = "Offset\n";
    else:
        format = "2Complement\n";
    if ((adc_status & SCYCLE) > 0x00):
        scycle = "Single\n";
    else:
        scycle = "Continuous\n";
    return ("Line frequency: "+lfreq +"Input Range: "+inprange+"Clock: "+clk+"Refference Buffer: "+rbuf+"Signal Buffer: "+sbuf+"Format: "+format+"Cycle: "+scycle)


def format_STAT1(STAT1):
    adc_status = STAT1

    if ((adc_status & SYSOR) > 0x00):
        gor = "True\n"
    else:
        gor = "False\n"

    srate = ((adc_status & 0b01110000)>>4 | 0b10000000)

    if (srate == MEASURE_1_SPS):
        rate = "1 Sample/sec\n"
    elif (srate == MEASURE_2p5_SPS):
        rate = "2.5 Samples/sec\n"
    elif (srate == MEASURE_5_SPS):
        rate = "5 Samples/sec\n"
    elif (srate == MEASURE_10_SPS):
        rate = "10 Samples/sec\n"
    elif (srate == MEASURE_15_SPS):
        rate = "15 Samples/sec\n"
    elif (srate == MEASURE_30_SPS):
        rate = "30 Samples/sec\n"
    elif (srate == MEASURE_60_SPS):
        rate = "60 Samples/sec\n"
    elif (srate == MEASURE_120_SPS):
        rate = "120 Samples/sec\n"

    if ((adc_status & OR_) > 0x00):
        mor = "True\n"
    else:
        mor = "False\n"
    if ((adc_status & UR) > 0x00):
        ur = "True\n"
    else:
        ur = "False\n"
    if ((adc_status & MSTAT) > 0x00):
        mstat = "Busy\n"
    else:
        mstat = "Idle\n"
    if ((adc_status & RDY) > 0x00):
        rdy = "Ready\n"
    else:
        rdy = "In Progress\n"
    return ("Gain Over Range: "+gor+"Sampling Rate: "+rate+"Input Signal Over Max: "+mor+"Input Signal Under Min: "+ur+"Modulator Status: "+mstat+"ADC Status: "+rdy)

def MAX11210_begin(proxy):
    LINE_FREQ = 60 # 60 Hz
    INPUT_RANGE_UNIPOLAR = 1
    INPUT_RANGE_BIPOLAR = 2
    CLOCK_SOURCE_EXTERNAL = 1
    CLOCK_SOURCE_INTERNAL = 2
    FORMAT_OFFSET = 1
    FORMAT_TWOS_COMPLEMENT = 2
    CONVERSION_MODE_SINGLE = 1
    CONVERSION_MODE_CONTINUOUS = 2

    proxy.MAX11210_setDefault();
    proxy.MAX11210_setLineFreq(LINE_FREQ);
    proxy.MAX11210_setInputRange(INPUT_RANGE_UNIPOLAR);
    proxy.MAX11210_setClockSource(CLOCK_SOURCE_INTERNAL);
    proxy.MAX11210_setEnableRefBuf(True);
    proxy.MAX11210_setEnableSigBuf(True);
    proxy.MAX11210_setFormat(FORMAT_OFFSET);
    proxy.MAX11210_setConvMode(CONVERSION_MODE_SINGLE);
    proxy.MAX11210_selfCal();
    proxy.MAX11210_sysOffsetCal();
    proxy.MAX11210_sysGainCal();

    logger = logging.getLogger(__name__)
    logger.info('\n%s' % proxy.get_adc_calibration())

def MAX11210_read(proxy, rate,  duration_s):
    assert(rate in (1, 2, 5, 10, 15, 30, 60, 120))
    proxy.MAX11210_setConvMode(1)

    # proxy.MAX11210_setGain(dgain)

    proxy.pin_mode(9, 1)  # Set pin to output.
    proxy.pmt_open_shutter()

    start_time = dt.datetime.now()

    timestamps = []
    readings = []
    try:
        while (dt.datetime.now() - start_time).total_seconds() < duration_s:
            proxy.MAX11210_setRate(rate)
            reading_i = proxy.MAX11210_getData()
            timestamps.append(dt.datetime.now())
            readings.append(reading_i)
    finally:
        proxy.pmt_close_shutter()
    return pd.Series(readings, index=timestamps)

def MAX11210_status(proxy):
    logger = logging.getLogger(__name__)
    logger.info('Status Register\n%s' % format_STAT1(proxy.MAX11210_getSTAT1()))
    logger.info('Control Register 1\n%s' % format_CTRL1(proxy.MAX11210_getCTRL1()))
    # logger.info('Control Register 1\n%s' % str(format(proxy.MAX11210_getCTRL2(),'b'))
    logger.info('Control Register 3\n%s' % format_CTRL3(proxy.MAX11210_getCTRL3()))
