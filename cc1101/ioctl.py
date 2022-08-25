"""
Copyright (c) 2021
"""

from enum import IntEnum
import fcntl

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

    ioctl = 0
    ioctl |= (ord(DEVICE_CHARACTER) << 8)
    ioctl |= cmd

    fcntl.ioctl(fh, ioctl)


def write(fh: int, cmd: IOCTL, data: bytes) -> None:
    """Helper function for IOCTLs that write data to the driver"""
    
    ioctl = 0x40000000
    ioctl |= (len(data) << 16)
    ioctl |= (ord(DEVICE_CHARACTER) << 8)
    ioctl |= cmd

    fcntl.ioctl(fh, ioctl, data)


def read(fh: int, cmd: IOCTL, data: bytes) -> None:
    """Helper function for IOCTLs that read data from the driver"""

    ioctl = 0x80000000
    ioctl |= (len(data) << 16)
    ioctl |= (ord(DEVICE_CHARACTER) << 8)
    ioctl |= cmd

    fcntl.ioctl(fh, ioctl, data)
