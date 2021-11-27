"""
Copyright (c) 2021
"""

from enum import IntEnum
import fcntl
from ioctl_opt import IOC, IOC_NONE, IOC_READ, IOC_WRITE

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


def call(fh: int, cmd: IOCTL) -> None:
    """Helper for IOCTLs that call driver functions (no arguments)"""
    fcntl.ioctl(fh, IOC(IOC_NONE, ord(DEVICE_CHARACTER), cmd, 0))


def write(fh: int, cmd: IOCTL, data: bytes) -> None:
    """Helper function for IOCTLs that write data to the driver"""
    fcntl.ioctl(fh, IOC(IOC_WRITE, ord(DEVICE_CHARACTER), cmd, len(data)), data)


def read(fh: int, cmd: IOCTL, data: bytes) -> None:
    """Helper function for IOCTLs that read data from the driver"""
    fcntl.ioctl(fh, IOC(IOC_READ, ord(DEVICE_CHARACTER), cmd, len(data)), data)
