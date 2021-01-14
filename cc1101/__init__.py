"""
Copyright (c) 2021
"""

import os
import struct

from typing import List, Optional
from cc1101.config import RXConfig, TXConfig, CONFIG_SIZE
from cc1101 import ioctl


class CC1101:
    """Class to control a CC1101 radio using the Linux driver"""

    VERSION = 1

    dev: str
    rx_config: Optional[RXConfig]

    def __init__(self, dev: str, rx_config: Optional[RXConfig] = None):
        self.dev = dev

        if not os.path.exists(dev):
            raise OSError(f"{dev} does not exist")

        version = bytearray(4)
        self._ioctl(ioctl.IOCTL.GET_VERSION, version)
        (version,) = struct.unpack("I", version)

        if version != self.VERSION:
            raise OSError(f"Version mismatch - got {version}, expected {self.VERSION}")

        self.set_rx_config(rx_config)

    def reset(self) -> None:
        """Reset the CC1101 device"""
        fh = os.open(self.dev, os.O_RDWR)
        ioctl.call(fh, ioctl.IOCTL.RESET)
        os.close(fh)

    def set_tx_config(self, tx_config: TXConfig) -> None:
        """Set the device transmit configuration"""
        fh = os.open(self.dev, os.O_RDWR)
        ioctl.write(fh, ioctl.IOCTL.SET_TX_CONF, tx_config.to_bytes())
        os.close(fh)

    def set_rx_config(self, rx_config: Optional[RXConfig]) -> None:
        """Set the device receive configuration"""
        self.rx_config = rx_config

        if self.rx_config is not None:
            fh = os.open(self.dev, os.O_RDWR)
            ioctl.write(fh, ioctl.IOCTL.SET_RX_CONF, self.rx_config.to_bytes())
            os.close(fh)

    def transmit(self, tx_config: TXConfig, packet: bytes) -> None:
        """Transmit a sequence of bytes using a TX configuration"""
        fh = os.open(self.dev, os.O_RDWR)
        ioctl.write(fh, ioctl.IOCTL.SET_TX_CONF, tx_config.to_bytes())
        os.write(fh, packet)
        os.close(fh)

    def receive(self) -> List[bytes]:
        """Read a sequence of packets from the device's receive buffer"""

        if self.rx_config is not None:
            packets = []

            fh = os.open(self.dev, os.O_RDWR)
            try:
                while True:
                    packets.append(os.read(fh, self.rx_config.packet_length))
            except OSError:
                return packets
            finally:
                os.close(fh)

        raise IOError("RX config not set")

    def _ioctl(self, command: ioctl.IOCTL, out: bytes) -> None:
        """Helper to read a device config"""
        fh = os.open(self.dev, os.O_RDWR)
        ioctl.read(fh, command, out)
        os.close(fh)

    def get_device_config(self) -> bytes:
        """Get the current device configuration registers as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_DEV_RAW_CONF, config)
        return config

    def get_tx_config_raw(self) -> bytes:
        """Get the current configuration registers for TX as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_TX_RAW_CONF, config)
        return config

    def get_rx_config_raw(self) -> bytes:
        """Get the current configuration registers for RX as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_RX_RAW_CONF, config)
        return config

    def get_rx_config(self) -> Optional[RXConfig]:
        """Get the current RX configuration"""
        config = bytearray(RXConfig.size())
        self._ioctl(ioctl.IOCTL.GET_RX_CONF, config)
        return RXConfig.from_bytes(config)

    def get_tx_config(self) -> Optional[TXConfig]:
        """Get the current TX configuration"""
        config = bytearray(TXConfig.size())
        self._ioctl(ioctl.IOCTL.GET_TX_CONF, config)
        return TXConfig.from_bytes(config)
