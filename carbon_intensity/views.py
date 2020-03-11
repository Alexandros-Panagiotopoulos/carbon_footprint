import urllib.request
import json

from datetime import datetime
from datetime import timedelta


def get_carbon_intensity(date):
    url = 'https://api.carbonintensity.org.uk/intensity/'
    start_date = datetime.strptime(date, '%Y-%m-%d').date()
    end_date = start_date + timedelta(days=1)
    url = '{}{}/{}/'.format(url, start_date, end_date)
    response = urllib.request.urlopen(url).read()
    carbon_intensity = deserialize_carbon_intensity(response)
    return carbon_intensity


def deserialize_carbon_intensity(json_type_data):
    deserialized_carbon_intensity = []
    deserialized_response = json.loads(json_type_data)
    half_hours_list = next(iter(deserialized_response.values()))
    for half_hour in half_hours_list:
        deserialized_carbon_intensity.append(half_hour["intensity"]["actual"])
    return deserialized_carbon_intensity[1:]    # First element excluded as it belongs on previous day
