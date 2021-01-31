"""
Copyright (c) 2021
"""

import argparse
from binascii import hexlify, unhexlify
import time

from . import config, CC1101


def tx(args: argparse.Namespace) -> None:
    """Handle the tx subcommand"""

    modulation = int(args.modulation)
    frequency = float(args.frequency)
    baud_rate = float(args.baud_rate)
    sync_word = int(args.sync_word, 16)

    try:
        if args.raw:
            tx_config = config.TXConfig(
                frequency,
                modulation,
                baud_rate,
                int(args.tx_power, 16),
                args.deviation,
                sync_word,
            )
        else:
            tx_config = config.TXConfig.from_ism(
                frequency,
                modulation,
                baud_rate,
                float(args.tx_power),
                args.deviation,
                sync_word,
            )

    except ValueError as e:
        print(f"Error: {e}")
        return

    cc1101 = CC1101(args.device, None)

    if args.config_only:
        cc1101.set_tx_config(tx_config)
    else:
        cc1101.transmit(tx_config, unhexlify(args.packet))

    if args.print_registers:
        config.print_raw_config(cc1101.get_device_config())


def rx(args: argparse.Namespace) -> None:
    """Handle the rx subcommand"""

    modulation = int(args.modulation)
    frequency = float(args.frequency)
    baud_rate = float(args.baud_rate)
    sync_word = int(args.sync_word, 16)
    packet_size = int(args.packet_size)

    try:
        rx_config = config.RXConfig(
            frequency,
            modulation,
            baud_rate,
            sync_word,
            packet_size,
            args.bandwidth,
            args.carrier_sense,
            args.deviation,
        )
    except ValueError as e:
        print(f"Error: {e}")
        return

    cc1101 = CC1101(args.device, rx_config)

    if args.print_registers:
        config.print_raw_config(cc1101.get_device_config())

    if not args.config_only:
        print("Receiving Packets")
        count = 1
        while True:
            for packet in cc1101.receive():
                print(f"[{count}] - {hexlify(packet).decode('ascii')}")
                count += 1

            time.sleep(0.1)


def conf(args: argparse.Namespace) -> None:
    """Handle the conf subcommand"""

    cc1101 = CC1101(args.device, None)

    if args.conf_type == "rx":
        print(cc1101.get_rx_config())

    elif args.conf_type == "tx":
        print(cc1101.get_tx_config())

    elif args.conf_type == "rx_raw":
        config.print_raw_config(cc1101.get_rx_config_raw())

    elif args.conf_type == "tx_raw":
        config.print_raw_config(cc1101.get_tx_config_raw())

    elif args.conf_type == "dev_raw":
        config.print_raw_config(cc1101.get_device_config())


def reset(args: argparse.Namespace) -> None:
    """Handle the reset subcommand"""

    cc1101 = CC1101(args.device, None)
    cc1101.reset()


def main():
    parser = argparse.ArgumentParser(prog="cc1101")
    subparsers = parser.add_subparsers()

    tx_parser = subparsers.add_parser("tx", help="Transmit a Packet")
    tx_parser.add_argument("device", help="CC1101 Device")
    tx_parser.add_argument(
        "modulation",
        type=config.Modulation.from_string,
        choices=list(config.Modulation),
    )
    tx_parser.add_argument("frequency", help="frequency (MHz)")
    tx_parser.add_argument("baud_rate", help="baud rate (kBaud)")
    tx_parser.add_argument("tx_power", help="transmit power (hex or dBm)")
    tx_parser.add_argument("packet", help="packet to transmit (hexadecimal string)")
    tx_parser.add_argument(
        "--sync_word", help="sync word (2 or 4 bytes hexadecimal)", default="0000"
    )
    tx_parser.add_argument(
        "--deviation",
        type=float,
        default=47.607422,
        help="frequency deviation for FSK modulations (MHz)",
    )
    tx_parser.add_argument(
        "--raw",
        action="store_true",
        help="Allow any frequency and use hex values for TX Power",
    )
    tx_parser.add_argument(
        "--config-only",
        action="store_true",
        help="configure the radio, but don't transmit",
    )
    tx_parser.add_argument(
        "--print-registers",
        action="store_true",
        help="print raw register values after configuration",
    )
    tx_parser.set_defaults(func=tx)

    rx_parser = subparsers.add_parser("rx", help="Receive Packets")
    rx_parser.add_argument("device", help="CC1101 Device")
    rx_parser.add_argument(
        "modulation",
        type=config.Modulation.from_string,
        choices=list(config.Modulation),
    )
    rx_parser.add_argument("frequency", help="frequency (MHz")
    rx_parser.add_argument("baud_rate", help="baud rate (kBaud)")
    rx_parser.add_argument("sync_word", help="sync word (2 or 4 bytes hexadecimal)")
    rx_parser.add_argument("packet_size", help="receive packet size (bytes)")
    rx_parser.add_argument(
        "--deviation",
        type=float,
        default=47.607422,
        help="frequency deviation for FSK modulations (MHz)",
    )
    rx_parser.add_argument(
        "--bandwidth",
        type=int,
        choices=config.RXConfig.supported_bandwidths(),
        default=203,
        help="recieve bandwidth (kHz)",
    )
    rx_parser.add_argument(
        "--carrier-sense",
        type=int,
        choices=range(17, 49),
        default=33,
        help="carrier-sense threshold (dB)",
    )
    rx_parser.add_argument(
        "--config-only",
        action="store_true",
        help="configure the radio, but don't receive",
    )
    rx_parser.add_argument(
        "--print-registers",
        action="store_true",
        help="print raw register values after configuration",
    )
    rx_parser.set_defaults(func=rx)

    conf_parser = subparsers.add_parser("config", help="Get Device Configs")
    conf_parser.add_argument("device", help="CC1101 Device")
    conf_parser.add_argument(
        "conf_type",
        help="Config to get",
        choices=["rx", "tx", "rx_raw", "tx_raw", "dev_raw"],
    )
    conf_parser.set_defaults(func=conf)

    reset_parser = subparsers.add_parser("reset", help="Reset Device")
    reset_parser.add_argument("device", help="CC1101 Device")
    reset_parser.set_defaults(func=reset)

    args = parser.parse_args()

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()