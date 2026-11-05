#include <iostream>
#include <cassert>
#include <vector>
#include <string>
#include <map>
#include "../include/majn_power_state_machine.h"
#include "../include/majn_amplifier_driver.h"
#include "../include/majn_safety_supervisor.h"

using namespace Majn;

/**
 * @brief High-fidelity Mock Hardware Abstraction Layer
 */
class MockHardwareInterface : public IHardwareInterface {
public:
    std::map<int, int> pinModes;
    std::map<int, int> pinValues;
    std::map<uint8_t, std::map<uint8_t, uint8_t>> i2cRegisters;
    std::vector<std::string> logMessages;
    uint32_t simulatedMillis = 0;
    bool forceI2cNack = false;

    void setPinMode(int pin, int mode) override {
        pinModes[pin] = mode;
    }

    void writePin(int pin, int value) override {
        pinValues[pin] = value;
    }

    int readPin(int pin) override {
        return pinValues[pin];
    }

    void delayMs(uint32_t ms) override {
        simulatedMillis += ms;
    }

    uint32_t getMillis() override {
        return simulatedMillis;
    }

    bool i2cWriteRegister(uint8_t addr, uint8_t reg, uint8_t val) override {
        if (forceI2cNack) return false;
        i2cRegisters[addr][reg] = val;
        return true;
    }

    bool i2cReadRegister(uint8_t addr, uint8_t reg, uint8_t &val) override {
        if (forceI2cNack) return false;
        if (i2cRegisters.find(addr) != i2cRegisters.end() &&
            i2cRegisters[addr].find(reg) != i2cRegisters[addr].end()) {
            val = i2cRegisters[addr][reg];
            return true;
        }
        val = 0x00;
        return true;
    }

    void logMessage(const char *msg) override {
        logMessages.push_back(std::string(msg));
        // std::cout << msg << std::endl;
    }
};

void test_cold_boot_sequencing() {
    std::cout << "[TEST] Running cold boot and sequencing test..." << std::endl;
    MockHardwareInterface hal;
    HardwarePinConfig pins{4, 13, 35, 21, 27, 26, 25, 22};
    // Default GPIO35 is HIGH (No fault via 4.7k pull-up R12)
    hal.pinValues[35] = 1;

    PowerStateMachine fsm(hal, pins);
    assert(fsm.getState() == PowerState::BOOT_COLD);

    fsm.initialize();
    // After initialize(), Boost is enabled (GPIO4=1), in POWER_STABILIZING
    assert(hal.pinValues[4] == 1);
    assert(hal.pinValues[13] == 0); // PDN not enabled yet!
    assert(fsm.getState() == PowerState::POWER_STABILIZING);

    // Advance 25ms (exceeding BOOST_SETTLE_MS of 20ms)
    hal.simulatedMillis += 25;
    fsm.tick(hal.simulatedMillis);

    // Now PDN should be HIGH (GPIO13=1) and state should be STANDBY_SAFE
    assert(hal.pinValues[13] == 1);
    assert(fsm.getState() == PowerState::STANDBY_SAFE);
    assert(fsm.isOutputSafe() == true);
    std::cout << "  -> PASS: Cold boot sequence correctly staggers Boost and PDN." << std::endl;
}

void test_hardware_fault_pin3_interrupt() {
    std::cout << "[TEST] Running TAS5805M Pin 3 FAULTz hardware interrupt test..." << std::endl;
    MockHardwareInterface hal;
    HardwarePinConfig pins{4, 13, 35, 21, 27, 26, 25, 22};
    hal.pinValues[35] = 1; // Normal High via R12

    PowerStateMachine fsm(hal, pins);
    fsm.initialize();
    hal.simulatedMillis += 25;
    fsm.tick(hal.simulatedMillis);
    assert(fsm.getState() == PowerState::STANDBY_SAFE);

    // Start running
    assert(fsm.requestStart() == true);
    assert(fsm.getState() == PowerState::RUNNING_ACTIVE);

    // Simulate TAS5805M pulling Pin 3 LOW (OTW/OCP hardware event)
    hal.pinValues[35] = 0;
    fsm.tick(hal.simulatedMillis);

    // State machine must immediately clamp both Boost and PDN to 0
    assert(fsm.getState() == PowerState::EMERGENCY_SHUTDOWN);
    assert(hal.pinValues[4] == 0);
    assert(hal.pinValues[13] == 0);
    assert((fsm.getFaultMask() & static_cast<uint32_t>(FaultSource::AMP_HARDWARE_FAULT_ISR)) != 0);
    std::cout << "  -> PASS: Pin 3 active-low trip triggers immediate hardware emergency shutdown." << std::endl;
}

void test_volume_clamp_enforcement() {
    std::cout << "[TEST] Running Volume Limiter (-3.5dBFS) clamp test..." << std::endl;
    MockHardwareInterface hal;
    // Mock TAS5805M responding on 0x2C
    hal.i2cRegisters[0x2C][0x00] = 0x00;

    AmplifierDriver amp(hal);
    assert(amp.probeAndInitialize() == true);
    assert(amp.getActiveAddress() == 0x2C);

    // Request 100% volume
    amp.setVolumeClamped(100);
    // Register 0x4C must be clamped at 0x37 (-3.5dBFS), NEVER 0x30 (0dBFS) or lower!
    uint8_t regVol = hal.i2cRegisters[0x2C][0x4C];
    assert(regVol == 0x37);

    // Request 0% volume (Mute)
    amp.setVolumeClamped(0);
    regVol = hal.i2cRegisters[0x2C][0x4C];
    assert(regVol == 0xFF);
    std::cout << "  -> PASS: Volume register strictly clamped at 0x37 (-3.5dBFS max)." << std::endl;
}

void test_safety_supervisor_watchdog_and_30min_limit() {
    std::cout << "[TEST] Running Watchdog & 30-minute KC limit supervisor test..." << std::endl;
    MockHardwareInterface hal;
    HardwarePinConfig pins{4, 13, 35, 21, 27, 26, 25, 22};
    hal.pinValues[35] = 1;

    PowerStateMachine fsm(hal, pins);
    fsm.initialize();
    hal.simulatedMillis += 25;
    fsm.tick(hal.simulatedMillis);
    fsm.requestStart();

    hal.i2cRegisters[0x2C][0x00] = 0x00;
    AmplifierDriver amp(hal);
    assert(amp.probeAndInitialize() == true);
    SafetySupervisor supervisor(hal, fsm, amp);
    supervisor.initialize();

    // Test 1: Vibration target clamp
    supervisor.setVibrationTarget(250.0f /* Over limit */, 0.90f /* Over limit */);
    assert(supervisor.getTargetFrequency() == 120.0f); // Clamped to 120Hz
    assert(supervisor.getCurrentAmplitude() == 0.0f);  // Still ramped from 0

    // Step through 20ms ticks to test ramping
    for (int i = 0; i < 50; i++) {
        hal.simulatedMillis += 20;
        supervisor.petWatchdog();
        supervisor.tickSupervisor(hal.simulatedMillis, 0.02f);
    }
    assert(supervisor.getCurrentAmplitude() <= 0.50f);
    assert(supervisor.getCurrentAmplitude() >= 0.24f);

    // Test 2: 30-minute auto-stop
    hal.simulatedMillis += 31 * 60 * 1000; // Fast forward 31 minutes
    supervisor.petWatchdog();
    supervisor.tickSupervisor(hal.simulatedMillis, 0.02f);
    assert(fsm.getState() == PowerState::STANDBY_SAFE);

    // Test 3: Watchdog starvation (>5000ms without pet)
    fsm.requestStart();
    hal.simulatedMillis += 6000;
    supervisor.tickSupervisor(hal.simulatedMillis, 0.02f);
    assert(fsm.getState() == PowerState::EMERGENCY_SHUTDOWN);
    std::cout << "  -> PASS: Supervisor enforces frequency/amplitude caps, 30m cutoff, and watchdog." << std::endl;
}

int main() {
    std::cout << "=================================================" << std::endl;
    std::cout << "  MAJN PCB #0006 Firmware State Machine Unit Tests" << std::endl;
    std::cout << "=================================================" << std::endl;

    test_cold_boot_sequencing();
    test_hardware_fault_pin3_interrupt();
    test_volume_clamp_enforcement();
    test_safety_supervisor_watchdog_and_30min_limit();

    std::cout << "=================================================" << std::endl;
    std::cout << "  ALL FIRMWARE UNIT TESTS PASSED DETERMINISTICALLY" << std::endl;
    std::cout << "=================================================" << std::endl;
    return 0;
}
