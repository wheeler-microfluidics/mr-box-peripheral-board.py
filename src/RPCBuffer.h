#ifndef ___RPC_BUFFER__H___
#define ___RPC_BUFFER__H___

#include <stdint.h>




#ifdef __AVR_ATmega328P__


/* ## uno settings ## */
#ifndef PACKET_SIZE
#define PACKET_SIZE   80
#endif  // #ifndef PACKET_SIZE

#ifndef I2C_PACKET_SIZE
#define I2C_PACKET_SIZE   PACKET_SIZE
#endif  // #ifndef I2C_PACKET_SIZE

#ifndef COMMAND_ARRAY_BUFFER_SIZE
#define COMMAND_ARRAY_BUFFER_SIZE
#endif  // #ifndef COMMAND_ARRAY_BUFFER_SIZE


#elif __AVR_ATmega2560__

/* ## mega2560 settings ## */
#ifndef PACKET_SIZE
#define PACKET_SIZE   256
#endif  // #ifndef PACKET_SIZE

#ifndef I2C_PACKET_SIZE
#define I2C_PACKET_SIZE   PACKET_SIZE
#endif  // #ifndef I2C_PACKET_SIZE

#ifndef COMMAND_ARRAY_BUFFER_SIZE
#define COMMAND_ARRAY_BUFFER_SIZE
#endif  // #ifndef COMMAND_ARRAY_BUFFER_SIZE


#else


/* ## default settings ## */
#ifndef PACKET_SIZE
#define PACKET_SIZE   80
#endif  // #ifndef PACKET_SIZE

#ifndef I2C_PACKET_SIZE
#define I2C_PACKET_SIZE   PACKET_SIZE
#endif  // #ifndef I2C_PACKET_SIZE

#ifndef COMMAND_ARRAY_BUFFER_SIZE
#define COMMAND_ARRAY_BUFFER_SIZE
#endif  // #ifndef COMMAND_ARRAY_BUFFER_SIZE


#endif


#endif  // #ifndef ___RPC_BUFFER__H___
