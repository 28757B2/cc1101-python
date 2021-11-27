"""
Copyright (c) 2021
"""

import os
import struct

from typing import List, Optional, Type
from types import TracebackType
from cc1101.config import RXConfig, TXConfig, CONFIG_SIZE
from cc1101 import ioctl

# CC1101 datasheet Table 31
RSSI_OFFSET = 74

class CC1101Handle:
    """Class to hold a file handle to a CC1101 device"""

    fh: int
    blocking: bool

    def __init__(self, fh: int, blocking: bool = False):
        self.fh = fh
        self.blocking = blocking

    def __enter__(self) -> int:
        return self.fh

    def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException], traceback: Optional[TracebackType]) -> bool:
        if not self.blocking:
            self.close()

        return True

    def close(self) -> None:
        os.close(self.fh)

class CC1101:
    """Class to control a CC1101 radio using the Linux driver"""

    VERSION = 3

    dev: str
    rx_config: Optional[RXConfig] = None
    handle: Optional[CC1101Handle] = None

    def __init__(self, dev: str, rx_config: Optional[RXConfig] = None, blocking: bool = False):
        self.dev = dev

        if blocking:
            self.handle = CC1101Handle(self._open(), True)

        if rx_config is not None:
            self.set_rx_config(rx_config)

    def __del__(self) -> None:
        if self.handle is not None:
            self.handle.close()

    def _open(self) -> int:
        if not os.path.exists(self.dev):
            raise OSError(f"{self.dev} does not exist")

        fh = os.open(self.dev, os.O_RDWR)

        version = bytearray(4)
        ioctl.read(fh, ioctl.IOCTL.GET_VERSION, version)
        (version,) = struct.unpack("I", version)

        if version != self.VERSION:
            raise OSError(f"Version mismatch - got {version}, expected {self.VERSION}")

        return fh

    def _get_handle(self) -> CC1101Handle:

        if self.handle is None:
            return CC1101Handle(self._open(), False)
        else:
            return self.handle

    def reset(self) -> None:
        """Reset the CC1101 device"""
        with self._get_handle() as fh:
            ioctl.call(fh, ioctl.IOCTL.RESET)

    def set_tx_config(self, tx_config: TXConfig) -> None:
        """Set the device transmit configuration"""
        with self._get_handle() as fh:
            ioctl.write(fh, ioctl.IOCTL.SET_TX_CONF, tx_config.to_bytes())

    def set_rx_config(self, rx_config: RXConfig) -> None:
        """Set the device receive configuration"""

        # If the new config is the same as the old config
        if rx_config == self.rx_config:

            # If not blocking mode
            if self.handle is None:
                # Get the config from the device
                device_config = self.get_rx_config_bytes()

                # If the config on the device differs (i.e it has been reconfigured from under us)
                if rx_config.to_bytes() != device_config:
                    # Reconfigure the device
                    with self._get_handle() as fh:
                        ioctl.write(fh, ioctl.IOCTL.SET_RX_CONF, self.rx_config.to_bytes())

        # Otherwise, update the stored config and reconfigure the device
        else:
            self.rx_config = rx_config
            with self._get_handle() as fh:
                ioctl.write(fh, ioctl.IOCTL.SET_RX_CONF, self.rx_config.to_bytes())
        
    def transmit(self, tx_config: TXConfig, packet: bytes) -> None:
        """Transmit a sequence of bytes using a TX configuration"""
        with self._get_handle() as fh:
            ioctl.write(fh, ioctl.IOCTL.SET_TX_CONF, tx_config.to_bytes())
            os.write(fh, packet)

    def receive(self) -> List[bytes]:
        """Read a sequence of packets from the device's receive buffer"""

        if self.rx_config is not None:
            self.set_rx_config(self.rx_config)
            packets = []

            with self._get_handle() as fh:
                try:
                    while True:
                        packets.append(os.read(fh, self.rx_config.packet_length))
                except OSError:
                    return packets


        raise IOError("RX config not set")

    def get_rssi(self) -> float:
        """Read the current RSSI value from the device"""
        rssi_byte = bytearray(1)
        self._ioctl(ioctl.IOCTL.GET_RSSI, rssi_byte)
        (rssi_dec,) = struct.unpack("B", rssi_byte)

        # Formula from CC1101 datasheet section 17.3
        if rssi_dec >= 128:
            rssi_dbm = (int(rssi_dec) - 256) / 2 - RSSI_OFFSET
        else:
            rssi_dbm = int(rssi_dec) / 2 - RSSI_OFFSET

        return rssi_dbm

    def get_max_packet_size(self) -> int:
        """Read the configured maximum packet size from the driver"""
        max_packet_size = bytearray(4)
        self._ioctl(ioctl.IOCTL.GET_MAX_PACKET_SIZE, max_packet_size)
        (max_packet_size,) = struct.unpack("I", max_packet_size)

        return int(max_packet_size)

    def _ioctl(self, command: ioctl.IOCTL, out: bytes) -> None:
        """Helper to read a device config"""
        with self._get_handle() as fh:
            ioctl.read(fh, command, out)

    def get_device_config(self) -> bytes:
        """Get the current device configuration registers as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_DEV_RAW_CONF, config)
        return bytes(config)

    def get_tx_config_raw(self) -> bytes:
        """Get the current configuration registers for TX as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_TX_RAW_CONF, config)
        return bytes(config)

    def get_rx_config_raw(self) -> bytes:
        """Get the current configuration registers for RX as a sequence of bytes"""
        config = bytearray(CONFIG_SIZE)
        self._ioctl(ioctl.IOCTL.GET_RX_RAW_CONF, config)
        return bytes(config)

    def get_rx_config_bytes(self) -> bytes:
        """Get the current RX configuration as struct bytes"""
        config = bytearray(RXConfig.size())
        self._ioctl(ioctl.IOCTL.GET_RX_CONF, config)
        return bytes(config)

    def get_rx_config(self) -> Optional[RXConfig]:
        """Get the current RX configuration"""
        return RXConfig.from_bytes(self.get_rx_config_bytes())

    def get_tx_config(self) -> Optional[TXConfig]:
        """Get the current TX configuration"""
        config = bytearray(TXConfig.size())
        self._ioctl(ioctl.IOCTL.GET_TX_CONF, config)
        return TXConfig.from_bytes(config)
