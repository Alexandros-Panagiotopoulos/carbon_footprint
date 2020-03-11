from .models import calculate_asset_power


def get_asset_power(asset_id, date):
    path = 'fixtures/power_measurements_' + date + '.csv'
    asset_power = calculate_asset_power(path, asset_id, date)
    return asset_power
