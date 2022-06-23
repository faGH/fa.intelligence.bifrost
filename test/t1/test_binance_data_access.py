'''This module contains T1 tests for the binance_data_access module.'''

# Setup root directory to allow for importing modules from a different adjacent directory.
import sys
import os

root_repo_path = os.getcwd()
sys.path.append(f'{root_repo_path}/src')

# Testing
import pytest # noqa
from data.config_data_access import ConfigDataAccess # noqa
from data.binance_data_access import BinanceDataAccess # noqa


def test_init_with_invalid_config_should_raise_error():
    expected: str = 'Valid config_data_access is required.'

    with pytest.raises(Exception) as e_info:
        config: ConfigDataAccess = None
        BinanceDataAccess(config_data_access=config)

    assert str(e_info.value) == expected


def test_init_with_valid_config_should_set_correct_base_url():
    config: ConfigDataAccess = ConfigDataAccess()
    expected: str = config.binance_base_api_url
    actual: BinanceDataAccess = BinanceDataAccess(config_data_access=config)

    assert actual.base_url == expected


def test_init_with_valid_config_should_set_correct_data_dir_path():
    config: ConfigDataAccess = ConfigDataAccess()
    expected: str = f'{os.getcwd()}/{config.data_dir_relative_path}'
    actual: BinanceDataAccess = BinanceDataAccess(config_data_access=config)

    assert actual.data_dir_path == expected
