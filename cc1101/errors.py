from enum import Enum, auto


class DeviceError(Enum):
    NO_DEVICE = auto()
    FILE_HANDLE_CLONE = auto()
    INVALID_IOCTL = auto()
    VERSION_MISMATCH = auto()
    NO_RX_CONFIG = auto()
    BUSY = auto()
    COPY = auto()
    INVALID_CONFIG = auto()
    OUT_OF_MEMORY = auto()
    BUFFER_EMPTY = auto()
    PACKET_SIZE = auto()
    UNKNOWN = auto()


class ConfigError(Enum):
    INVALID_FREQUENCY = auto()
    INVALID_BANDWIDTH = auto()
    INVALID_CARRIER_SENSE = auto()
    INVALID_TX_POWER = auto()
    INVALID_BAUD_RATE = auto()
    INVALID_DEVIATION = auto()
    INVALID_SYNC_WORD = auto()
    INVALID_MAX_LNA_GAIN = auto()
    INVALID_MAX_DVGA_GAIN = auto()
    INVALID_MAGN_TARGET = auto()


class CC1101Exception(Exception):
    pass


class DeviceException(CC1101Exception):
    def __init__(self, error: DeviceError):
        self.error = error


class ConfigException(CC1101Exception):
    def __init__(self, error: ConfigError):
        self.error = error
