from django.shortcuts import render
from django.http import HttpResponse

from carbon_intensity.views import get_carbon_intensity
from asset_power.views import get_asset_power
from .models import calculate_carbon_footprint, HalfHourFootprint, ValidateInput, plot_carbon_footprint
from .models import create_df_from_objects, create_df_from_df_and_list
from .models import InvalidAssetId, InvalidDateFormat, InvalidTimeId


def get_carbon_footprint(request, asset_id, date, time_id):
    valid, message = validate_input(asset_id, date, time_id)
    if not valid:
        return HttpResponse(message, status=400)
    carbon_intensity_and_asset_power = get_carbon_intensity_and_asset_power(asset_id, date)
    carbon_footprint = calculate_carbon_footprint(carbon_intensity_and_asset_power, time_id)
    graphic = plot_carbon_footprint(carbon_footprint, asset_id, date)
    return render(request, 'graphic.html', {'graphic': graphic})


def get_carbon_intensity_and_asset_power(asset_id, date):
    half_hour_data = HalfHourFootprint.objects.asset_date(asset_id, date)
    if half_hour_data:
        df = create_df_from_objects(half_hour_data)
        return df
    else:
        carbon_intensity = get_carbon_intensity(date)
        asset_power = get_asset_power(asset_id, date)
        populate_db(carbon_intensity, asset_power, asset_id, date)
        df = create_df_from_df_and_list(carbon_intensity, asset_power)
        return df


def populate_db(carbon_intensity, asset_power, asset_id, date):
    for i in range(len(carbon_intensity)):
        entry = HalfHourFootprint(date=date, time_period=asset_power.index.values[i], asset_id=asset_id,
                                  asset_power=asset_power.iloc[i]['asset_power'], carbon_intensity=carbon_intensity[i])
        entry.save()


def validate_input(asset_id, date, time_id):
    validation = ValidateInput(asset_id, date, time_id)
    try:
        validation.is_valid()
    except InvalidAssetId:
        return False, 'Invalid asset ID'
    except InvalidDateFormat:
        return False, 'Invalid date format, please provide date into %Y %b %d format'
    except FileNotFoundError:
        return False, 'No csv file found, please check if there are available asset data the specific date'
    except InvalidTimeId:
        return False, 'Invalid time ID, please separate the start and end integers time-ID numbers (from 1 to 48) with "-"'
    else:
        return True, None
