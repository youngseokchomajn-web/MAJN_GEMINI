#ifndef LSM6DSOX_H
#define LSM6DSOX_H

#include <stdint.h>

// LSM6DSOX Registers
#define REG_WHO_AM_I        0x0F
#define REG_CTRL1_XL        0x10
#define REG_CTRL2_G         0x11
#define REG_INT1_CTRL       0x0D
#define REG_INT2_CTRL       0x0E
#define REG_OUTX_L_A        0x28
#define REG_OUTX_H_A        0x29
#define REG_OUTY_L_A        0x2A
#define REG_OUTY_H_A        0x2B
#define REG_OUTZ_L_A        0x2C
#define REG_OUTZ_H_A        0x2D
#define REG_TAP_CFG0        0x56
#define REG_TAP_CFG1        0x57
#define REG_TAP_CFG2        0x58
#define REG_TAP_THS_6D      0x59
#define REG_INT_DUR2        0x5A
#define REG_WAKE_UP_THS     0x5B
#define REG_WAKE_UP_DUR     0x5C
#define REG_FREE_FALL       0x5D
#define REG_MD1_CFG         0x5E

// Struct to store 3-axis accelerometer raw data
struct AccelData {
    int16_t x;
    int16_t y;
    int16_t z;
    float x_g;
    float y_g;
    float z_g;
};

class LSM6DSOX {
public:
    LSM6DSOX(int csPin);
    
    // Initialize SPI interface and setup accelerometer
    bool begin();
    
    // Read raw 16-bit 3-axis accelerometer data
    bool readAccel(AccelData &data);
    
    // Configure hardware interrupt on INT1 for Free Fall / Shock safety detection
    // When a severe impact or drop is detected, INT1 will assert HIGH to trigger ESP32 ISR
    bool configureSafetyInterrupt(float threshold_g, uint8_t duration_ms);

private:
    int _cs;
    uint8_t readRegister(uint8_t reg);
    void writeRegister(uint8_t reg, uint8_t value);
    void select();
    void deselect();
};

#endif // LSM6DSOX_H
