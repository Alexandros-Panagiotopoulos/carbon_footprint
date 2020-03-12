from django.test import TestCase
from asset_power.views import read_relative_values_from_csv


class TestViews(TestCase):

    def test_read_relative_values_from_csv_with_single_relative_entry(self):
        path = 'fixtures/testing_csv_files/single_relative_asset_id.csv'
        asset_id = 'test'
        asset_power_all = read_relative_values_from_csv(path, asset_id)
        self.assertEqual(len(asset_power_all), 1)

    def test_read_relative_values_from_csv_without_relative_entry(self):
        path = 'fixtures/testing_csv_files/reduced.csv'
        asset_id = 'test'
        asset_power_all = read_relative_values_from_csv(path, asset_id)
        self.assertEqual(len(asset_power_all), 0)
