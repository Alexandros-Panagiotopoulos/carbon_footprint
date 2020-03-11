from .models import AssetPower


def get_asset_power(asset_id, date):
    path = 'fixtures/power_measurements_' + date + '.csv'
    asset_power_calculator = AssetPower(path, asset_id, date)
    asset_power = asset_power_calculator.calculate_cov_based_asset_power()
    return asset_power
