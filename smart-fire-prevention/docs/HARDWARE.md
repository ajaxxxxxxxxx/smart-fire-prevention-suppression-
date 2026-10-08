# Hardware Connections (ESP32)

| Component            | ESP32 Pin | Notes                                   |
|----------------------|-----------|-----------------------------------------|
| DHT22 data           | GPIO 4    | 10k pull-up to 3.3V                     |
| MQ-2 analog out (AO) | GPIO 34   | Needs 5V supply; use voltage divider    |
| Flame sensor (DO)    | GPIO 27   | LOW = flame detected                    |
| Buzzer               | GPIO 26   | Via transistor if high current          |
| Relay IN             | GPIO 25   | Drives water pump / solenoid valve      |

**Safety:** power the pump from a separate supply, isolate mains from low-voltage
electronics, and never rely on this prototype as the only fire-protection system.

## MQTT Topics
| Topic                | Direction       | Payload                                                        |
|----------------------|-----------------|----------------------------------------------------------------|
| `fire/node1/sensors` | ESP32 -> Server | `{"temp":31.2,"hum":55,"gas":820,"flame":false,"pump":false}` |
| `fire/node1/cmd`     | Server -> ESP32 | `PUMP_ON`, `PUMP_OFF`, `ALERT`, `CLEAR`                        |
