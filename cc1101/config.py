"""
Copyright (c) 2021
"""

import ctypes
import math

from enum import IntEnum
from typing import Dict, List, Tuple, TypeVar, Type, Optional, Any

from .patable import TX_POWERS_315, TX_POWERS_433, TX_POWERS_868, TX_POWERS_915

# Crystal frequency of 26 Mhz
XTAL_FREQ = 26
DEFAULT_DEVIATION = 47.607422
DEFAULT_BANDWIDTH = 203
DEFAULT_SYNC_WORD = 0x0000
DEFAULT_MAX_LNA_GAIN = 0
DEFAULT_MAX_DVGA_GAIN = 0
DEFAULT_MAGN_TARGET = 33
DEFAULT_CARRIER_SENSE = 10

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

class cc1101_common_config(ctypes.Structure):
    """C struct definition for cc1101_common_config from cc1101.h"""

    _fields_ = [
        ("frequency", ctypes.c_uint),
        ("modulation", ctypes.c_ubyte),
        ("baud_rate_mantissa", ctypes.c_ubyte),
        ("baud_rate_exponent", ctypes.c_ubyte),
        ("deviation_mantissa", ctypes.c_ubyte), 
        ("deviation_exponent", ctypes.c_ubyte), 
        ("sync_word", ctypes.c_ulong),               
    ]

class cc1101_rx_config(ctypes.Structure):
    """C struct definition for cc1101_rx_config from cc1101.h"""

    _fields_ = [
        ("common", cc1101_common_config),
        ("bandwidth_mantissa", ctypes.c_ubyte),
        ("bandwidth_exponent", ctypes.c_ubyte),
        ("max_lna_gain", ctypes.c_ubyte),
        ("max_dvga_gain", ctypes.c_ubyte), 
        ("magn_target", ctypes.c_ubyte), 
        ("carrier_sense_mode", ctypes.c_ubyte), 
        ("carrier_sense", ctypes.c_byte), 
        ("packet_length", ctypes.c_uint), 
    ]

class cc1101_tx_config(ctypes.Structure):
    """C struct definition for cc1101_tx_config from cc1101.h"""

    _fields_ = [
        ("common", cc1101_common_config),
        ("tx_power", ctypes.c_ubyte), 
    ]

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
        return ctypes.sizeof(cc1101_common_config)

    @classmethod
    def from_struct(cls: Type[T], config: cc1101_common_config) -> T:
        """Construct a CommonConfig from a cc1101_common_config struct"""

        frequency = cls.config_to_frequency(config.frequency)

        baud_rate = cls.config_to_baud_rate(
            config.baud_rate_mantissa, config.baud_rate_exponent
        )

        deviation = cls.config_to_deviation(
            config.deviation_mantissa, config.deviation_exponent
        )

        return cls(
            frequency,
            config.modulation,
            baud_rate,
            deviation,
            config.sync_word
        )

    def to_struct(self) -> cc1101_common_config:
        """Serialize a CommonConfig to a cc1101_common_config struct"""

        baud_rate_mantissa, baud_rate_exponent = self.baud_rate_to_config(
            self._baud_rate
        )

        deviation_mantissa, deviation_exponent = self.deviation_to_config(
            self._deviation
        )

        return cc1101_common_config(
            self.frequency_to_config(self._frequency),
            self._modulation,
            baud_rate_mantissa,
            baud_rate_exponent,
            deviation_mantissa,
            deviation_exponent,
            self._sync_word,
        )

    @classmethod
    def from_bytes(cls: Type[T], config_bytes: bytes) -> Optional[T]:
        """Convert struct bytes from the CC1101 driver to a CommonConfig"""

        print(config_bytes)

        # Check for all zeroes in the config (not configured)
        if sum(config_bytes) == 0:
            return None

        config = cc1101_common_config.from_buffer_copy(config_bytes)
        return cls.from_struct(config)

    def to_bytes(self) -> bytes:
        """Convert configuration to struct bytes to send to the CC1101 driver"""
        return bytes(self.to_struct())

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

    T = TypeVar("T", bound="RXConfig")

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

    @classmethod
    def size(cls) -> int:
        return ctypes.sizeof(cc1101_rx_config)

    @classmethod
    def from_struct(cls: Type[T], config: cc1101_rx_config) -> T: # type: ignore[override]
        """Construct a RXConfig from a cc1101_rx_config struct"""

        common_config = CommonConfig.from_struct(config.common)

        bandwidth = cls.config_to_bandwidth(config.bandwidth_mantissa, config.bandwidth_exponent)

        return cls(
            common_config.frequency,
            common_config.modulation,
            common_config.baud_rate,
            common_config.sync_word,
            config.packet_length,
            bandwidth,
            config.max_lna_gain,
            config.max_dvga_gain,
            config.magn_target,
            config.carrier_sense_mode,
            config.carrier_sense,
            common_config.deviation
        )

    @classmethod
    def from_bytes(cls: Type[T], config_bytes: bytes) -> Optional[T]:
        """Convert struct bytes from the CC1101 driver to a RXConfig"""

        # Check for all zeroes in the config (not configured)
        if sum(config_bytes) == 0:
            return None

        config = cc1101_rx_config.from_buffer_copy(config_bytes)

        return cls.from_struct(config)

    def to_struct(self) -> cc1101_rx_config: # type: ignore[override]
        """Serialize a RXConfig to a cc1101_rx_config struct"""

        common_config = super().to_struct()

        bandwidth_mantissa, bandwidth_exponent = self.bandwidth_to_config(
            self.bandwidth
        )

        return cc1101_rx_config(
            common_config,
            bandwidth_mantissa,
            bandwidth_exponent,
            self.max_lna_gain,
            self.max_dvga_gain,
            self.magn_target,
            self.carrier_sense_mode,
            self.carrier_sense,
            self.packet_length,
        )

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

    T = TypeVar("T", bound="TXConfig")

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

    @classmethod
    def size(cls: Type[T]) -> int:
        """Get the size in bytes of the configuration struct"""
        return ctypes.sizeof(cc1101_tx_config)

    @classmethod
    def from_struct(cls: Type[T], config: cc1101_tx_config) -> T: # type: ignore[override]
        """Convert a cc1101_tx_config struct to a TXConfig"""

        common_config = CommonConfig.from_struct(config.common)

        return cls(
            common_config.frequency,
            common_config.modulation,
            common_config.baud_rate,
            config.tx_power,
            common_config.deviation,
            common_config.sync_word
        )

    @classmethod
    def from_bytes(cls: Type[T], config_bytes: bytes) -> Optional[T]:
        """Convert struct bytes from the CC1101 driver to a TXConfig"""

        # Check for all zeroes in the config (not configured)
        if sum(config_bytes) == 0:
            return None

        config = cc1101_tx_config.from_buffer_copy(config_bytes)
        return cls.from_struct(config)

    def to_struct(self) -> cc1101_tx_config: # type: ignore[override]
        """Serialize a TXConfig to a cc1101_tx_config struct"""

        common_config = super().to_struct()

        return cc1101_tx_config(
            common_config,
            self._tx_power
        )
        
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
