'''This module contains T1 tests for the fs_cache_data_access module.'''

# Setup root directory to allow for importing modules from a different adjacent directory.
import sys
import os

root_repo_path = os.getcwd()
sys.path.append(f'{root_repo_path}/src')

# Testing
import pytest # noqa
from data.config_data_access import ConfigDataAccess # noqa
from data.fs_cache_data_access import FsCacheDataAccess # noqa

# Clear out test data.
import glob # noqa

config = ConfigDataAccess()
config.data_dir_relative_path = f'{config.data_dir_relative_path}_tmp'
files = glob.glob(f'{config.data_dir_relative_path}/*')
for f in files:
    os.remove(f)


def test_init_with_invalid_config_should_raise_error():
    expected: str = 'Valid config_data_access is required.'

    with pytest.raises(Exception) as e_info:
        config: ConfigDataAccess = None
        FsCacheDataAccess(config_data_access=config)

    assert str(e_info.value) == expected


def test_init_with_valid_config_should_set_correct_data_dir_path():
    config: ConfigDataAccess = ConfigDataAccess()
    expected: str = f'{os.getcwd()}/{config.data_dir_relative_path}'
    actual: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

    assert actual.data_dir_path == expected


def test_get_from_cache_with_invalid_key_should_raise_error():
    expected: str = 'Valid key is required.'

    with pytest.raises(Exception) as e_info:
        config: ConfigDataAccess = ConfigDataAccess()
        instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

        instance.get_from_cache(key=None)

    assert str(e_info.value) == expected


def test_get_from_cache_with_valid_key_non_existing_file_should_return_none():
    expected = None
    non_existing_key: str = 'RandomKey'
    config: ConfigDataAccess = ConfigDataAccess()
    instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

    config.data_dir_relative_path = f'{config.data_dir_relative_path}_tmp'
    actual = instance.get_from_cache(key=non_existing_key)

    assert actual == expected


def test_get_from_cache_with_valid_key_and_existing_file_should_return_data():
    expected_data = ['hello', 'world']
    key: str = 'test.write'
    config: ConfigDataAccess = ConfigDataAccess()
    config.data_dir_relative_path = f'{config.data_dir_relative_path}_tmp'
    instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

    instance.write_to_cache(key=key, data=expected_data)

    actual = instance.get_from_cache(key=key)

    assert actual == expected_data


def test_write_to_cache_with_invalid_key_should_raise_error():
    expected: str = 'Valid key is required.'

    with pytest.raises(Exception) as e_info:
        key: str = None
        data = 'Hello World'
        config: ConfigDataAccess = ConfigDataAccess()
        instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

        instance.write_to_cache(key=key, data=data)

    assert str(e_info.value) == expected


def test_write_to_cache_with_invalid_data_should_raise_error():
    expected: str = 'Valid data is required.'

    with pytest.raises(Exception) as e_info:
        key: str = 'test.key'
        data = None
        config: ConfigDataAccess = ConfigDataAccess()
        instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

        instance.write_to_cache(key=key, data=data)

    assert str(e_info.value) == expected


def test_write_to_cache_with_valid_params_should_write_file():
    key: str = 'test.key'
    data = ['test', 'data']
    config: ConfigDataAccess = ConfigDataAccess()
    config.data_dir_relative_path = f'{config.data_dir_relative_path}_tmp'
    instance: FsCacheDataAccess = FsCacheDataAccess(config_data_access=config)

    instance.write_to_cache(key=key, data=data)

    file_name: str = f'{instance.data_dir_path}/{key}.fa'
    does_file_exist: bool = os.path.isfile(file_name)

    assert does_file_exist
