#ifndef __MAX11210_H
#define __MAX11210_H

// MAX11210 8-bit Command
// ------------------------------------------------------------------------
// name     B7         B6         B5     B4     B3     B2     B1     B0
// ------------------------------------------------------------------------
// COMMAND  START = 1  MODE = 0   CAL1   CAL0   IMPD   RATE2  RATE1  RATE0
// COMMAND  START = 1  MODE = 1   0      RS3    RS2    RS1    RS0    R/!W

// MAX11210 Status & Control Registers
// ------------------------------------------------------------------------
//     name     B7     B6     B5     B4     B3     B2     B1     B0
// ------------------------------------------------------------------------
// 0x0 STAT1    SYSOR  RATE2  RATE1  RATE0  OR     UR     MSTAT  RDY
// 0x1 CTRL1    LINEF  U/!B   EXTCLK REFBUF SIGBUF FORMAT SCYCLE RESERVED
// 0x2 CTRL2    DIR4   DIR3   DIR2   DIR1   DIO4   DIO3   DIO2   DIO1
// 0x3 CTRL3    DGAIN2 DGAIN1 DGAIN0 NOSYSG NOSYSO NOSCG  NOSCO  RESERVED
//
// 0x4 DATA     D[23:16], D[15:8], D[7:0]
// 0x5 SOC      B[23:16], B[15:8], B[7:0]
// 0x6 SGC      B[23:16], B[15:8], B[7:0]
// 0x7 SCOC     B[23:16], B[15:8], B[7:0]
// 0x8 SCGC     B[23:16], B[15:8], B[7:0]
// ------------------------------------------------------------------------

#define START 0b10000000 //Start bit
#define READ  0b00000001 //Read bit

// REGISTER SELECTION (MODE = 1)
#define STAT1 0b11000000 // reg size = 8 bits    (RO, general chip operational status)
#define CTRL1 0b11000010 // reg size = 8 bits    (RW, FREQ, UNI/BI, INT/EXT CLK, ENBL BUFF, DATA FORMAT, SINGLE / CONT MODE)
#define CTRL2 0b11000100 // reg size = 8 bits    (RW,FOR GPIO pins)
#define CTRL3 0b11000110 // reg size = 8 bits    (RW,Calibration & Prog. Gain)
#define DATA_ 0b11001000 // reg size = 24 bits   (RO, MSB first Data Outpt)
#define SOC   0b11001010 // reg size = 24 bits   (RW,System Offset Calibration)
#define SGC   0b11001100 // reg size = 24 bits   (RW,System Gain Calibration)
#define SCOC  0b11001110 // reg size = 24 bits   (RW,Self-calibration Offset)
#define SCGC  0b11010000 // reg size = 24 bits   (RW,Self-calibration Gain)

// COMMAND BYTES  (MODE = 0, LINEF = 0)
#define SELF_CALIB        0b10010000  //CAL0
#define SYS_OFFSET_CALIB  0b10100000  //CAL1
#define SYS_GAIN_CALIB    0b10110000  //CAL0 & CAL1
#define POWER_DOWN        0b10001000  //IMPD
    //SAMPLIG SPEED
#define MEASURE_1_SPS     0b10000000
#define MEASURE_2p5_SPS   0b10000001
#define MEASURE_5_SPS     0b10000010
#define MEASURE_10_SPS    0b10000011
#define MEASURE_15_SPS    0b10000100
#define MEASURE_30_SPS    0b10000101
#define MEASURE_60_SPS    0b10000110
#define MEASURE_120_SPS   0b10000111

//STAT1
#define SYSOR             0b10000000
#define OR_               0b00001000
#define UR                0b00000100
#define MSTAT             0b00000010
#define RDY               0b00000001

//CTRL1 COMMAND BYTES
#define LINEF             0b10000000    //50 Hz
#define U_B               0b01000000    //Unipolar
#define EXTCLK            0b00100000    //External Clock
#define REFBUF            0b00010000    //Reference Buffer
#define SIGBUF            0b00001000    //Signal Buffer
#define FORMAT            0b00000100    //Offset binary format
#define SCYCLE            0b00000010    //Single-conversion mode
#define CTRL1_DEFAULT     0b00000010

//CTRL2 COMMAND BYTES (GPIO Control)
#define DIR4              0b10000000    //Pin 4 Set as Output
#define DIR3              0b01000000    //Pin 3 Set as Output
#define DIR2              0b00100000    //Pin 2 Set as Output
#define DIR1              0b00010000    //Pin 1 Set as Output
#define DIO4              0b00001000
#define DIO3              0b00000100
#define DIO2              0b00000010
#define DIO1              0b00000001
#define CTRL2_DEFAULT     0b00001111

//CTRL3 COMMAND BYTES (Gain & Calibration)
#define GAIN_1            0b00000000
#define GAIN_2            0b00100000
#define GAIN_4            0b01000000
#define GAIN_8            0b01100000
#define GAIN_16           0b10000000
#define NOSYSG            0b00010000     //Disables the use of the system gain
#define NOSYSO            0b00001000     //Disables the use of the system offset
#define NOSCG             0b00000100     //Disables the use of the self-calibration gain
#define NOSCO             0b00000010     //Disables the use of the self-calibration offset
#define CTRL3_DEFAULT     0b00011110

#endif /* __MAX11210_H */
