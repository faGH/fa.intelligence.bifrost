class ConfigDataAccess():
    '''A class holding all static application configuration.'''
    def __init__(self):
        self.window_length_in_days = 60
        self.data_dir_relative_path = 'pair_data'
        self.binance_base_api_url = 'https://api.binance.com/api/v3'
