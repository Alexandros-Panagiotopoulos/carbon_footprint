from django.test import TestCase
from asset_power.models import AssetPower

import pandas as pd


class TestModels(TestCase):

    def test_initialization_of_class_with_single_relative_entry(self):
        path = 'fixtures/testing_csv_files/single_relative_asset_id.csv'
        asset_id = 'test'
        date = '2019-11-25'
        asset_power_calculator = AssetPower(path, asset_id, date)
        self.assertEqual(len(asset_power_calculator.asset_power_all), 1)

    def test_initialization_of_class_without_relative_entry(self):
        path = 'fixtures/testing_csv_files/reduced.csv'
        asset_id = 'test'
        date = '2019-11-25'
        asset_power_calculator = AssetPower(path, asset_id, date)
        self.assertEqual(len(asset_power_calculator.asset_power_all), 0)

    def test_calculate_cov_based_time_assignment_and_sorting(self):
        path = 'fixtures/testing_csv_files/reduced.csv'
        asset_id = 'abc123xyz'
        date = '2019-11-25'
        asset_power_calculator = AssetPower(path, asset_id, date)
        asset_power = asset_power_calculator.calculate_cov_based_asset_power()
        time = pd.to_datetime('2019-11-25 05:54:08.8640000', format='%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(asset_power_calculator.asset_power_all['Time'].iloc[0], time)

    def test_implement_cov(self):

        self.assertEqual(1, 1)

    def test_resample_by_half_hour(self):

        self.assertEqual(1, 1)
