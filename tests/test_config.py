import pytest

from cc1101.config import CommonConfig, Modulation, RXConfig, TXConfig
from cc1101.errors import ConfigException, ConfigError

VALID_FREQUENCY = 433.92
VALID_MODULATION = Modulation.OOK
VALID_BAUD_RATE = 1
VALID_DEVIATION = 1.586914
VALID_TX_POWER = 9.9
VALID_PACKET_LENGTH = 1024
VALID_SYNC_WORD = 0x00000000

def test_freq() -> None:
    assert CommonConfig.frequency_to_config(315.0) == 0x000C1D89
    assert CommonConfig.frequency_to_config(315.0) == 0x000C1D89
    assert CommonConfig.frequency_to_config(433.0) == 0x0010A762
    assert CommonConfig.frequency_to_config(868.0) == 0x00216276
    assert CommonConfig.frequency_to_config(915.0) == 0x0023313B

    assert CommonConfig.frequency_to_config(299.999756) == 0x000B89D8
    assert CommonConfig.frequency_to_config(347.999939) == 0x000D6276
    assert CommonConfig.frequency_to_config(386.999939) == 0x000EE276
    assert CommonConfig.frequency_to_config(463.999786) == 0x0011D89C
    assert CommonConfig.frequency_to_config(778.999878) == 0x001DF627
    assert CommonConfig.frequency_to_config(928.000000) == 0x0023B13B

    CommonConfig.config_to_frequency(0x000B89D8) == 299.999756
    CommonConfig.config_to_frequency(0x000D6276) == 347.999939
    CommonConfig.config_to_frequency(0x000EE276) == 386.999939
    CommonConfig.config_to_frequency(0x0011D89C) == 463.999786
    CommonConfig.config_to_frequency(0x001DF627) == 778.999878
    CommonConfig.config_to_frequency(0x0023B13B) == 928.000000

    CommonConfig.config_to_frequency(0x000C1D89) == 314.999664
    CommonConfig.config_to_frequency(0x0010A762) == 432.999817
    CommonConfig.config_to_frequency(0x00216276) == 867.999939
    CommonConfig.config_to_frequency(0x0023313B) == 915.000000

    with pytest.raises(ConfigException) as e_info:
        CommonConfig.frequency_to_config(0.0)
    assert e_info.value.error == ConfigError.INVALID_FREQUENCY

    with pytest.raises(ConfigException) as e_info:
        CommonConfig.frequency_to_config(464.0)
    assert e_info.value.error == ConfigError.INVALID_FREQUENCY

    with pytest.raises(ConfigException) as e_info:
        CommonConfig.frequency_to_config(999.0)
    assert e_info.value.error == ConfigError.INVALID_FREQUENCY


def test_baud_rate() -> None:
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 0.6) == (0x83, 0x04)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 0.599742) == (0x83, 0x04)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 26.0) == (0x06, 0x0A)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 25.9857) == (0x06, 0x0A)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 250.0) == (0x3B, 0x0D)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 249.939) == (0x3B, 0x0D)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 300.0) == (0x7A, 0x0D)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 299.927) == (0x7A, 0x0D)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 500.0) == (0x3B, 0x0E)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 499.878) == (0x3B, 0x0E)
    assert CommonConfig.baud_rate_to_config(Modulation.FSK_2, 115.051) == (0x22, 0x0C)

    assert CommonConfig.config_to_baud_rate(0x83, 0x04) == 0.59974
    assert CommonConfig.config_to_baud_rate(0x06, 0x0A) == 25.98572
    assert CommonConfig.config_to_baud_rate(0x3B, 0x0D) == 249.93896
    assert CommonConfig.config_to_baud_rate(0x7A, 0x0D) == 299.92676
    assert CommonConfig.config_to_baud_rate(0x3B, 0x0E) == 499.87793
    assert CommonConfig.config_to_baud_rate(0x22, 0x0C) == 115.05127

    with pytest.raises(ConfigException) as e_info:
        CommonConfig.baud_rate_to_config(Modulation.FSK_2, 0.0)
    assert e_info.value.error == ConfigError.INVALID_BAUD_RATE

    with pytest.raises(ConfigException) as e_info:
        CommonConfig.baud_rate_to_config(Modulation.FSK_2, 999.0)
    assert e_info.value.error == ConfigError.INVALID_BAUD_RATE


def test_deviation() -> None:
    CommonConfig.deviation_to_config(1.586914) == (0x00, 0x00)
    CommonConfig.deviation_to_config(380.859375) == (0x07, 0x07)

    CommonConfig.config_to_deviation(0x00, 0x00) == 1.586914
    CommonConfig.config_to_deviation(0x07, 0x07) == 380.859375

    with pytest.raises(ConfigException) as e_info:
        CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, 0.0, VALID_SYNC_WORD)
    assert e_info.value.error == ConfigError.INVALID_DEVIATION

    with pytest.raises(ConfigException) as e_info:
        CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, 400.0, VALID_SYNC_WORD)
    assert e_info.value.error == ConfigError.INVALID_DEVIATION

def test_sync_word() -> None:
    CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_DEVIATION, 0x00000000)
    CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_DEVIATION, 0x0000FFFF)
    CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_DEVIATION, 0xFFFFFFFF)

    with pytest.raises(ConfigException) as e_info:
        CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_DEVIATION, 0xFFFF0000)
    assert e_info.value.error == ConfigError.INVALID_SYNC_WORD

    with pytest.raises(ConfigException) as e_info:
        CommonConfig(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_DEVIATION, 0xAAAABBBB)
    assert e_info.value.error == ConfigError.INVALID_SYNC_WORD

def test_bandwidth() -> None:
    assert RXConfig.bandwidth_to_config(812) == (0x00, 0x00)
    assert RXConfig.bandwidth_to_config(58) == (0x03, 0x03)

    assert RXConfig.config_to_bandwidth(0x00, 0x00) == 812
    assert RXConfig.config_to_bandwidth(0x03, 0x03) == 58

    with pytest.raises(ConfigException) as e_info:
        RXConfig.bandwidth_to_config(0)
    assert e_info.value.error == ConfigError.INVALID_BANDWIDTH

    with pytest.raises(ConfigException) as e_info:
        RXConfig.bandwidth_to_config(400)
    assert e_info.value.error == ConfigError.INVALID_BANDWIDTH

def test_tx_power() -> None:

    for frequency in [315.0, 433.0, 868.0, 915.0]:
        power_table = TXConfig.get_power_table(frequency)
        for hex, dbm in power_table.items():
            assert TXConfig.config_to_tx_power(frequency, hex) == dbm
            assert TXConfig.tx_power_to_config(frequency, dbm) == hex


    with pytest.raises(ConfigException) as e_info:
        TXConfig.config_to_tx_power(123.0, 0xFF)
    assert e_info.value.error == ConfigError.INVALID_FREQUENCY

    with pytest.raises(ConfigException) as e_info:
        TXConfig.config_to_tx_power(433.0, 0xFF)
    assert e_info.value.error == ConfigError.INVALID_TX_POWER

    with pytest.raises(ConfigException) as e_info:
        TXConfig.config_to_tx_power(433.0, -1)
    assert e_info.value.error == ConfigError.INVALID_TX_POWER


def test_to_struct() -> None:
    RXConfig.new(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_PACKET_LENGTH).to_struct()
    TXConfig.new(VALID_FREQUENCY, VALID_MODULATION, VALID_BAUD_RATE, VALID_TX_POWER).to_struct()