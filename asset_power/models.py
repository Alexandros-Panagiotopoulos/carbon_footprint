import pandas as pd
import numpy as np


def calculate_asset_power(path, asset_id, date):
    asset_power_all = pd.read_csv(path, usecols=['Time', 'AssetId', 'Value'], encoding='utf-8')
    asset_power_all = asset_power_all[asset_power_all['AssetId'] == asset_id]
    # If csv file is large with many assetIds we could use an iterator to reduce the used memory
    asset_power = calculate_cov_based_df(asset_power_all, date)
    return asset_power


def calculate_cov_based_df(asset_power_all, date):
    date = pd.to_datetime(date, format='%Y-%m-%d')
    asset_power_all['Time'] = pd.to_datetime(asset_power_all['Time'], format='%Y-%m-%d %H:%M:%S.%f')
    asset_power_all = asset_power_all.sort_values('Time')
    asset_power_all = implement_cov(asset_power_all)
    asset_power = resample_by_half_hour(asset_power_all, date)
    return asset_power


def implement_cov(asset_power_all):
    cov_threshold = 0.05    # COV threshold decided equal to 5%
    time_interval = 5      # A value is recorded at least every 5 minutes
    e = 0.0001              # Small value to avoid dividing by zero, more sophisticated solution can be applied
    time_p = pd.to_datetime(0)
    value_p = 0
    for idx, row in asset_power_all.iterrows():
        try:
            if pd.Timedelta(asset_power_all.loc[idx, 'Time'] - time_p).seconds / 60 < time_interval and\
                    abs(asset_power_all.loc[idx, 'Value'] - value_p) / (value_p + e) < cov_threshold:
                asset_power_all.loc[idx, 'Value'] = None
            else:
                time_p = asset_power_all.loc[idx, 'Time']
                value_p = asset_power_all.loc[idx, 'Value']
        except ZeroDivisionError:
            time_p = asset_power_all.loc[idx, 'Time']
            value_p = asset_power_all.loc[idx, 'Value']
    asset_power_all.dropna(inplace=True)
    return asset_power_all


def resample_by_half_hour(asset_power_all, date):
    start = date + (pd.Timedelta('1 second')/10)
    end = start + pd.Timedelta('1 days')
    delta = pd.Timedelta((end - start)/48)

    #   The last value of half hour periods is saved to fill missing values
    asset_power_last = asset_power_all.groupby(pd.cut(asset_power_all["Time"],
                                                      np.arange(start-delta, end, delta)))['Value'].last()
    asset_power_last = pd.DataFrame(asset_power_last).reset_index()
    asset_power_last.columns = ['DateTime', 'last_value']
    asset_power_last['last_value'].fillna(method='ffill', inplace=True)

    #   The mean value is being used for resapling while in case of missing values the last provided value is used
    asset_power = asset_power_all.groupby(pd.cut(asset_power_all["Time"],
                                                 np.arange(start, end+delta, delta)))['Value'].mean()
    asset_power = pd.DataFrame(asset_power).reset_index()
    asset_power.columns = ['DateTime', 'asset_power']
    asset_power['asset_power'].fillna(asset_power_last['last_value'], inplace=True)

    asset_power.set_index('DateTime', inplace=True)
    asset_power.index = asset_power.index.map(str)
    asset_power.index = asset_power.index.str[12:17] + '-' + asset_power.index.str[-16:-11]
    return asset_power
