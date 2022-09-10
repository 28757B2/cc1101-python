"""
Copyright (c) 2022
"""

import ctypes
import math

from enum import IntEnum
from typing import Dict, Tuple, TypeVar, Type, Optional

from cc1101.errors import ConfigError, ConfigException

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

AVAILABLE_MAX_LNA_GAINS = [0, 3, 6, 7, 9, 12, 15, 17]
AVAILABLE_MAX_DVGA_GAINS = [0, 6, 12, 18]
AVAILABLE_MAGN_TARGETS = [24, 27, 30, 33, 36, 38, 40, 42]

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

class CarrierSenseMode(IntEnum):
    DISABLED = 0
    RELATIVE = 1
    ABSOLUTE = 2


class CommonConfig:
    """Class for common configuration properties shared by TX and RX"""

    _frequency: int
    _modulation: Modulation
    _baud_rate_mantissa: int
    _baud_rate_exponent: int
    _deviation_mantissa: int
    _deviation_exponent: int
    _sync_word: int

    T = TypeVar("T", bound="CommonConfig")

    def __init__(
        self,
        frequency: float,
        modulation: Modulation,
        baud_rate: float,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ):
        self.set_frequency(frequency)
        self.set_modulation_and_baud_rate(modulation, baud_rate)
        self.set_deviation(deviation)
        self.set_sync_word(sync_word)

    @staticmethod
    def frequency_to_config(frequency: float) -> int:
        """Convert a frequency in MHz to a configuration value

        Uses the formula from section 21 of the CC1101 datasheet
        """

        if not (
            (frequency >= 299.999756 and frequency <= 347.999939)
            or (frequency >= 386.999939 and frequency <= 463.999786)
            or (frequency >= 778.999878 and frequency <= 928.000000)
        ):
            raise ConfigException(ConfigError.INVALID_FREQUENCY)
        multiplier = (frequency * 2 ** 16) / XTAL_FREQ
        return int(multiplier)

    @staticmethod
    def config_to_frequency(config: int) -> float:
        """Convert a configuration value to a frequency in MHz

        Uses the formula from section 21 of the CC1101 datasheet
        """
        return round((XTAL_FREQ / 2 ** 16) * config, 6)

    def get_frequency(self) -> float:
        """Get the configured frequency"""
        return self.config_to_frequency(self._frequency)

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency"""
        self._frequency = self.frequency_to_config(frequency)

    @staticmethod
    def baud_rate_to_config(modulation: Modulation, baud_rate: float) -> Tuple[int, int]:
        """Convert a baud rate in kBaud to a configuration value

        Uses the formula from section 12 of the datasheet

        Table 3 of the datasheet specifieds minimum of 0.5 kBaud, maximum of 500 kBaud
        """

        if modulation == Modulation.GFSK or modulation == Modulation.OOK:
            if baud_rate < 0.599742 or baud_rate > 249.939:
                raise ConfigException(ConfigError.INVALID_BAUD_RATE)
        elif modulation == Modulation.FSK_2:
            if baud_rate < 0.599742 or baud_rate > 500:
                raise ConfigException(ConfigError.INVALID_BAUD_RATE)
        elif modulation == Modulation.FSK_4:
            if baud_rate < 0.599742 or baud_rate > 299.927:
                raise ConfigException(ConfigError.INVALID_BAUD_RATE)
        elif modulation == Modulation.MSK:
            if baud_rate < 25.9857 or baud_rate > 499.878:
                raise ConfigException(ConfigError.INVALID_BAUD_RATE)
        
        
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

    def get_modulation_and_baud_rate(self) -> Tuple[Modulation, float]:
        """Get the configured baud rate"""
        return self._modulation, self.config_to_baud_rate(self._baud_rate_mantissa, self._baud_rate_exponent)

    def set_modulation_and_baud_rate(self, modulation: Modulation, baud_rate: float) -> None:
        """Set the baud rate"""
        self._baud_rate_mantissa, self._baud_rate_exponent = self.baud_rate_to_config(modulation, baud_rate)
        self._modulation = modulation

    @staticmethod
    def deviation_to_config(deviation: float) -> Tuple[int, int]:
        """Convert a deviation in kHz to a configuration value"""
        for exponent in range(0, 8):
            for mantissa in range(0, 8):
                if CommonConfig.config_to_deviation(mantissa, exponent) == deviation:
                    return mantissa, exponent

        raise ConfigException(ConfigError.INVALID_DEVIATION)

    @staticmethod
    def config_to_deviation(mantissa: int, exponent: int) -> float:
        """Convert a deviation configuration value to kHz

        Uses the formula from section 16.1 of the datasheet
        """
        xtal_freq = XTAL_FREQ * 1000000

        f_dev = float((xtal_freq / 2 ** 17) * (8 + mantissa) * (2 ** exponent))

        return round(f_dev / 1000, 6)

    def get_deviation(self) -> float:
        """Get the configured deviation"""
        return self.config_to_deviation(self._deviation_mantissa, self._deviation_exponent)

    def set_deviation(self, deviation: float) -> None:
        """Set deviation"""
        self._deviation_mantissa, self._deviation_exponent = self.deviation_to_config(deviation)

    def get_sync_word(self) -> int:
        """Get the configured sync word"""
        return self._sync_word

    def set_sync_word(self, sync_word: int) -> None:
        """Set the sync word
        
        Any 16-bit sync word between 0x0000 and 0xFFFF is allowed
        For a 32-bit sync word, the high and low 16-bits must be the same
        """
        if sync_word < 0 or sync_word > 0xFFFFFFFF:
            raise ConfigException(ConfigError.INVALID_SYNC_WORD)

        if sync_word > 0xFFFF:
            if sync_word & 0x0000FFFF != sync_word >> 16:
                raise ConfigException(ConfigError.INVALID_SYNC_WORD)

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

        return cc1101_common_config(
            self.frequency_to_config(self._frequency),
            self._modulation,
            self._baud_rate_mantissa,
            self._baud_rate_exponent,
            self._deviation_mantissa,
            self._deviation_exponent,
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

        modulation, baud_rate = self.get_modulation_and_baud_rate()

        ret = f"Frequency: {self._frequency} MHz\n"
        ret += f"Modulation: {modulation.name}\n"
        ret += f"Baud Rate: {baud_rate} kBaud\n"
        ret += f"Deviation: {self.get_deviation()} kHz\n"
        ret += f"Sync Word: 0x{self.get_sync_word():08X}\n"
        return ret

class RXConfig():
    """Class for configuration properties required for RX"""

    T = TypeVar("T", bound="RXConfig")

    _common_config: CommonConfig
    _bandwidth_mantissa: int
    _bandwidth_exponent: int
    _max_lna_gain: int
    _max_dvga_gain: int
    _magn_target: int
    _carrier_sense: int
    packet_length: int

    def __init__(
        self,
        common_config: CommonConfig,
        packet_length: int,
        bandwidth: int = DEFAULT_BANDWIDTH,
        carrier_sense_mode: CarrierSenseMode = CarrierSenseMode.RELATIVE,
        carrier_sense: int = DEFAULT_CARRIER_SENSE,
        max_lna_gain: int = DEFAULT_MAX_LNA_GAIN,
        max_dvga_gain: int = DEFAULT_MAX_DVGA_GAIN,
        magn_target: int = DEFAULT_MAGN_TARGET,
    ):
        self._common_config = common_config
        self.set_bandwidth(bandwidth)
        self.set_carrier_sense(carrier_sense_mode, carrier_sense)
        self.set_max_lna_gain(max_lna_gain)
        self.set_max_dvga_gain(max_dvga_gain)
        self.set_magn_target(magn_target)
        self.packet_length = packet_length

    @classmethod
    def new(
        cls: Type["RXConfig"],
        frequency: float,
        modulation: Modulation,
        baud_rate: float,
        packet_length: int,
        bandwidth: int = DEFAULT_BANDWIDTH,
        carrier_sense_mode: CarrierSenseMode = CarrierSenseMode.RELATIVE,
        carrier_sense: int = DEFAULT_CARRIER_SENSE,
        max_lna_gain: int = DEFAULT_MAX_LNA_GAIN,
        max_dvga_gain: int = DEFAULT_MAX_DVGA_GAIN,
        magn_target: int = DEFAULT_MAGN_TARGET,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ) -> "RXConfig":
        """Construct a RXConfig from all available parameters"""
        common_config = CommonConfig(frequency, modulation, baud_rate, deviation, sync_word)
        return cls(common_config, packet_length, bandwidth, carrier_sense_mode, carrier_sense, max_lna_gain, max_dvga_gain, magn_target)

    @staticmethod
    def bandwidth_to_config(bandwidth: int) -> Tuple[int, int]:
        """Convert a bandwidth in kHz to a configuration value"""
        for mantissa in range(0, 4):
            for exponent in range(0, 4):
                if bandwidth == RXConfig.config_to_bandwidth(mantissa, exponent):
                    return mantissa, exponent

        raise ConfigException(ConfigError.INVALID_BANDWIDTH)

    @staticmethod
    def config_to_bandwidth(mantissa: int, exponent: int) -> int:
        """Convert a bandwidth configuration value to kHz

        Uses the formula from section 13 of the datasheet
        """
        xtal_freq = XTAL_FREQ * 1000000

        bw_channel = xtal_freq / (8 * (4 + mantissa) * 2 ** exponent)

        return int(bw_channel / 1000)

    def get_bandwidth(self) -> int:
        """Get the configured bandwidth"""
        return self.config_to_bandwidth(self._bandwidth_mantissa, self.bandwidth_exponent)

    def set_bandwidth(self, bandwidth: int) -> None:
        """Set bandwidth"""
        self._bandwidth_mantissa, self.bandwidth_exponent = self.bandwidth_to_config(bandwidth)

    def get_carrier_sense(self) -> Tuple[CarrierSenseMode, int]:
        """Get the configured carrier sense mode and value"""
        return self._carrier_sense_mode, self._carrier_sense

    def set_carrier_sense(self, carrier_sense_mode: CarrierSenseMode, carrier_sense: int) -> None:

        if carrier_sense_mode == CarrierSenseMode.RELATIVE:
            if carrier_sense in [6, 10, 14]:
                self._carrier_sense_mode = carrier_sense_mode
                self._carrier_sense = carrier_sense
            else:
                raise ConfigException(ConfigError.INVALID_CARRIER_SENSE)
        elif carrier_sense_mode == CarrierSenseMode.ABSOLUTE:
            if carrier_sense >= -7 and carrier_sense <= 7:
                self._carrier_sense_mode = carrier_sense_mode
                self._carrier_sense = carrier_sense
            else:
                raise ConfigException(ConfigError.INVALID_CARRIER_SENSE)
        elif carrier_sense_mode == CarrierSenseMode.DISABLED:
            self._carrier_sense_mode = carrier_sense_mode
            self._carrier_sense = 0
        else:
            raise ConfigException(ConfigError.INVALID_CARRIER_SENSE)


    def get_max_lna_gain(self) -> int:
        """Get the configured maximum LNA gain"""
        return self._max_lna_gain

    def set_max_lna_gain(self, max_lna_gain: int) -> None:
        """Set maximum LNA gain"""

        if max_lna_gain in AVAILABLE_MAX_LNA_GAINS:
            self._max_lna_gain = max_lna_gain
        else:
            raise ConfigException(ConfigError.INVALID_MAX_LNA_GAIN)

    def get_max_dvga_gain(self) -> int:
        """Get the configured maximum DVGA gain"""
        return self._max_dvga_gain

    def set_max_dvga_gain(self, max_dvga_gain: int) -> None:
        """Set maximum DVGA gain"""

        if max_dvga_gain in AVAILABLE_MAX_DVGA_GAINS:
            self._max_dvga_gain = max_dvga_gain
        else:
            raise ConfigException(ConfigError.INVALID_MAX_DVGA_GAIN)

    def get_magn_target(self) -> int:
        """Get the configured maximum DVGA gain"""
        return self._magn_target

    def set_magn_target(self, magn_target: int) -> None:
        """Set maximum DVGA gain"""

        if magn_target in AVAILABLE_MAGN_TARGETS:
            self._magn_target = magn_target
        else:
            raise ConfigException(ConfigError.INVALID_MAGN_TARGET)

    @classmethod
    def size(cls) -> int:
        return ctypes.sizeof(cc1101_rx_config)

    @classmethod
    def from_struct(cls: Type[T], config: cc1101_rx_config) -> T: # type: ignore[override]
        """Construct a RXConfig from a cc1101_rx_config struct"""

        bandwidth = cls.config_to_bandwidth(config.bandwidth_mantissa, config.bandwidth_exponent)

        return cls(
            CommonConfig.from_struct(config.common),
            config.packet_length,
            bandwidth,
            config.max_lna_gain,
            config.max_dvga_gain,
            config.magn_target,
            config.carrier_sense_mode,
            config.carrier_sense,
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

        return cc1101_rx_config(
            self._common_config.to_struct(),
            self._bandwidth_mantissa,
            self._bandwidth_exponent,
            self._max_lna_gain,
            self._max_dvga_gain,
            self._magn_target,
            self._carrier_sense_mode,
            self._carrier_sense,
            self.packet_length,
        )

    def to_bytes(self) -> bytes:
        """Serialize a RXConfig to a cc1101_rx_config struct bytes"""
        return bytes(self.to_struct())

    def __repr__(self) -> str:
        ret = self._common_config.__repr__()
        ret += f"Bandwidth: {self.get_bandwidth()} kHz\n"
        ret += f"Packet Length: {self.packet_length}\n"
        ret += f"Max LNA Gain: -{self.get_max_lna_gain()} dB\n"
        ret += f"Max DVGA Gain: -{self.get_max_dvga_gain()} dB\n"
        ret += f"Target Channel Filter Amplitude: {self.get_magn_target()} dB\n"

        carrier_sense_mode, carrier_sense = self.get_carrier_sense()

        if carrier_sense_mode == CarrierSenseMode.ABSOLUTE:
            ret += f"Carrier Sense: {carrier_sense} dB\n"
        elif carrier_sense_mode == CarrierSenseMode.RELATIVE:
            ret += f"Carrier Sense: +{carrier_sense} dB\n"
        else:
            ret += "Carrier Sense: Disabled"

        return ret

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RXConfig):
            return self.to_bytes() == other.to_bytes()
        
        return False

class TXConfig():
    """Class for configuration properties required for TX"""

    T = TypeVar("T", bound="TXConfig")

    _common_config: CommonConfig
    _tx_power: int

    def __init__(
        self,
        common_config: CommonConfig,
        tx_power: int,
    ):
        self._common_config = common_config
        self.set_tx_power_raw(tx_power)

    @classmethod
    def new(
        cls: Type["TXConfig"],
        frequency: float,
        modulation: Modulation,
        baud_rate: float,
        tx_power: float,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ) -> "TXConfig":
        """Construct a TXConfig from a frequency within the ISM bands (315/433/868/915 MHz) and a power output in dBm"""
        common_config = CommonConfig(frequency, modulation, baud_rate, deviation, sync_word)
        tx_power = TXConfig.tx_power_to_config(frequency, tx_power)
        return cls(common_config, tx_power)

    @classmethod
    def new_raw(
        cls: Type["TXConfig"],
        frequency: float,
        modulation: Modulation,
        baud_rate: float,
        tx_power: int,
        deviation: float = DEFAULT_DEVIATION,
        sync_word: int = DEFAULT_SYNC_WORD,
    ) -> "TXConfig":
        """Construct a TXConfig with a raw PATABLE TX power value"""
        common_config = CommonConfig(frequency, modulation, baud_rate, deviation, sync_word)
        return cls(common_config, tx_power)

    @staticmethod
    def frequency_near(frequency: float, target_frequency: int) -> bool:
        """Determine if a frequency is near to another frequency +/- 1MHz"""
        return frequency >= target_frequency - 1 and frequency <= target_frequency + 1

    @staticmethod
    def get_power_table(frequency: float) -> Dict[int, float]:
        if TXConfig.frequency_near(frequency, 315):
            return TX_POWERS_315
        elif TXConfig.frequency_near(frequency, 433):
            return TX_POWERS_433
        elif TXConfig.frequency_near(frequency, 868):
            return TX_POWERS_868
        elif TXConfig.frequency_near(frequency, 915):
            return TX_POWERS_915
        else:
            raise ConfigException(ConfigError.INVALID_FREQUENCY)

    @staticmethod
    def config_to_tx_power(frequency: float, tx_power: int) -> float:

        power_table = TXConfig.get_power_table(frequency)

        if tx_power in power_table:
            return power_table[tx_power]
        else:
            raise ConfigException(ConfigError.INVALID_TX_POWER)

    @staticmethod
    def tx_power_to_config(frequency: float, tx_power: float) -> int:

        reversed_power_table = {v:k for k,v in TXConfig.get_power_table(frequency).items()}

        if tx_power in reversed_power_table:
            return reversed_power_table[tx_power]
        else:
            raise ConfigException(ConfigError.INVALID_TX_POWER)

    def get_tx_power_raw(self) -> int:
        """Get the TX power as a raw PATABLE value"""
        return self._tx_power

    def set_tx_power_raw(self, tx_power: int) -> None:
        """Set the TX power as a raw PATABLE value"""
        if tx_power < 0x00 or tx_power > 0xFF:
            raise ConfigException(ConfigError.INVALID_TX_POWER)
        self._tx_power = tx_power

    def get_tx_power(self) -> float:
        """Get the TX power in dBm
        
        Configured frequency must be within 1MHz of 315/433/868/915Mhz
        """
        return self.config_to_tx_power(self._common_config.get_frequency(), self._tx_power)

    def set_tx_power(self, tx_power: float) -> None:
        """Set the TX power in dBm
        
        Configured frequency must be within 1MHz of 315/433/868/915Mhz
        """
        self._tx_power = self.tx_power_to_config(self._common_config.get_frequency(), tx_power)

    @classmethod
    def size(cls: Type[T]) -> int:
        """Get the size in bytes of the configuration struct"""
        return ctypes.sizeof(cc1101_tx_config)

    @classmethod
    def from_struct(cls: Type[T], config: cc1101_tx_config) -> T: # type: ignore[override]
        """Convert a cc1101_tx_config struct to a TXConfig"""

        return cls(
            CommonConfig.from_struct(config.common),
            config.tx_power
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

        return cc1101_tx_config(
            self._common_config.to_struct(),
            self._tx_power
        )

    def to_bytes(self) -> bytes:
        """Serialize a TXConfig to cc1101_tx_config struct bytes"""
        return bytes(self.to_struct())
        
    def __repr__(self) -> str:
        ret = self._common_config.__repr__()

        try:
            ret += f"TX Power: {self.get_tx_power()} dBm\n"
        except ConfigException:
            ret += f"TX Power: 0x{self._tx_power:02X}\n"

        return ret

def print_raw_config(config_bytes: bytes) -> None:
    """Print an array of CC1101 config bytes as register key/values"""
    config = {}

    for r in Registers:
        config[r.name] = config_bytes[r.value]

    for k in config.keys():
        print(f"{k}: {config[k]:02x}")
