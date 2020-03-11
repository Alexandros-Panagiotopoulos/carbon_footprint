from django.db import models
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import base64


def calculate_carbon_footprint(carbon_in_and_power, time_id):
    start, end = time_id.split('-')
    carbon_in_and_power['asset_power'] = carbon_in_and_power['asset_power'].div(2)
    carbon_in_and_power['carbon_footprint'] = carbon_in_and_power['asset_power'] * carbon_in_and_power['carbon_intensity']
    return carbon_in_and_power.iloc[int(start)-1:int(end)]


def plot_carbon_footprint(footprint, asset_id, date):
    footprint['carbon_footprint'].plot(kind='bar')
    plt.title('Asset ' + asset_id + ' on ' + date, fontsize=15, pad=10)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel('Carbon Footprint [gCO2eq]')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


def create_df_from_objects(half_hour_data):
    time_period = []
    asset_power = []
    carbon_intensity = []
    for i in range(len(half_hour_data)):
        time_period.append(half_hour_data[i].time_period)
        asset_power.append(half_hour_data[i].asset_power)
        carbon_intensity.append(half_hour_data[i].carbon_intensity)
    df = pd.DataFrame(list(zip(asset_power, carbon_intensity)), index=time_period,
                      columns=['asset_power', 'carbon_intensity'])
    df.index.name = 'Time Period'
    print(df)
    return df


def create_df_from_df_and_list(lst, df):
    df['carbon_intensity'] = lst
    return df


class ValidateInput:
    def __init__(self, asset_id, date, time_id):
        self.asset_id = asset_id
        self.date = date
        self.time_id = time_id
        self.min_asset_len = 6
        self.max_asset_len = 15

    def validate_asset_id(self):
        if not isinstance(self.asset_id, str) or not (self.min_asset_len < len(self.asset_id) < self.max_asset_len):
            raise InvalidAssetId

    def validate_date(self):
        try:
            date = datetime.strptime(self.date, '%Y-%m-%d').date()
        except ValueError:
            raise InvalidDateFormat
        else:
            path = 'fixtures/power_measurements_' + str(date) + '.csv'
            with open(path, encoding='utf-8') as f_obj:
                f_obj.read()

    def validate_time_id(self):
        try:
            start, end = self.time_id.split('-')
        except ValueError:
            raise InvalidTimeId
        else:
            if not 1 <= int(start) <= int(end) <= 48:
                raise InvalidTimeId

    def is_valid(self):
        self.validate_asset_id()
        self.validate_date()
        self.validate_time_id()


class HalfHourFootprintQuerySet(models.QuerySet):
    def asset_date(self, asset_id, date):
        return self.filter(
            asset_id=asset_id, date=date,
        )


class HalfHourFootprint(models.Model):
    date = models.DateField()
    time_period = models.CharField(max_length=15)
    asset_id = models.CharField(max_length=15)
    asset_power = models.FloatField()
    carbon_intensity = models.FloatField()

    objects = HalfHourFootprintQuerySet.as_manager()

    def __str__(self):
        return"On {0} during {1} the average power of asset {2} was {3} kW and the UK carbon intensity {4} gCO2eq/KWh"\
            .format(self.date, self.time_period, self.asset_id, self.asset_power, self.carbon_intensity)


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidAssetId(Error):
    """Raised when the item is out of stock"""
    pass


class InvalidDateFormat(Error):
    """Raised when the price of an item is not positive"""
    pass


class InvalidTimeId(Error):
    """Raised when the price of an item is not positive"""
    pass
