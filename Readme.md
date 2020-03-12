# Task for Python Developers


## Overview
You can use any framework or library you like, however you should provide some explanation on how to reproduce the calculations in your code on our machines.  

Please take 1 to 2 hours to complete the task with as much details as you can.  
We are providing all the data in files as a shortcut to easily complete the task, however we are looking for how you deal with APIs and databases.  
We are looking after the way you structure your code,documentation, tests, database/files schema.  

When taking shortcuts please explain why in comments so we know.  
If you end up with some pieces of functionality not completely working due to lack of time, then it’s fine to submit that as well with some comments explaining.  
Comments with ideas and reasons for improvement are welcome as well.  

We want to know the half-hourly “carbon footprint” for a given asset.  
The carbon footprint, measured in gCO2eq, is defined as the electricity consumed by the asset in the given half-hour (the energy measured in kWh)  
multiplied by the carbon intensity for that half hour (in gCO2eq/KWh).

There will be 48 rows of data with HalfHourId from 1 to 48.

## Requirements

The task involves the following requirements:
-  processing data from different data sources e.g. APIs and CSV files
-  resampling the data to a common rate
-  performing the calculations
-  storing the results in a SQLite database (or CSV file as a shortcut)
-  retrieving the results from the storage filtering them by HalfHourId range 14-20
-  plot the retrieval (or the calculation, or the API data, depending on what is easiest/quicker)

## Data sources

We need to combine data about the actual/forecast carbon footprint with the power measurement of the asset identified by the ID abc123xyz.

### Carbon intensity data

The Carbon Intensity data can be retrieved via the API provided by National Grid.  
API docs at: https://carbon-intensity.github.io/api-definitions/#intensity  
Sample API call retrieving gCO2eq/KWhe (providing start/end as input parameters):  
curl -X GET \
https://api.carbonintensity.org.uk/intensity/2019-11-25/2019-11-26 \
-H 'Accept: application/json'

If for any reason the API retrieval does not work, then the file carbon_intensity_2019-11-25.json can be used instead.  

### Power measurements

The data for one day power measurements (KW) is in the CSV file power_measurements_2019-11-25.csv.  

#### On the COV rule

The electrical power is measured following the COV rule (change of value) because we want to minimise the amount of data sent from the  
remote asset to our cloud back-end.  
We want to save on communication costs and storage costs (DBs).  
This means that, instead of regularly sampling the power and recording that value, we will only record the value when it changes by some  
predefined amount (the threshold). 
Sometimes, we will combine COV sampling with regular sampling, to ensure that we record at least one point in a given interval.  
Those power measurements are absolute values representing that asset.  
Let’s say for example that at time 15:00 UTC the power measure is 100.0 kW, then at 15:01 UTC the power measure is 92.0 kW.  
- If we set the COV threshold to be a percentage of 5% (but we could set a threshold to be absolute instead, or a combination of rules),  
then anything lower/higher than 95/105 (compared to the previous measurement of 100.0 kW) should be sent as a measurement. Given that
we are measuring 92.0 then we send that message.
- If the threshold is set to 10%, then we should send anything below 90 or above 110, so we won’t send the measurement of 92.0 kW.  
The power values can be negative or positive because an asset e.g. a battery can charge (taking energy from the grid) or discharge  
(sending energy to the grid).

#### How to calculate the carbon footprint

Given the above definition for COV you should resample this power data to 1 row for each HalfHourId so the you can easily combine it with  
the Carbon Intensity data.
If this takes too much time, then just take 1 row from that half-hour interval and use it as the value for that HalfHourId.  
If there are no samples for that half-hour, then just use the previous value from the previous HalfHourId.



# Solution

The solution was created using Python 3.8.2 and Django 3.0.4

In order to run the code, the following libraries should be installed:
pandas
matplotlib

The endpoint can receive a GET request at `/footprint` in the following format

`footprint/<asset_id>/<date>/<time_id>/`

So, the request according to the task should be 

`http://127.0.0.1:8000/footprint/abc123xyz/2019-11-25/14-20/`

The response is an image of a column chart visualising the carbon footprint of the asset at the specified time period separated into half-hour intervals.
In order to see the image the postman software can be used and set the response at `body` and `preview`.
The response for the specific task is all zeroes as there are no entries at the specified period. So an empty column chart is shown.  
A different time period can be selected to see the visualisation of the carbon footprint.


## Stracture

The project is separated into three different django applications with different roles:

- ### footprint_calc
- ### carbon_intensity
- ### asset_power

### footprint_calc

The footprint_calc application coordinates the solution. The code in the views.py of the app is implementing the following:

- Receives the get request from the url.py (located in the carbon_footprint directory)
- Validates the get request (if request is invalid a 400 code is return with appropriate message)
- Queries for the necessary data in the database
- calls the carbon intensity application (if data weren't found in the database)
- calls the asset_power application (if data weren't found in the database)
- populates the database with the retrieved data (if data weren't found in the database)
- calculates the carbon_footprint
- creates the plot of the carbon_footprint
- returns the plot as a response to the GET request

The logic is at views.py while the implementation and the class connected to the database are located at the models.py of the app

### carbon_intensity

The carbon_intensity application is responsible for providing the carbon intensity data for UK in a specific day.
It collects the data from the specified sourse doing a GET request and then deserialises the json response and returns a list of the "actual" values.

All the code is stored at the views.py of the application


### asset_power

The asset power application is responsible for reading the csv file and do all necessary calculations in order to return the desired values

More specifically the views.py is reading the csv and calls the class `AssetPower` at the model.py in order to make the calculations.
At the model.py of the app the COV rule and the resampling at 48 half-hours is implemented using pandas dataframes


## Improvements

Due to time limitation some parts are omitted but could be added in the future if needed like:

- A validation of the response from the get request to the carbon intensity sourse.  As the external sourse is not controlled by us, any change would result into coding crush
- Much more many tests are required. Currently only the asset_power application is tested as it contains the most complicated logic at the model.py
- More validations could be implemented also by using django standard or custom Middleware classes for cleaner code
- A better looking plot could be designed

## Assumptions

- The entire csv file is available for reading from the endpoint.
- The values at the csv files are treated as "trusted" without validation and it is expected to be consistent at specific format including naming
- A value at the first half-hour of the day is always provided at the csv file so as to have an indication of the asset power.
- Only a single day or part of it is expected to be asked in every request.
- Every csv file could represents data for specific date but for several assets with different asset ID
- The database is populated only if there is a GET request.  
If we need to store data for every day then a cron should be implemented in order to fire the code once per day
