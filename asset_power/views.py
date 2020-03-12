from .models import AssetPower
import pandas as pd


def get_asset_power(asset_id, date):
    path = 'fixtures/power_measurements_' + date + '.csv'
    asset_power_all = read_relative_values_from_csv(path, asset_id)
    asset_power_calculator = AssetPower(asset_power_all, date)
    asset_power = asset_power_calculator.calculate_cov_based_asset_power()
    return asset_power


def read_relative_values_from_csv(path, asset_id):
    asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
    asset_power_all = asset_power_all[asset_power_all['AssetId'] == asset_id]
    # If csv file is large with many assetIds we could use an iterator to reduce the used memory
    return asset_power_all
