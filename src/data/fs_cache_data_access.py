from .config_data_access import ConfigDataAccess
import os
import os.path
import json
from pathlib import Path


class FsCacheDataAccess():
    '''A proxy to the file system for the respective cache directory configured.'''
    def __init__(self, config_data_access: ConfigDataAccess):
        if config_data_access is None:
            raise Exception('Valid config_data_access is required.')

        self.data_dir_path = f'{os.getcwd()}/{config_data_access.data_dir_relative_path}'

    def get_from_cache(self, key: str):
        '''Fetch data from cache should the key exist. Otherwise None.'''
        if key is None:
            raise Exception('Valid key is required.')

        file_name: str = f'{self.data_dir_path}/{key}.fa'
        does_file_exist: bool = os.path.isfile(file_name)

        if not does_file_exist:
            return None

        with open(file_name, 'r') as f:
            return json.loads(f.read())

    def write_to_cache(self, key: str, data):
        '''Write data to the cache for a given key.'''
        if key is None:
            raise Exception('Valid key is required.')

        if data is None:
            raise Exception('Valid data is required.')

        Path(self.data_dir_path).mkdir(parents=True, exist_ok=True)

        file_name: str = f'{self.data_dir_path}/{key}.fa'

        with open(file_name, 'w') as f:
            f.write(json.dumps(data))
