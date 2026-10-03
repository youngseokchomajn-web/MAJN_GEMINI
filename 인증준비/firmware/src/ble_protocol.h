#pragma once

#include <Arduino.h>

namespace MajnBle {
static constexpr uint8_t PROTOCOL_VERSION = 1;

static constexpr char SERVICE_UUID[] = "7b4d0001-7a6a-4d41-9a4d-4d414a4a4e01";
static constexpr char COMMAND_UUID[] = "7b4d0002-7a6a-4d41-9a4d-4d414a4a4e01";
static constexpr char TELEMETRY_UUID[] = "7b4d0003-7a6a-4d41-9a4d-4d414a4a4e01";
static constexpr char EVENT_UUID[] = "7b4d0004-7a6a-4d41-9a4d-4d414a4a4e01";

static constexpr uint32_t HEARTBEAT_TIMEOUT_MS = 5000;
static constexpr uint32_t TELEMETRY_PERIOD_MS = 200;

enum class SystemState : uint8_t {
    BOOT,
    SELF_TEST,
    READY,
    RUNNING,
    FAULT
};
}
