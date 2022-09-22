"""
Copyright (c) 2022
"""
import errno
import fcntl

from enum import IntEnum

from cc1101.errors import DeviceError, DeviceException

DEVICE_CHARACTER = "c"


class IOCTL(IntEnum):
    """IOCTL values corresponding with those defined in cc1101_chrdev.c in the driver"""

    GET_VERSION = 0
    RESET = 1
    SET_TX_CONF = 2
    SET_RX_CONF = 3
    GET_TX_CONF = 4
    GET_TX_RAW_CONF = 5
    GET_RX_CONF = 6
    GET_RX_RAW_CONF = 7
    GET_DEV_RAW_CONF = 8
    GET_RSSI = 9
    GET_MAX_PACKET_SIZE = 10


def handle_status(status: int) -> None:
    """Convert IOCTL errno to an exception if required"""

    if status == 0:
        return
    elif status == errno.EIO:
        raise DeviceException(DeviceError.INVALID_IOCTL)
    elif status == errno.EFAULT:
        raise DeviceException(DeviceError.COPY)
    elif status == errno.EINVAL:
        raise DeviceException(DeviceError.INVALID_CONFIG)
    elif status == errno.ENOMEM:
        raise DeviceException(DeviceError.OUT_OF_MEMORY)
    else:
        raise DeviceException(DeviceError.UNKNOWN)


def call(fh: int, cmd: IOCTL) -> None:
    """Helper for IOCTLs that call driver functions (no arguments)"""

    ioctl = 0
    ioctl |= ord(DEVICE_CHARACTER) << 8
    ioctl |= cmd

    try:
        status = fcntl.ioctl(fh, ioctl)
    except OSError as e:
        status = e.errno

    handle_status(status)


def write(fh: int, cmd: IOCTL, data: bytearray) -> None:
    """Helper function for IOCTLs that write data to the driver"""

    ioctl = 0x40000000
    ioctl |= len(data) << 16
    ioctl |= ord(DEVICE_CHARACTER) << 8
    ioctl |= cmd

    try:
        status = fcntl.ioctl(fh, ioctl, data, True)
    except OSError as e:
        status = e.errno

    handle_status(status)


def read(fh: int, cmd: IOCTL, data: bytearray) -> None:
    """Helper function for IOCTLs that read data from the driver"""

    ioctl = 0x80000000
    ioctl |= len(data) << 16
    ioctl |= ord(DEVICE_CHARACTER) << 8
    ioctl |= cmd

    try:
        status = fcntl.ioctl(fh, ioctl, data, True)
    except OSError as e:
        status = e.errno

    handle_status(status)
