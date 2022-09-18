# cc1101-python

This project provides an interface to the [CC1101 Linux Driver](https://github.com/28757B2/cc1101-driver) to allow receiving and transmitting packets from Python.

## Setup

    pip3 install cc1101-python

# Command Line

    python3 -m cc1101 {tx,rx,config,reset}

## config
Retreive the current configuration from the driver.

`rx` and `tx` print the human-readable configuration options.

`rx_raw` and `tx_raw` print the register values of the CC1101 for the current RX and TX configs.

`dev_raw` prints the current register values of the hardware.

## reset
Clear the RX and TX configs and reset the radio hardware.

## tx/rx

Transmits or receives packets.

###  Common Options

#### `device`
The path to a `/dev/cc1101.x.x` interface provided by the driver.

#### `frequency`
The frequency to receive/transmit on. Valid values are 300-348, 387-464 and 779-928 MHz.

#### `modulation`
The modulation scheme to use. Valid values are OOK, FSK_2, FSK_4, GFSK, MSK.

#### `baud_rate`
The data rate in kBaud to receive/transmit packets. Valid values are within the range 0.6-500 and depend on modulation:

| Modulation | Baud Rate |
|------------|-----------|
| OOK / GFSK | 0.6 - 250 |
| 2FSK       | 0.6 - 500 |
| 4FSK       | 0.6 - 300 |
| MSK        | 26 - 500  |

#### `--sync_word`
The Sync Word to use, specified as a two or four byte hexadecimal value (e.g `0f0f`). If four bytes are used, the upper and lower two bytes must be the same (e.g `0f0f0f0f`) 

In RX, the device searches for the specified sync word to begin reception. Set `0x00` to disable the sync word.

In TX, the sync word is preprended to each packet.

#### `--deviation`
When using an FSK modulation, sets the deviation in kHz either side of the provided frequency to use for modulation. 

### `rx` Options

#### `packet_length`
The number of bytes the radio will receive once RX is triggered, either via sync word or carrier sense threshold. 

#### `--bandwidth`
Sets the receive bandwidth in kHz. Valid values are

    58,67,81,101,116,135,162,203,232,270,325,406,464,541,650,812

#### `--carrier-sense`
Sets the carrier sense threshold in dB required to begin RX. Carrier sense can be set to a relative or an absolute value. When a sync word is provided, RX only begins when the carrier sense is above the threshold and the sync word has been received.

Not specifying a value disables carrier sense.

Relative values are `+6`, `+10` and `+14`. These cause the radio to begin RX when the Received Signal Strength Indicator (RSSI) suddenly increases by this value. This is the easiest mode to use for basic RX.

Absolute values are `-7` to `7` dB. These values cause the radio to begin RX when the RSSI exceeds the absolute value specified by `--magn-target` +/- the carrier-sense value. Using absolute carrier sense will likely require adjusting the `--magn-target`, `--max-lna-gain` and `--max-dvga-gain` experimentally until the required RSSI range is reached. `--out-format rssi` can be used to help find this. See Section 17.4 of the [CC1101 Datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf) for examples.

#### `--magn-target`
Sets the target channel filter amplitude in dB. Valid values are:

    24, 27, 30, 33, 36, 38, 40, 42

#### `--max-lna-gain`
Decreases the maximum LNA gain by approximately the specified amount in dB.

Valid values are:

    0, 3, 6, 7, 9, 12, 15, 17

#### `--max-dvga-gain`
Decreases the maximum DVGA gain by approximately the specified amount in dB.

Valid values are:

    0, 6, 12, 18

#### `--block`
Hold the device handle open while receiving. This prevents another process from using or reconfiguring the device, but prevents multiplexing of RX/TX on a single device between two processes. 

#### `--out-format`
Set the output format. 

`info` prints the packet received count, Received Signal Strength Indictator (RSSI) and the hexadecimal representation of each packet as it is received.

`hex` prints the packet as hexadecimal.

`bin` outputs the raw packet bytes to stdout. This is useful for piping into other tools.

`rssi` continually outputs the current value of RSSI.

### `tx` Options

#### `frequency`
Frequency to transmit on. In TX mode, frequencies are by default restricted to 315/433/868/915 MHz +/- 1MHz, which allows specifying TX Power as one of the dBm values listed in [TI DN013](https://www.ti.com/lit/an/swra151a/swra151a.pdf). This checking can be disabled by using the `--raw` flag.

#### `tx_power`
The power in dBm to use for transmission. Values must match one of the values in the appropriate frequency table of [TI DN013](https://www.ti.com/lit/an/swra151a/swra151a.pdf).

#### `packet`
A sequence of bytes in hexadecimal form to transmit using the CC1101.

#### `--raw`
In `--raw` mode, `tx_power` is provided as a single byte in hexadecimal, which will be directly set in the CC1101's `PATABLE`. Any valid frequency value can be used.

## RX Example
    python3 -m cc1101 rx /dev/cc1101.0.0 433 OOK 1 64

## TX Example
    python3 -m cc1101 tx /dev/cc1101.0.0 433 OOK 1 1.4 0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f

# Python Library
These examples show how to integrate the CC1101 into Python programs.

## Receive
```python
from time import sleep
from binascii import hexlify

from cc1101.config import RXConfig, Modulation
from cc1101 import CC1101

rx_config = RXConfig(frequency=434, modulation=Modulation.OOK, baud_rate=1, sync_word=0x0000, packet_length=64)
radio = CC1101("/dev/cc1101.0.0", rx_config, blocking=True)

while True:
    packets = radio.receive()

    for packet in packets:
        print(f"Received - {hexlify(packet)}")
    
    sleep(0.1)
```


## Transmit
```python
from binascii import unhexlify

from cc1101.config import TXConfig, Modulation
from cc1101 import CC1101

tx_config = TXConfig.from_ism(frequency=434, modulation=Modulation.OOK, baud_rate=1, tx_power=0.1)
radio = CC1101("/dev/cc1101.0.0")

radio.transmit(tx_config, unhexlify("0f0f0f0f0f0f0f0f0f0f0f"))
```
