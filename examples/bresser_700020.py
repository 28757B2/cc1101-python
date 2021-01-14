"""
Copyright (c) 2021

bresser_7000020.py

Example showing decoding of data packets from a Bresser 7000020 Weather Station using the CC1101

#### Packet Information (from https://github.com/merbanan/rtl_433/blob/master/src/devices/nexus.c)###

Nexus sensor protocol with ID, temperature and optional humidity
also FreeTec (Pearl) NC-7345 sensors for FreeTec Weatherstation NC-7344,
also infactory/FreeTec (Pearl) NX-3980 sensors for infactory/FreeTec NX-3974 station,
also Solight TE82S sensors for Solight TE76/TE82/TE83/TE84 stations,
also TFA 30.3209.02 temperature/humidity sensor.

The sensor sends 36 bits 12 times,
the packets are ppm modulated (distance coding) with a pulse of ~500 us
followed by a short gap of ~1000 us for a 0 bit or a long ~2000 us gap for a
1 bit, the sync gap is ~4000 us.

The data is grouped in 9 nibbles:

    [id0] [id1] [flags] [temp0] [temp1] [temp2] [const] [humi0] [humi1]

- The 8-bit id changes when the battery is changed in the sensor.
- flags are 4 bits B 0 C C, where B is the battery status: 1=OK, 0=LOW
- and CC is the channel: 0=CH1, 1=CH2, 2=CH3
- temp is 12 bit signed scaled by 10
- const is always 1111 (0x0F)
- humidity is 8 bits
"""

import bitstring
import time

from cc1101 import CC1101
from cc1101.config import RXConfig, Modulation

from typing import List

DEVICE = "/dev/cc1101.0.0"
FREQUENCY = 434.0
SYNC_WORD = 0x00 # No sync word - use default carrier sense threshold to trigger RX
PACKET_LENGTH = 1024

"""
Pulse width is ~500us = 500 * 10^-6

2 * (1 / 500 * 10^-6) = 4000 (4kbps)
"""
BAUD_RATE = 4

def decode_rx_bytes(rx_bytes: bytes) -> List[str]:
    """Decode the received bytes to a sequence of Bresser 7000020 packets (36-bit strings)"""

    # Convert the received bytes to a string of bits
    rx_bits = bitstring.BitArray(bytes=rx_bytes).bin

    packets = []

    bits = ""
    count = 0

    # Decode OOK by iterating over each bit
    for bit in rx_bits:
        # A sequence of 1's seperate each OOK-encoded bit
        if bit == "1":
            # 10 or more 0's indicates the start of a packet
            if count > 10:
                # Bresser 7000020 data packets are 36-bits
                if len(bits) == 36:
                    packets.append(bits)
                bits = ""
            # 4 or more 0's is an OOK 1
            elif count > 4:
                bits += "1"
            # 1 or more 0's is an OOK 0
            elif count > 0: 
                bits += "0"
            count = 0
        else:
            # Count the number of zeros
            count += 1
    
    return packets

# Create the RX config and device
rx_config = RXConfig(FREQUENCY, Modulation.OOK, BAUD_RATE, SYNC_WORD, PACKET_LENGTH)
radio = CC1101(DEVICE, rx_config)

# RX Loop
print("Receiving:")
while True:
    # Read bytes from the CC1101
    for rx_bytes in radio.receive():
        # Decode using OOK
        for packet in decode_rx_bytes(rx_bytes):
            # Decode the OOK decoded bitstrings based on the packet format 
            id, battery_ok, const0, channel, temperature, const1, humidity = bitstring.Bits(bin=packet).unpack("uint:8, bool:1, uint:1, uint:2, int:12, uint:4, uint:8")

            print(id, battery_ok, const0, channel, temperature, const1, humidity)
            
            # Basic data checks
            if channel in [0,1,2] and const0 == 0 and const1 == 0xF and humidity <= 100:
                print(f"ID: {id}\nChannel: {channel + 1}\nTemperature: {temperature / 10} °C\nHumidity: {humidity}%\nBattery: {'OK' if battery_ok else 'LOW'}\n")

    time.sleep(1)