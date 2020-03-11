import pandas as pd
import numpy as np


class AssetPower:

    def __init__(self, path, asset_id, date):
        self.path = path
        self.asset_id = asset_id
        self.date = pd.to_datetime(date, format='%Y-%m-%d')
        asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
        self.asset_power_all = asset_power_all[asset_power_all['AssetId'] == asset_id]
        # If csv file is large with many assetIds we could use an iterator to reduce the used memory

    def calculate_cov_based_asset_power(self):
        self.asset_power_all['Time'] = pd.to_datetime(self.asset_power_all['Time'], format='%Y-%m-%d %H:%M:%S.%f')
        self.asset_power_all = self.asset_power_all.sort_values('Time')
        self.implement_cov()
        asset_power = self.resample_by_half_hour()
        return asset_power

    def implement_cov(self):
        cov_threshold = 0.05    # COV threshold decided equal to 5%
        time_interval = 5       # A value is recorded at least every 5 minutes
        e = 0.0001              # Small value to avoid dividing by zero, more sophisticated solution can be applied
        time_p = pd.to_datetime(0)
        value_p = 0
        for idx, row in self.asset_power_all.iterrows():
            try:
                if pd.Timedelta(self.asset_power_all.loc[idx, 'Time'] - time_p).seconds / 60 < time_interval and\
                        abs(self.asset_power_all.loc[idx, 'Value'] - value_p) / (value_p + e) < cov_threshold:
                    self.asset_power_all.loc[idx, 'Value'] = None
                else:
                    time_p = self.asset_power_all.loc[idx, 'Time']
                    value_p = self.asset_power_all.loc[idx, 'Value']
            except ZeroDivisionError:
                time_p = self.asset_power_all.loc[idx, 'Time']
                value_p = self.asset_power_all.loc[idx, 'Value']
        self.asset_power_all.dropna(inplace=True)

    def resample_by_half_hour(self):
        start = self.date + (pd.Timedelta('1 second')/10)
        end = start + pd.Timedelta('1 days')
        delta = pd.Timedelta((end - start)/48)

        #   The last value of half hour periods is saved to fill missing values
        asset_power_last = self.asset_power_all.groupby(pd.cut(self.asset_power_all["Time"],
                                                          np.arange(start-delta, end, delta)))['Value'].last()
        asset_power_last = pd.DataFrame(asset_power_last).reset_index()
        asset_power_last.columns = ['DateTime', 'last_value']
        asset_power_last['last_value'].fillna(method='ffill', inplace=True)

        #   The mean value is being used for resapling while in case of missing values the last provided value is used
        asset_power = self.asset_power_all.groupby(pd.cut(self.asset_power_all["Time"],
                                                          np.arange(start, end+delta, delta)))['Value'].mean()
        asset_power = pd.DataFrame(asset_power).reset_index()
        asset_power.columns = ['DateTime', 'asset_power']
        asset_power['asset_power'].fillna(asset_power_last['last_value'], inplace=True)

        asset_power.set_index('DateTime', inplace=True)
        #   Format index to receive a string of half hour time period
        asset_power.index = asset_power.index.map(str)
        asset_power.index = asset_power.index.str[12:17] + '-' + asset_power.index.str[-16:-11]
        return asset_power
