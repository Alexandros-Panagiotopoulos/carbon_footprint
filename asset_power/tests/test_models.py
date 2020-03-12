from django.test import TestCase
from asset_power.models import AssetPower

import pandas as pd


class TestModels(TestCase):

    def setUp(self):
        self.asset_id = 'abc123xyz'
        self.date = '2019-11-25'
        path = 'fixtures/testing_csv_files/values_with_high_time_difference.csv'
        asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
        self.asset_power_all = asset_power_all[asset_power_all['AssetId'] == self.asset_id]

    def test_calculate_cov_based_all_values_read(self):
        path = 'fixtures/testing_csv_files/reduced.csv'
        asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
        asset_power_all = asset_power_all[asset_power_all['AssetId'] == self.asset_id]
        asset_power_calculator = AssetPower(asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        time = pd.to_datetime('2019-11-25 00:50:00.0', format='%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(asset_power_calculator.asset_power_all['Time'].iloc[0], time)
        self.assertEqual(asset_power['asset_power'].iloc[1], 1550)

    def test_calculate_cov_based_ignore_similar_values(self):
        path = 'fixtures/testing_csv_files/ignore_similar_values.csv'
        asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
        asset_power_all = asset_power_all[asset_power_all['AssetId'] == self.asset_id]
        asset_power_calculator = AssetPower(asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        self.assertEqual(asset_power['asset_power'].iloc[1], 1600)

    def test_calculate_cov_based_read_values_with_high_time_difference(self):
        asset_power_calculator = AssetPower(self.asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        self.assertEqual(asset_power['asset_power'].iloc[1], 1598)

    def test_calculate_cov_fill_nan_values_with_last_value(self):
        asset_power_calculator = AssetPower(self.asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        self.assertEqual(asset_power['asset_power'].iloc[2], 1596)
        self.assertEqual(asset_power['asset_power'].iloc[47], 1596)

    def test_calculate_cov_fill_index_values_and_format(self):
        asset_power_calculator = AssetPower(self.asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        self.assertEqual(asset_power.index.values[0], '00:00-00:30')
        self.assertEqual(asset_power.index.values[47], '23:30-00:00')
        self.assertEqual(len(asset_power), 48)

    def test_calculate_cov_fill_by_pass_zero_division(self):
        path = 'fixtures/testing_csv_files/by_pass_zero_division.csv'
        asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
        asset_power_all = asset_power_all[asset_power_all['AssetId'] == self.asset_id]
        asset_power_calculator = AssetPower(asset_power_all, self.date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        self.assertEqual(asset_power['asset_power'].iloc[1], -0.0001)
