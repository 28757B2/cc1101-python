"""
Copyright (c) 2021
"""

import math
import struct

from enum import IntEnum
from typing import Dict, List, Tuple, TypeVar, Type, Optional, Any

# Crystal frequency of 26 Mhz
XTAL_FREQ = 26
DEFAULT_DEVIATION = 47.607422
DEFAULT_BANDWIDTH = 203
DEFAULT_SYNC_WORD = 0x0000
DEFAULT_MAX_LNA_GAIN = 0
DEFAULT_MAX_DVGA_GAIN = 0
DEFAULT_MAGN_TARGET = 33
DEFAULT_CARRIER_SENSE = 10

# Valid TX powers from Design Note DN013
# fmt: off
TX_POWERS_315 = {
    0xC0:  10.6, 0xC1:  10.3, 0xC2:   9.9, 0xC3:   9.6, 0xC4:   9.2, 0xC5:   8.8, 0xC6:   8.5, 0xC7:   8.2,
    0xC8:   7.9, 0xC9:   7.5, 0xCA:   7.2, 0xCB:   6.9, 0xCC:   6.6, 0x80:   6.6, 0x81:   6.3, 0xCD:   6.3,
    0x82:   6.0, 0x83:   5.8, 0xCE:   5.6, 0x84:   5.4, 0x85:   5.0, 0x86:   4.7, 0x87:   4.3, 0x88:   3.9,
    0x89:   3.5, 0x8A:   3.1, 0xCF:   2.8, 0x8B:   2.7, 0x8C:   2.2, 0x8D:   1.7, 0x50:   0.7, 0x8E:   0.6,
    0x60:   0.5, 0x51:   0.1, 0x61:  -0.1, 0x40:  -0.3, 0x52:  -0.5, 0x62:  -0.7, 0x3F:  -0.8, 0x3E:  -1.0,
    0x53:  -1.1, 0x3D:  -1.3, 0x63:  -1.3, 0x3C:  -1.7, 0x54:  -1.7, 0x64:  -1.9, 0x3B:  -2.1, 0x55:  -2.3,
    0x65:  -2.5, 0x2F:  -2.6, 0x3A:  -2.7, 0x56:  -3.0, 0x2E:  -3.1, 0x66:  -3.1, 0x39:  -3.4, 0x57:  -3.5,
    0x2D:  -3.6, 0x67:  -3.7, 0x8F:  -4.2, 0x2C:  -4.2, 0x38:  -4.3, 0x68:  -4.3, 0x2B:  -4.9, 0x69:  -4.9,
    0x37:  -5.4, 0x6A:  -5.5, 0x2A:  -5.7, 0x6B:  -6.1, 0x29:  -6.5, 0x6C:  -6.7, 0x36:  -6.7, 0x6D:  -7.2,
    0x28:  -7.5, 0x35:  -8.1, 0x6E:  -8.4, 0x27:  -8.6, 0x26:  -9.8, 0x34:  -9.9, 0x25: -11.1, 0x33: -12.2,
    0x24: -13.0, 0x6F: -13.2, 0x1F: -13.3, 0x1E: -13.9, 0x1D: -14.5, 0x1C: -15.2, 0x23: -15.4, 0x32: -15.6,
    0x1B: -15.9, 0x1A: -16.6, 0x19: -17.5, 0x18: -18.5, 0x22: -18.8, 0x0F: -18.8, 0x0E: -19.4, 0x17: -19.6,
    0x0D: -20.0, 0x0C: -20.7, 0x16: -20.9, 0x31: -21.3, 0x0B: -21.4, 0x0A: -22.2, 0x15: -22.4, 0x09: -23.0,
    0x08: -24.0, 0x14: -24.3, 0x21: -24.5, 0x07: -25.1, 0x06: -26.4, 0x13: -26.6, 0x05: -27.7, 0x04: -29.6,
    0x12: -29.8, 0x03: -31.7, 0x02: -34.6, 0x11: -34.6, 0x01: -38.3, 0x10: -41.2, 0x30: -41.3, 0x20: -41.3,
    0x00: -63.8
}

TX_POWERS_433 = {
    0xC0:   9.9, 0xC1:   9.5, 0xC2:   9.2, 0xC3:   8.8, 0xC4:   8.5, 0xC5:   8.1, 0xC6:   7.8, 0xC7:   7.4,
    0xC8:   7.1, 0xC9:   6.8, 0xCA:   6.4, 0x80:   6.3, 0xCB:   6.1, 0x81:   6.0, 0xCC:   5.8, 0x82:   5.8,
    0xCD:   5.5, 0x83:   5.5, 0x84:   5.1, 0xCE:   4.9, 0x85:   4.8, 0x86:   4.4, 0x87:   4.0, 0x88:   3.6,
    0x89:   3.2, 0x8A:   2.8, 0x8B:   2.3, 0xCF:   2.0, 0x8C:   1.9, 0x8D:   1.4, 0x8E:   0.4, 0x50:   0.4,
    0x60:   0.1, 0x51:  -0.3, 0x61:  -0.5, 0x40:  -0.8, 0x52:  -0.9, 0x62:  -1.1, 0x3E:  -1.4, 0x53:  -1.5,
    0x63:  -1.7, 0x3C:  -2.1, 0x54:  -2.2, 0x64:  -2.3, 0x3B:  -2.5, 0x55:  -2.8, 0x65:  -2.9, 0x2F:  -3.0,
    0x3A:  -3.1, 0x56:  -3.3, 0x66:  -3.5, 0x39:  -3.8, 0x2D:  -4.0, 0x67:  -4.1, 0x8F:  -4.6, 0x68:  -4.7,
    0x69:  -5.3, 0x37:  -5.6, 0x6A:  -5.9, 0x2A:  -6.0, 0x6B:  -6.5, 0x36:  -6.8, 0x29:  -6.9, 0x6C:  -7.1,
    0x6D:  -7.7, 0x28:  -7.8, 0x35:  -8.3, 0x27:  -8.7, 0x6E:  -8.9, 0x26:  -9.9, 0x34: -10.1, 0x25: -11.4,
    0x33: -12.3, 0x24: -13.3, 0x1F: -13.7, 0x1E: -14.3, 0x1D: -14.9, 0x1C: -15.5, 0x23: -15.6, 0x32: -15.7,
    0x1B: -16.2, 0x1A: -17.0, 0x19: -17.8, 0x18: -18.8, 0x22: -19.0, 0x0F: -19.3, 0x0E: -19.8, 0x0D: -20.4,
    0x16: -21.0, 0x31: -21.3, 0x0B: -21.7, 0x0A: -22.5, 0x09: -23.3, 0x14: -24.3, 0x21: -24.5, 0x07: -25.3,
    0x13: -26.5, 0x05: -27.9, 0x04: -29.5, 0x12: -29.6, 0x03: -31.4, 0x02: -33.8, 0x01: -36.5, 0x20: -38.3,
    0x30: -38.4, 0x00: -62.7
}

TX_POWERS_868 = {
    0xC0:  10.7, 0xC1:  10.3, 0xC2:  10.0, 0xC3:   9.6, 0xC4:   9.2, 0xC5:   8.9, 0xC6:   8.5, 0xC7:   8.2,
    0xC8:   7.8, 0xC9:   7.5, 0xCA:   7.2, 0xCB:   6.8, 0xCC:   6.5, 0xCD:   6.2, 0xCE:   5.5, 0x80:   5.2,
    0x81:   5.0, 0x82:   4.8, 0x83:   4.6, 0x84:   4.4, 0x85:   4.1, 0x86:   3.7, 0x87:   3.4, 0x88:   3.0,
    0x89:   2.6, 0xCF:   2.4, 0x8A:   2.1, 0x8B:   1.7, 0x8C:   1.1, 0x8D:   0.6, 0x50:  -0.3, 0x60:  -0.5,
    0x8E:  -0.5, 0x51:  -0.9, 0x61:  -1.1, 0x40:  -1.5, 0x52:  -1.6, 0x62:  -1.8, 0x53:  -2.3, 0x63:  -2.4,
    0x3F:  -2.6, 0x3E:  -2.8, 0x54:  -2.9, 0x64:  -3.1, 0x3D:  -3.2, 0x3C:  -3.5, 0x55:  -3.6, 0x65:  -3.7,
    0x3B:  -4.0, 0x56:  -4.2, 0x66:  -4.4, 0x2F:  -4.5, 0x3A:  -4.5, 0x57:  -4.8, 0x2E:  -4.9, 0x67:  -5.0,
    0x39:  -5.2, 0x2D:  -5.5, 0x68:  -5.7, 0x8F:  -6.0, 0x2C:  -6.0, 0x38:  -6.1, 0x69:  -6.3, 0x2B:  -6.7,
    0x6A:  -6.9, 0x37:  -6.9, 0x2A:  -7.4, 0x6B:  -7.5, 0x36:  -8.1, 0x29:  -8.2, 0x6C:  -8.7, 0x28:  -9.0,
    0x35:  -9.4, 0x27:  -9.8, 0x26: -11.0, 0x34: -11.1, 0x25: -12.5, 0x33: -13.3, 0x24: -14.3, 0x6D: -14.5,
    0x1F: -14.6, 0x1E: -15.1, 0x1D: -15.7, 0x1C: -16.4, 0x23: -16.5, 0x32: -16.5, 0x1B: -17.0, 0x1A: -17.8,
    0x19: -18.6, 0x18: -19.5, 0x22: -19.6, 0x0F: -20.0, 0x0E: -20.5, 0x17: -20.5, 0x0D: -21.1, 0x0C: -21.7,
    0x16: -21.7, 0x31: -21.9, 0x0B: -22.3, 0x0A: -23.0, 0x15: -23.0, 0x09: -23.8, 0x08: -24.6, 0x14: -24.7,
    0x21: -24.8, 0x07: -25.5, 0x13: -26.5, 0x06: -26.5, 0x05: -27.7, 0x12: -28.9, 0x04: -28.9, 0x03: -30.2,
    0x02: -31.7, 0x11: -31.7, 0x01: -33.1, 0x10: -34.1, 0x20: -34.1, 0x30: -34.2, 0x6E: -45.8, 0x00: -59.3,
    0x6F: -69.2
}

TX_POWERS_915 = {
    0xC0:   9.4, 0xC1:   9.0, 0xC2:   8.6, 0xC3:   8.3, 0xC4:   7.9, 0xC5:   7.6, 0xC6:   7.2, 0xC7:   6.9,
    0xC8:   6.6, 0xC9:   6.2, 0xCA:   5.9, 0xCB:   5.6, 0xCC:   5.3, 0xCD:   5.0, 0x80:   4.9, 0x81:   4.7,
    0x82:   4.5, 0xCE:   4.3, 0x83:   4.2, 0x84:   3.9, 0x85:   3.6, 0x86:   3.3, 0x87:   2.9, 0x88:   2.5,
    0x89:   2.2, 0x8A:   1.8, 0xCF:   1.6, 0x8B:   1.3, 0x8C:   0.9, 0x8D:   0.5, 0x8E:  -0.6, 0x50:  -0.9,
    0x60:  -1.1, 0x51:  -1.6, 0x61:  -1.8, 0x40:  -2.1, 0x52:  -2.2, 0x62:  -2.4, 0x3F:  -2.5, 0x3E:  -2.7,
    0x53:  -2.9, 0x3D:  -3.0, 0x63:  -3.0, 0x3C:  -3.4, 0x22: -19.4, 0x0F: -19.7, 0x0E: -20.2, 0x17: -20.3,
    0x0D: -20.8, 0x0C: -21.4, 0x16: -21.4, 0x31: -21.7, 0x0B: -22.0, 0x0A: -22.7, 0x15: -22.8, 0x09: -23.5,
    0x6D: -23.8, 0x08: -24.3, 0x14: -24.4, 0x21: -24.6, 0x07: -25.2, 0x13: -26.2, 0x06: -26.2, 0x05: -27.3,
    0x12: -28.6, 0x04: -28.6, 0x03: -29.8, 0x02: -31.2, 0x11: -31.3, 0x01: -32.7, 0x10: -33.6, 0x20: -33.7,
    0x30: -33.7, 0x00: -58.2, 0x6E: -64.5, 0x6F: -69.7
}
# fmt: on


class Registers(IntEnum):
    """Mapping of register name to address
    Extracted from SmartRF studio using @RN@@<<@= 0x@AH@ config string
    """

    IOCFG2 = 0x00  # GDO2 Output Pin Configuration
    IOCFG1 = 0x01  # GDO1 Output Pin Configuration
    IOCFG0 = 0x02  # GDO0 Output Pin Configuration
    FIFOTHR = 0x03  # RX FIFO and TX FIFO Thresholds
    SYNC1 = 0x04  # Sync Word, High Byte
    SYNC0 = 0x05  # Sync Word, Low Byte
    PKTLEN = 0x06  # Packet Length
    PKTCTRL1 = 0x07  # Packet Automation Control
    PKTCTRL0 = 0x08  # Packet Automation Control
    ADDR = 0x09  # Device Address
    CHANNR = 0x0A  # Channel Number
    FSCTRL1 = 0x0B  # Frequency Synthesizer Control
    FSCTRL0 = 0x0C  # Frequency Synthesizer Control
    FREQ2 = 0x0D  # Frequency Control Word, High Byte
    FREQ1 = 0x0E  # Frequency Control Word, Middle Byte
    FREQ0 = 0x0F  # Frequency Control Word, Low Byte
    MDMCFG4 = 0x10  # Modem Configuration
    MDMCFG3 = 0x11  # Modem Configuration
    MDMCFG2 = 0x12  # Modem Configuration
    MDMCFG1 = 0x13  # Modem Configuration
    MDMCFG0 = 0x14  # Modem Configuration
    DEVIATN = 0x15  # Modem Deviation Setting
    MCSM2 = 0x16  # Main Radio Control State Machine Configuration
    MCSM1 = 0x17  # Main Radio Control State Machine Configuration
    MCSM0 = 0x18  # Main Radio Control State Machine Configuration
    FOCCFG = 0x19  # Frequency Offset Compensation Configuration
    BSCFG = 0x1A  # Bit Synchronization Configuration
    AGCCTRL2 = 0x1B  # AGC Control
    AGCCTRL1 = 0x1C  # AGC Control
    AGCCTRL0 = 0x1D  # AGC Control
    WOREVT1 = 0x1E  # High Byte Event0 Timeout
    WOREVT0 = 0x1F  # Low Byte Event0 Timeout
    WORCTRL = 0x20  # Wake On Radio Control
    FREND1 = 0x21  # Front End RX Configuration
    FREND0 = 0x22  # Front End TX Configuration
    FSCAL3 = 0x23  # Frequency Synthesizer Calibration
    FSCAL2 = 0x24  # Frequency Synthesizer Calibration
    FSCAL1 = 0x25  # Frequency Synthesizer Calibration
    FSCAL0 = 0x26  # Frequency Synthesizer Calibration
    RCCTRL1 = 0x27  # RC Oscillator Configuration
    RCCTRL0 = 0x28  # RC Oscillator Configuration
    FSTEST = 0x29  # Frequency Synthesizer Calibration Control
    PTEST = 0x2A  # Production Test
    AGCTEST = 0x2B  # AGC Test
    TEST2 = 0x2C  # Various Test Settings
    TEST1 = 0x2D  # Various Test Settings
    TEST0 = 0x2E  # Various Test Settings


CONFIG_SIZE = 0x2F


class Modulation(IntEnum):
    """CC1101 modulation modes"""

    FSK_2 = 0
    GFSK = 1
    OOK = 3
    FSK_4 = 4
    MSK = 7

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls: Type["Modulation"], s: str) -> "Modulation":
        try:
            return cls[s]
        except:
            raise ValueError()


class CarrierSenseMode(IntEnum):
    DISABLED = 0
    RELATIVE = 1
    ABSOLUTE = 2

class CommonConfig:
    """Class for common configuration properties shared by TX and RX

    typedef struct {
        unsigned frequency;
        unsigned char modulation;
        unsigned char baud_rate_mantissa;
        unsigned char baud_rate_exponent;
        unsigned char deviation_mantissa;
        unsigned char deviation_exponent;
        unsigned long sync_word;
    } cc1101_common_config_t;
    """

    COMMON_STRUCT_FORMAT: str = "IBBBBBL"
    STRUCT_FORMAT: str = ""
    _frequency: float
    _modulation: Modulation
    _baud_rate: float
    _deviation: float
    _sync_word: int

    T = TypeVar("T", bound="CommonConfig")

    def __init__(
        self,
        frequency: float,
        modulation: int,
        baud_rate: float,
        deviation: float,
        sync_word: int,
    ):
        self.frequency = frequency
        self._modulation = Modulation(modulation)
        self.baud_rate = baud_rate
        self.deviation = deviation
        self.sync_word = sync_word

    @staticmethod
    def validate_frequency(frequency: float) -> None:
        """Validate a frequency

        Values taken from SmartRF Studio
        """
        if not (
            (frequency >= 299.999756 and frequency <= 347.99993)
            or (frequency >= 386.999939 and frequency <= 463.999786)
            or (frequency >= 778.999878 and frequency <= 928.000000)
        ):
            raise ValueError(
                "frequency must be between 300-348 MHz, 387-464 MHz or 779-928 MHz"
            )

    @staticmethod
    def frequency_to_config(frequency: float) -> int:
        """Convert a frequency in MHz to a configuration value

        Uses the formula from section 21 of the CC1101 datasheet
        """
        CommonConfig.validate_frequency(frequency)
        multiplier = (frequency * 2 ** 16) / XTAL_FREQ
        return int(multiplier)

    @staticmethod
    def config_to_frequency(config: int) -> float:
        """Convert a configuration value to a frequency in MHz

        Uses the formula from section 21 of the CC1101 datasheet
        """
        return round((XTAL_FREQ / 2 ** 16) * config, 6)

    @property
    def frequency(self) -> float:
        """Get the configured frequency"""
        return self._frequency

    @frequency.setter
    def frequency(self, frequency: float) -> None:
        """Set the frequency"""
        self.validate_frequency(frequency)
        self._frequency = frequency

    @property
    def modulation(self) -> Modulation:
        """Get the configured modulation mode"""
        return self._modulation

    @modulation.setter
    def modulation(self, modulation: int) -> None:
        """Set the modulation mode"""
        self._modulation = Modulation(modulation)

    @staticmethod
    def validate_baud_rate(baud_rate: float) -> None:
        """Validate a baud rate

        Table 3 of the datasheet specifieds minimum of 0.5 kBaud, maximum of 500 kBaud
        """
        if baud_rate < 0.6 or baud_rate > 500:
            raise ValueError("baud rate must be between 0.6 and 500 kBaud")

    @staticmethod
    def baud_rate_to_config(baud_rate: float) -> Tuple[int, int]:
        """Convert a baud rate in kBaud to a configuration value

        Uses the formula from section 12 of the datasheet
        """
        CommonConfig.validate_baud_rate(baud_rate)

        xtal_freq = XTAL_FREQ * 1000000

        r_data = baud_rate * 1000

        exponent = math.floor(math.log((r_data * 2 ** 20) / xtal_freq, 2))

        mantissa = int(
            round(
                ((r_data * 2 ** 28) / (xtal_freq * 2 ** exponent)) - 256,
                0,
            )
        )

        return mantissa, exponent

    @staticmethod
    def config_to_baud_rate(mantissa: int, exponent: int) -> float:
        """Convert a baud rate configuration value to kBaud"""
        xtal_freq = XTAL_FREQ * 1000000

        r_data = (((256 + mantissa) * 2 ** exponent) / 2 ** 28) * xtal_freq

        baud_rate = float(round(r_data / 1000, 5))

        return baud_rate

    @property
    def baud_rate(self) -> float:
        """Get the configured baud rate"""
        return self._baud_rate

    @baud_rate.setter
    def baud_rate(self, baud_rate: float) -> None:
        """Set the baud rate"""
        self.validate_baud_rate(baud_rate)

        if self.modulation == Modulation.GFSK or self.modulation == Modulation.OOK:
            if baud_rate < 0.6 or baud_rate > 250:
                raise ValueError(f"Invalid baud rate for {self.modulation.name} modulation")
        elif self.modulation == Modulation.FSK_2:
            if baud_rate < 0.6 or baud_rate > 500:
                raise ValueError(f"Invalid baud rate for {self.modulation.name} modulation")
        elif self.modulation == Modulation.FSK_4:
            if baud_rate < 0.6 or baud_rate > 300:
                raise ValueError(f"Invalid baud rate for {self.modulation.name} modulation")
        elif self.modulation == Modulation.MSK:
            if baud_rate < 26 or baud_rate > 500:
                raise ValueError(f"Invalid baud rate for {self.modulation.name} modulation")

        self._baud_rate = baud_rate

    @staticmethod
    def validate_deviation(deviation: float) -> None:
        """Validate a deviation frequency

        Min/Max values allowed by 3-bit mantissa and exponent
        """
        RXConfig.deviation_to_config(deviation)

    @staticmethod
    def deviation_to_config(deviation: float) -> Tuple[int, int]:
        """Convert a deviation in kHz to a configuration value"""
        for exponent in range(0, 8):
            for mantissa in range(0, 8):
                if RXConfig.config_to_deviation(mantissa, exponent) == deviation:
                    return mantissa, exponent

        raise ValueError("invalid deviation")

    @staticmethod
    def config_to_deviation(mantissa: int, exponent: int) -> float:
        """Convert a deviation configuration value to kHz

        Uses the formula from section 16.1 of the datasheet
        """
        xtal_freq = XTAL_FREQ * 1000000

        f_dev = float((xtal_freq / 2 ** 17) * (8 + mantissa) * (2 ** exponent))

        return round(f_dev / 1000, 6)

    @property
    def deviation(self) -> float:
        """Get the configured deviation"""
        return self._deviation

    @deviation.setter
    def deviation(self, deviation: float) -> None:
        """Set deviation"""
        self.validate_deviation(deviation)
        self._deviation = deviation

    @staticmethod
    def validate_sync_word(sync_word: int) -> None:
        """Validate a sync word

        Any 16-bit sync word between 0x0000 and 0xFFFF is allowed
        For a 32-bit sync word, the high and low 16-bits must be the same
        """
        if sync_word < 0 or sync_word > 0xFFFFFFFF:
            raise ValueError("sync word must be between 0x00000000 and 0xFFFFFFFF")

        if sync_word > 0xFFFF:
            if sync_word & 0x0000FFFF != sync_word >> 16:
                raise ValueError("sync word 16 msb must match 16 lsb")

    @property
    def sync_word(self) -> int:
        """Get the configured sync word"""
        return self._sync_word

    @sync_word.setter
    def sync_word(self, sync_word: int) -> None:
        """Set the sync word"""
        self.validate_sync_word(sync_word)
        self._sync_word = sync_word

    @classmethod
    def size(cls: Type[T]) -> int:
        """Get the size in bytes of the configuration struct"""
        return struct.calcsize(cls.COMMON_STRUCT_FORMAT + cls.STRUCT_FORMAT)

    def get_unique(self) -> Tuple:
        """Serialise the unique elements of a configuration

        Child classes override this to return their unique configuration values
        """
        return ()

    @classmethod
    def set_unique(cls, config_bytes: bytes) -> Dict[str, Any]:
        """Deserialise the unqiue elements of a configuration

        Child classes override this to unpack their unique configuration values
        """
        return {}

    @classmethod
    def from_bytes(cls: Type[T], config_bytes: bytes) -> Optional[T]:
        """Convert a struct from the CC1101 driver to a configuration"""

        # Check for all zeroes in the config (not configured)
        if sum(config_bytes) == 0:
            return None

        # Unpack the common elements of the config
        (
            frequency,
            modulation,
            baud_rate_mantissa,
            baud_rate_exponent,
            deviation_mantissa,
            deviation_exponent,
            sync_word,
        ) = struct.unpack(cls.COMMON_STRUCT_FORMAT, config_bytes[: CommonConfig.size()])

        # Build common constructor arguments
        args = {
            "frequency": cls.config_to_frequency(frequency),
            "modulation": modulation,
            "baud_rate": cls.config_to_baud_rate(
                baud_rate_mantissa, baud_rate_exponent
            ),
            "deviation": cls.config_to_deviation(
                deviation_mantissa, deviation_exponent
            ),
            "sync_word": sync_word,
        }

        # Add the unique constructor arguments
        args.update(cls.set_unique(config_bytes[CommonConfig.size() :]))

        # Call the constructor
        return cls(**args)

    def to_bytes(self) -> bytes:
        """Convert the configuration to a struct that can be sent to the CC1101 driver"""

        # Get common items that convert to multiple values
        baud_rate_mantissa, baud_rate_exponent = self.baud_rate_to_config(
            self._baud_rate
        )

        deviation_mantissa, deviation_exponent = self.deviation_to_config(
            self._deviation
        )

        # Build an array of common values to pack
        args = [
            self.frequency_to_config(self._frequency),
            self._modulation,
            baud_rate_mantissa,
            baud_rate_exponent,
            deviation_mantissa,
            deviation_exponent,
            self._sync_word,
        ]

        # Get the unique values to pack
        args += self.get_unique()

        return struct.pack(self.COMMON_STRUCT_FORMAT + self.STRUCT_FORMAT, *args)

    def __repr__(self) -> str:
        ret = f"Frequency: {self._frequency} MHz\n"
        ret += f"Modulation: {self._modulation.name}\n"
        ret += f"Baud Rate: {self.baud_rate} kBaud\n"
        ret += f"Deviation: {self.deviation} kHz\n"
        ret += f"Sync Word: 0x{self.sync_word:08X}\n"
        return ret


class RXConfig(CommonConfig):
    """Class for configuration properties required for RX

    typedef struct {
        cc1101_common_config_t common;
        unsigned char bandwidth_mantissa;
        unsigned char bandwidth_exponent;
        unsigned char max_lna_gain;
        unsigned char max_dvga_gain;
        unsigned char magn_target;
        unsigned char absolute_carrier_sense;
        signed char carrier_sense;
        unsigned packet_length;
    } cc1101_rx_config_t;
    """

    STRUCT_FORMAT = "BBBBBBbI"

    packet_length: int

    def __init__(
        self,
        frequency: float,
        modulation: int,
        baud_rate: float,
        sync_word: int,
        packet_length: int,
        bandwidth: int = DEFAULT_BANDWIDTH,
        max_lna_gain: int = DEFAULT_MAX_LNA_GAIN,
        max_dvga_gain: int = DEFAULT_MAX_DVGA_GAIN,
        magn_target: int = DEFAULT_MAGN_TARGET,
        carrier_sense_mode: CarrierSenseMode = CarrierSenseMode.RELATIVE,
        carrier_sense: int = DEFAULT_CARRIER_SENSE,
        deviation: float = DEFAULT_DEVIATION,
    ):
        super().__init__(frequency, modulation, baud_rate, deviation, sync_word)
        self.bandwidth = bandwidth
        self.max_lna_gain = max_lna_gain
        self.max_dvga_gain = max_dvga_gain
        self.magn_target = magn_target
        self.carrier_sense_mode = carrier_sense_mode
        self.carrier_sense = carrier_sense
        self.packet_length = packet_length

    @staticmethod
    def supported_bandwidths() -> List[int]:
        """Get a list of bandwidth values supported by the device"""
        return [
            int(RXConfig.config_to_bandwidth(m, e))
            for m in reversed(range(0, 4))
            for e in reversed(range(0, 4))
        ]

    @staticmethod
    def validate_bandwidth(bandwidth: int) -> None:
        """Validate a bandwidth

        Min/Max values allowed by 2-bit exponent and mantissa
        """
        RXConfig.bandwidth_to_config(bandwidth)

    @staticmethod
    def bandwidth_to_config(bandwidth: int) -> Tuple[int, int]:
        """Convert a bandwidth in kHz to a configuration value"""
        for mantissa in range(0, 4):
            for exponent in range(0, 4):
                if bandwidth == RXConfig.config_to_bandwidth(mantissa, exponent):
                    return mantissa, exponent

        raise ValueError("invalid bandwidth")

    @staticmethod
    def config_to_bandwidth(mantissa: int, exponent: int) -> int:
        """Convert a bandwidth configuration value to kHz

        Uses the formula from section 13 of the datasheet
        """
        xtal_freq = XTAL_FREQ * 1000000

        bw_channel = xtal_freq / (8 * (4 + mantissa) * 2 ** exponent)

        return int(bw_channel / 1000)

    @property
    def bandwidth(self) -> int:
        """Get the configured bandwidth"""
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, bandwidth: int) -> None:
        """Set bandwidth"""
        self.validate_bandwidth(bandwidth)
        self._bandwidth = bandwidth

    def get_unique(self) -> Tuple[int, int, int, int, int, CarrierSenseMode, int, int]:
        bandwidth_mantissa, bandwidth_exponent = self.bandwidth_to_config(
            self.bandwidth
        )
        return (
            bandwidth_mantissa,
            bandwidth_exponent,
            self.max_lna_gain,
            self.max_dvga_gain,
            self.magn_target,
            self.carrier_sense_mode,
            self.carrier_sense,
            self.packet_length,
        )

    @classmethod
    def set_unique(cls, config_bytes: bytes) -> Dict[str, Any]:
        (
            bandwidth_mantissa,
            bandwidth_exponent,
            max_lna_gain,
            max_dvga_gain,
            magn_target,
            carrier_sense_mode,
            carrier_sense,
            packet_length,
        ) = struct.unpack(cls.STRUCT_FORMAT, config_bytes)

        bandwidth = cls.config_to_bandwidth(bandwidth_mantissa, bandwidth_exponent)

        return {
            "bandwidth": bandwidth,
            "max_lna_gain": max_lna_gain,
            "max_dvga_gain": max_dvga_gain,
            "magn_target": magn_target,
            "carrier_sense_mode": carrier_sense_mode,
            "carrier_sense": carrier_sense,
            "packet_length": packet_length,
        }

    def __repr__(self) -> str:
        ret = super().__repr__()
        ret += f"Bandwidth: {self.bandwidth} kHz\n"
        ret += f"Packet Length: {self.packet_length}\n"
        ret += f"Max LNA Gain: -{self.max_lna_gain} dB\n"
        ret += f"Max DVGA Gain: -{self.max_dvga_gain} dB\n"
        ret += f"Target Channel Filter Amplitude: {self.magn_target} dB\n"

        if self.carrier_sense_mode == CarrierSenseMode.ABSOLUTE:
            ret += f"Carrier Sense: {self.carrier_sense} dB\n"
        elif self.carrier_sense_mode == CarrierSenseMode.RELATIVE:
            ret += f"Carrier Sense: +{self.carrier_sense} dB\n"
        else:
            ret += "Carrier Sense: Disabled"

        return ret

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RXConfig):
            return self.to_bytes() == other.to_bytes()
        
        return False

class TXConfig(CommonConfig):
    """Class for configuration properties required for TX

    typedef struct {
        cc1101_common_config_t common;
        unsigned char tx_power;
    } cc1101_tx_config_t;
    """

    STRUCT_FORMAT = "Bxxx"

    _tx_power: int
    power_table = None

    def __init__(
        self,
        frequency: float,
        modulation: int,
        baud_rate: float,
        tx_power: int,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ):
        super().__init__(frequency, modulation, baud_rate, deviation, sync_word)
        self.tx_power = tx_power

    @classmethod
    def from_ism(
        cls: Type["TXConfig"],
        frequency: float,
        modulation: int,
        baud_rate: float,
        tx_power: float,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ) -> "TXConfig":
        """Construct a TXConfig from a frequency within the ISM bands (315/433/868/915 MHz) and a power output in dBm"""

        if cls.frequency_near(frequency, 315):
            power_table = TX_POWERS_315
        elif cls.frequency_near(frequency, 433):
            power_table = TX_POWERS_433
        elif cls.frequency_near(frequency, 868):
            power_table = TX_POWERS_868
        elif cls.frequency_near(frequency, 915):
            power_table = TX_POWERS_915
        else:
            raise ValueError("Invalid ISM frequency")

        try:
            hex_tx_power = {v: k for k, v in power_table.items()}[tx_power]
        except:
            raise ValueError("Invalid TX power")

        conf = cls(frequency, modulation, baud_rate, hex_tx_power, deviation, sync_word)
        conf.power_table = power_table
        return conf

    @staticmethod
    def frequency_near(frequency: float, target_frequency: int) -> bool:
        """Determine if a frequency is near to another frequency +/- 1MHz"""
        return frequency >= target_frequency - 1 and frequency <= target_frequency + 1

    @property
    def tx_power(self) -> int:
        """Get the TX power"""
        return self._tx_power

    @tx_power.setter
    def tx_power(self, tx_power: int) -> None:
        """Set the TX power"""
        if tx_power < 0x00 or tx_power > 0xFF:
            raise ValueError("invalid TX power")
        self._tx_power = tx_power

    def get_unique(self) -> Tuple[int]:
        return (self.tx_power,)

    @classmethod
    def set_unique(cls, config_bytes: bytes) -> Dict[str, Any]:
        (tx_power,) = struct.unpack(cls.STRUCT_FORMAT, config_bytes)

        return {"tx_power": tx_power}

    def __repr__(self) -> str:
        ret = super().__repr__()

        if self.power_table is not None:
            ret += f"TX Power: {self.power_table[self.tx_power]} dBm\n"
        else:
            ret += f"TX Power: 0x{self.tx_power:02X}\n"
        return ret


def print_raw_config(config_bytes: bytes) -> None:
    """Print an array of CC1101 config bytes as register key/values"""
    config = {}

    for r in Registers:
        config[r.name] = config_bytes[r.value]

    for k in config.keys():
        print(f"{k}: {config[k]:02x}")
