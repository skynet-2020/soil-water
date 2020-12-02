# -*- coding: utf-8 -*-

import os
from collections import defaultdict
import math 
import xlrd # For reading xls sheets; this is what pandas calls in the background.
import csv # For writing to a csv.
import pprint
import datetime


from constants import DATA_DIRECTORY

# this is a class that is created for sensors in the experiment
# each object holds valuable information from the lookup table
# each object also holds the data in its nested dictionaries
class Logger_Port:

    def __init__(self, port, logger, title, column, sensor, sensor_units, mammal_treatment, burn_treatment, block, precipitation, sensor_number, sensor_measurement, prop_pressure):
        self.port = port 
        self.logger = logger
        self.title = title
        self.column = column
        self.sensor = sensor
        self.sensor_units = sensor_units
        self.mammal_treatment = mammal_treatment
        self.burn_treatment = burn_treatment
        self.block = block
        self.precipitation = precipitation
        self.sensor_assigned_number = sensor_number
        self.prop_pressure = prop_pressure
        # VWC or WP
        self.sensor_measurement = sensor_measurement
        
        # nested dictionaries that hold the raw data
        self.dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
        self.dict1 = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        # self.dict2 = defaultdict(lambda: defaultdict(lambda: defaultdict(Value)))
        self.dict3 = defaultdict(lambda: defaultdict(list))
        self.dict4 = defaultdict(lambda: defaultdict(float))

        self.date_list = []
        self.test_bool = True

        ## keys = date, values = daily average of SM data
        ## used to minima/maxima
        # self.sm_values_dict = {}

        ## this holds the min/max date ranges for wetting events
        self.minima_maxima_list = []
        self.maxima_list = []

        ## this holds the date range for arbitrary_rain_event_numbers
        self.rain_event_date_range = []

        ## boolean to show if there is data present for the desired date range
        self.data_present = True

        ## list that holds dictionaries
        self.dict_list = []

## tests bool functions in python
def Test_Bool(test_variable):
    if test_variable == "dumbhead":
        return True
    else:
        return False

def Append_To_Object_List(object_list, logger_object):
    object_list.append(logger_object)

## returns true if the object has not been created
def Object_Not_Created(object_list, object_logger, object_title, object_column, object_sensor, object_mammal, object_burn, object_block, object_precipitation):
    test_bool = True
    if object_list == []:
        test_bool = True
    for object in object_list:
        if object.logger == object_logger and object.title == object_title and object.column == object_column:
            test_bool = False
    
    return test_bool
        
## returns the port number (e.g. 1s)
def Create_Object_Port(header_dict, value):
    index = int(value)
    string_port = header_dict["header_one"][index]
    return string_port.split()[1]

## returns a list of column numbers with VWC or WP sensor fields in header line 2
def Header_Two_List(header_dict, user_measurement):
    header_two_list = []
    count = 0
    for value in header_dict["header_two"]:
        if user_measurement == "VWC":
            if value == "GS3 Moisture/Temp/EC" or value == "GS1 Soil and Media Moisture" or value == "5TM Moisture/Temp" or value == "5TE Moisture/Temp/EC" or value == "EC-TM Moisture/Temp" or value == "ECRN-50 Precipitation":
                header_two_list.append(count)
        if user_measurement == "WP":
            if value == "MPS-6 Water Potential/Temp" or value == "MPS-2 Water Potential/Temp" or value == "ECRN-50 Precipitation":
                header_two_list.append(count)
        count += 1
    return header_two_list

## returns a list of column numbers with VWC or WP units in header line 3
def Header_Three_List(header_dict, user_measurement):
    header_three_list = []
    count = 0
    for value in header_dict["header_three"]:
        if user_measurement == "VWC":
            if value == "m³/m³ VWC" or value == "mm Precip":
                header_three_list.append(count) 
                
        if user_measurement == "WP":
            if value == "kPa Potential" or value == "mm Precip":
                header_three_list.append(count)
        count += 1
    return header_three_list

## this function checks to see if the file in the look-up table has dates in the user_date_range
def Create_Shared_Values_List(list1, list2):
    new_list = []
    for element in list1:
        for element2 in list2:
            if element == element2:
                new_list.append(element)
    return new_list

## takes a month string (i.e. "May") and returns "05" (mm)
def Return_Integer_Month(month_string):
    if month_string == "Jan":
        return "01"
    elif month_string == "Feb":
        return "02"
    elif month_string == "Mar":
        return "03"
    elif month_string == "Apr":
        return "04"
    elif month_string == "May":
        return "05"
    elif month_string == "Jun":
        return "06"
    elif month_string == "Jul":
        return "07"
    elif month_string == "Aug":
        return "08"
    elif month_string == "Sep":
        return "09"
    elif month_string == "Oct":
        return "10"
    elif month_string == "Nov":
        return "11"
    else:
        return "12"

## takes the end date provided by the title of the raw data file 
# and converts it to mm/dd/yyyy
def File_End_Date(filename):
    char_list = []
    string_list = []

    date_piece = filename.split()[1]
    fields = date_piece.split("-")
    date = fields[0]


    for char in date:
        if char.isdigit():
            char_list.append(char)
        
        else:
            string_list.append(char)

    if len(char_list) == 4:
        year_list = char_list[2:]
        del char_list[2:]
    else: 
        year_list = char_list[1:]
        del char_list[1:]

    year = ''.join(year_list)
    year = ("20" + year)
    day = ''.join(char_list)
    if len(day) < 2:
        day = "0" + day
    
    month_string = ''.join(string_list)
    month = Return_Integer_Month(month_string)
    end_date = (year + '-' + month + '-' + day)
    year, month, day = map(int, end_date.split('-'))
    file_date = datetime.date(year, month, day)
    return file_date
   

## takes the filename and the number of entries to create a list of dates contained by each raw data
def File_Begin_Date(file_end_date, records_field):
    num_records = records_field[0]
    num_days = math.ceil(int(num_records) / 24)
    file_begin_date = file_end_date - timedelta(days=num_days)
    return file_begin_date

## returns the datalogger portion of each raw data file filename
def Title_To_LoggerNumber(file_name):
    return file_name.split()[0]

# from datetime import datetime
from dateutil.relativedelta import relativedelta

# creates a date range with hours included; hour is the smallest time unit
def Date_Range(start_date, end_date):
    result = []
    nxt = start_date
    while nxt <= end_date:
        result.append(nxt)
        nxt += relativedelta(hours=+1)
    return result

# creates a date range without hours included; day is smallest time unit
def Date_Range1(start_date, end_date):
    result = []
    nxt = start_date
    while nxt <= end_date:
        result.append(nxt)
        nxt += relativedelta(days=+1)
    return result

## takes a water potential value and thresholds it
def Water_Potential_Threshold(value_to_append):
    test_variable = float(value_to_append)
    if isinstance(test_variable, float):
        if test_variable < -2000:
            test_variable = -2000
        return test_variable

## takes a value from the raw data file and return the calibrated value
def GSone_function(raw_output_float):
    # below is the calibration_one equation
    # corrected_output = 0.0140939 + 0.7711084 * (raw_output_float) - ((1.3367036 * (raw_output_float)-0.27569) * 2)
    corrected_output = 0.87115*(raw_output_float) + 0.01790 
    return corrected_output

## takes a value from the raw data file and returns the calibrated value
def GSthree_function(raw_output_float):
    corrected_output = -1.21536*(raw_output_float**2) + 1.71552*raw_output_float - 0.11103
    return corrected_output

## takes a value from the raw data file and returns the calibrated value
def fiveTM_function(raw_output_float):
    corrected_output = (1.242251 * raw_output_float) - 0.028679
    return corrected_output

def Create_Date_Object(date_string):
    year, month, day, hour, minute, second = map(int, date_string.split('-'))
    date_entry = datetime.date(year, month, day)

    return date_entry

def Create_CETE_Date_Dict():
    CETE_dict = {}

    # 2017
    # fall growth season
    begin_date_fall_2017 = Create_Date_Object('2017-08-15-00-00-00')
    end_date_fall_2017 = Create_Date_Object('2017-10-31-00-00-00')

    # 2018
    # pre-growth season
    begin_date_pre_growth_2018 = Create_Date_Object('2018-03-01-00-00-00')
    end_date_pre_growth_2018 = Create_Date_Object('2018-04-01-00-00-00')

    # spring growth season
    begin_date_growth_2018 = Create_Date_Object('2018-04-07-00-00-00')
    end_date_growth_2018 = Create_Date_Object('2018-05-07-00-00-00')

    # post-growth season
    begin_date_post_growth_2018 = Create_Date_Object('2018-06-16-00-00-00')
    end_date_post_growth_2018 = Create_Date_Object('2018-07-13-00-00-00')

    # summer growth season
    begin_date_summer_2018 = Create_Date_Object('2018-07-14-00-00-00')
    end_date_summer_2018 = Create_Date_Object('2018-08-14-00-00-00')

    # fall growth season
    begin_date_fall_2018 = Create_Date_Object('2018-08-15-00-00-00')
    end_date_fall_2018 = Create_Date_Object('2018-10-31-00-00-00')

    # 2019 season
    # pre-growth season
    begin_date_pre_growth_2019 = Create_Date_Object('2019-04-01-00-00-00')
    end_date_pre_growth_2019 = Create_Date_Object('2019-04-30-00-00-00')

    # spring growth season
    begin_date_growth_2019 = Create_Date_Object('2019-05-01-00-00-00')
    end_date_growth_2019 = Create_Date_Object('2019-05-30-00-00-00')

    # post-growth season
    begin_date_post_growth_2019 = Create_Date_Object('2019-06-16-00-00-00')
    end_date_post_growth_2019 = Create_Date_Object('2019-07-13-00-00-00')

    # summer growth season
    begin_date_summer_2019 = Create_Date_Object('2019-07-14-00-00-00')
    end_date_summer_2019 = Create_Date_Object('2019-08-14-00-00-00')

    # fall growth season
    begin_date_fall_2019 = Create_Date_Object('2019-08-15-00-00-00')
    end_date_fall_2019 = Create_Date_Object('2019-10-31-00-00-00')

    # 2017
    date_list_fall_2017 = Date_Range1(begin_date_fall_2017, end_date_fall_2017)

    # 2018
    date_list_pre_growth_2018 = Date_Range1(begin_date_pre_growth_2018, end_date_pre_growth_2018)
    date_list_growth_2018 = Date_Range1(begin_date_growth_2018, end_date_growth_2018)
    date_list_post_growth_2018 = Date_Range1(begin_date_post_growth_2018, end_date_post_growth_2018)
    date_list_summer_2018 = Date_Range1(begin_date_summer_2018, end_date_summer_2018)
    date_list_fall_2018 = Date_Range1(begin_date_fall_2018, end_date_fall_2018)

    # 2019
    date_list_pre_growth_2019 = Date_Range1(begin_date_pre_growth_2019, end_date_pre_growth_2019)
    date_list_growth_2019 = Date_Range1(begin_date_growth_2019, end_date_growth_2019)
    date_list_post_growth_2019 = Date_Range1(begin_date_post_growth_2019, end_date_post_growth_2019)
    date_list_summer_2019 = Date_Range1(begin_date_summer_2019, end_date_summer_2019)
    date_list_fall_2019 = Date_Range1(begin_date_fall_2019, end_date_fall_2019)

    CETE_dict["date_list_fall_2017"] = date_list_fall_2017
    CETE_dict["date_list_pre_growth_2018"] = date_list_pre_growth_2018
    CETE_dict["date_list_growth_2018"] = date_list_growth_2018
    CETE_dict["date_list_post_growth_2018"] = date_list_post_growth_2018
    CETE_dict["date_list_summer_2018"] = date_list_summer_2018
    CETE_dict["date_list_fall_2018"] = date_list_fall_2018
    CETE_dict["date_list_pre_growth_2019"] = date_list_pre_growth_2019
    CETE_dict["date_list_growth_2019"] = date_list_growth_2019
    CETE_dict["date_list_post_growth_2019"] = date_list_post_growth_2019
    CETE_dict["date_list_summer_2019"] = date_list_summer_2019
    CETE_dict["date_list_fall_2019"] = date_list_fall_2019

    return CETE_dict

# receives a datetime object and returns a string corresponding to season. 
def Assign_Season(date, CETE_dict):

    season = None
    if date in CETE_dict["date_list_fall_2017"]:
        season = "fall"
    elif date in CETE_dict["date_list_pre_growth_2018"]:
        season = "pre_growth"
    elif date in CETE_dict["date_list_growth_2018"]:
        season = "growth"
    elif date in CETE_dict["date_list_post_growth_2018"]:
        season = "post_growth"
    elif date in CETE_dict["date_list_summer_2018"]:
        season = "summer"
    elif date in CETE_dict["date_list_fall_2018"]:
        season = "fall"
    elif date in CETE_dict["date_list_pre_growth_2019"]:
        season = "pre_growth"
    elif date in CETE_dict["date_list_growth_2019"]:
        season = "growth"
    elif date in CETE_dict["date_list_post_growth_2019"]:
        season = "post_growth"
    elif date in CETE_dict["date_list_summer_2019"]:
        season = "summer"
    elif date in CETE_dict["date_list_fall_2019"]:
        season = "fall"
    else:
        season = "winter"
    return season

def Create_BRTE_Date_Dict():
    BRTE_dict = {}

    # 2017
    # fall growth season
    begin_date_fall_2017 = Create_Date_Object('2017-08-15-00-00-00')
    end_date_fall_2017 = Create_Date_Object('2017-10-31-00-00-00')

    # 2018 
    # pre-growth season
    begin_date_pre_growth_2018 = Create_Date_Object('2018-03-01-00-00-00')
    end_date_pre_growth_2018 = Create_Date_Object('2018-04-01-00-00-00')

    # spring growth season
    begin_date_growth_2018 = Create_Date_Object('2018-04-07-00-00-00')
    end_date_growth_2018 = Create_Date_Object('2018-05-07-00-00-00')

    # post-growth season
    begin_date_post_growth_2018 = Create_Date_Object('2018-06-16-00-00-00')
    end_date_post_growth_2018 = Create_Date_Object('2018-07-13-00-00-00')

    # summer growth season
    begin_date_summer_2018 = Create_Date_Object('2018-07-14-00-00-00')
    end_date_summer_2018 = Create_Date_Object('2018-08-14-00-00-00')

    # fall growth season
    begin_date_fall_2018 = Create_Date_Object('2018-08-15-00-00-00')
    end_date_fall_2018 = Create_Date_Object('2018-10-31-00-00-00')

    # 2019 season
    # pre-growth season
    begin_date_pre_growth_2019 = Create_Date_Object('2019-04-01-00-00-00')
    end_date_pre_growth_2019 = Create_Date_Object('2019-04-30-00-00-00')

    # spring growth season
    begin_date_growth_2019 = Create_Date_Object('2019-05-15-00-00-00')
    end_date_growth_2019 = Create_Date_Object('2019-06-15-00-00-00')

    # post-growth season
    begin_date_post_growth_2019 = Create_Date_Object('2019-06-16-00-00-00')
    end_date_post_growth_2019 = Create_Date_Object('2019-07-13-00-00-00')

    # summer growth season
    begin_date_summer_2019 = Create_Date_Object('2019-07-14-00-00-00')
    end_date_summer_2019 = Create_Date_Object('2019-08-14-00-00-00')

    # fall growth season
    begin_date_fall_2019 = Create_Date_Object('2019-08-15-00-00-00')
    end_date_fall_2019 = Create_Date_Object('2019-10-31-00-00-00')

    # 2017
    date_list_fall_2017 = Date_Range1(begin_date_fall_2017, end_date_fall_2017)

    # 2018
    date_list_pre_growth_2018 = Date_Range1(begin_date_pre_growth_2018, end_date_pre_growth_2018)
    date_list_growth_2018 = Date_Range1(begin_date_growth_2018, end_date_growth_2018)
    date_list_post_growth_2018 = Date_Range1(begin_date_post_growth_2018, end_date_post_growth_2018)
    date_list_summer_2018 = Date_Range1(begin_date_summer_2018, end_date_summer_2018)
    date_list_fall_2018 = Date_Range1(begin_date_fall_2018, end_date_fall_2018)

    # 2019
    date_list_pre_growth_2019 = Date_Range1(begin_date_pre_growth_2019, end_date_pre_growth_2019)
    date_list_growth_2019 = Date_Range1(begin_date_growth_2019, end_date_growth_2019)
    date_list_post_growth_2019 = Date_Range1(begin_date_post_growth_2019, end_date_post_growth_2019)
    date_list_summer_2019 = Date_Range1(begin_date_summer_2019, end_date_summer_2019)
    date_list_fall_2019 = Date_Range1(begin_date_fall_2019, end_date_fall_2019)

    BRTE_dict["date_list_fall_2017"] = date_list_fall_2017
    BRTE_dict["date_list_pre_max_trans_2018"] = date_list_pre_growth_2018
    BRTE_dict["date_list_max_trans_2018"] = date_list_growth_2018
    BRTE_dict["date_list_post_max_trans_2018"] = date_list_post_growth_2018
    BRTE_dict["date_list_summer_2018"] = date_list_summer_2018
    BRTE_dict["date_list_fall_2018"] = date_list_fall_2018
    BRTE_dict["date_list_pre_max_trans_2019"] = date_list_pre_growth_2019
    BRTE_dict["date_list_max_trans_2019"] = date_list_growth_2019
    BRTE_dict["date_list_post_max_trans_2019"] = date_list_post_growth_2019
    BRTE_dict["date_list_summer_2019"] = date_list_summer_2019
    BRTE_dict["date_list_fall_2019"] = date_list_fall_2019

    return BRTE_dict

# receives a datetime object and returns a string corresponding to season. 
def Assign_Season_Alternate(date, BRTE_dict):

    season = None
    if date in BRTE_dict["date_list_fall_2017"]:
        season = "fall"
    elif date in BRTE_dict["date_list_pre_max_trans_2018"]:
        season = "pre_growth"
    elif date in BRTE_dict["date_list_max_trans_2018"]:
        season = "growth"
    elif date in BRTE_dict["date_list_post_max_trans_2018"]:
        season = "post_growth"
    elif date in BRTE_dict["date_list_summer_2018"]:
        season = "summer"
    elif date in BRTE_dict["date_list_fall_2018"]:
        season = "fall"
    elif date in BRTE_dict["date_list_pre_max_trans_2019"]:
        season = "pre_growth"
    elif date in BRTE_dict["date_list_max_trans_2019"]:
        season = "growth"
    elif date in BRTE_dict["date_list_post_max_trans_2019"]:
        season = "post_growth"
    elif date in BRTE_dict["date_list_summer_2019"]:
        season = "summer"
    elif date in BRTE_dict["date_list_fall_2019"]:
        season = "fall"
    else:
        season = "winter"

    return season

# writes header line to output file
def Outwrite_Header_Line(user_measurement):
    columns = ["continuous_time", "rodent_treatment", "burn_treatment",
     "precip_treatment", "block", "date", "datalogger", "sensor_assignment", "sensor_type", "year", "month", "propagule_pressure"]
    if user_measurement == "WP":
        outfile3.write(",".join(["daily_average"] + columns) + "\n")
    else:
        outfile1.write(",".join(["daily_average"] + columns) + "\n")

# when given list, this returns a daily average
def Get_Daily_Average(daily_list):
    num_values = 0
    daily_sum = 0
    for value in daily_list:
        num_values += 1
        daily_sum += float(value)
    daily_average = None
    try:
        daily_average = daily_sum/num_values
    except:
        pass 
    return daily_average

# outwrites data to the output file
def Outwrite_Daily_Continuous(object_list, user_date_list1, user_measurement, CETE_dict, BRTE_dict):
    for object in object_list:
        if object.data_present and object.sensor_measurement == user_measurement:
            continuous_time_count = 0
            for date in user_date_list1:
                try:
                    daily_measurement_list = object.dict1[date.year][date.month][date.day]
                except:
                    continue

                list_size = 0
                list_sum = 0
                # get the daily_average
                if len(daily_measurement_list) != 0:
                # print(daily_measurement_list)
                    for value in daily_measurement_list:
                        # print(value)
                        # if float(value) == 42.0:
                        #     continue
                        # elif float(value) == -3764.9509907740517:
                        #     continue
                        # elif float(value) == -3088.593800917666:
                        #     continue
                        # elif float(value) == 3.8334600925445557:
                        #     continue
                        list_size += 1
                        list_sum += float(value)

                        continue

                    if list_size == 0 and list_sum == 0:
                        pass
                    else:
                        
                        daily_average = list_sum/list_size
                        if user_measurement == "WP":
                            if object.sensor_measurement == "WP":
                                season = Assign_Season(date, CETE_dict)
                                season_BRTE = Assign_Season_Alternate(date, BRTE_dict)
                                
                                try:
                                    columns = [str(daily_average), str(continuous_time_count), 
                                    object.mammal_treatment, object.burn_treatment, object.precipitation, object.block,
                                    '{:%Y-%m-%d %H-%M-%S}'.format(date), object.logger, object.title, object.sensor,
                                    str(date.year), str(date.month), object.prop_pressure]
                                    outfile3.write(",".join(columns) + "\n")
                                    continuous_time_count += 1
                                except:
                                    print("exception here che!!!!!")
                                    pass
                            
                        else:
                            if object.sensor_measurement == "VWC":
                                season = Assign_Season(date, CETE_dict)
                                season_BRTE = Assign_Season_Alternate(date, BRTE_dict)
                                try:
                                    columns = [str(daily_average), str(continuous_time_count),
                                    object.mammal_treatment, object.burn_treatment, object.precipitation, object.block,
                                    '{:%Y-%m-%d %H-%M-%S}'.format(date), object.logger, object.title, object.sensor,
                                    str(date.year), str(date.month), str(season), str(season_BRTE), object.prop_pressure]
                                    outfile1.write(",".join(columns) + "\n")
                                    continuous_time_count += 1
                                except:
                                    pass

###############################  MAIN CODE ###################################
## this program is designed to work with daily averages; therefore, date ranges, dictionaries 
## will all be using dates with day as the smallest time unit.

# open the look-up file
#lookup_file = open(f'{DATA_DIRECTORY}/look_up_tables/new_lookup_table.csv', 'r')
lookup_file = open('/Users/joshuagilman/Documents/code/data/look_up_tables/new_lookup_table.csv', 'r')


## get the user entered beginning date
## these dates determine the date range of data that is outputted 
## to the output file
date_entry = raw_input('Enter the beginning date in YYYY-MM-DD-HH-MM-SS format: ')
year, month, day, hour, minute, second = map(int, date_entry.split('-'))
begin_date = datetime.datetime(year, month, day, hour)

# begin_date does not include hour
# these are better for getting daily averages of data
begin_date1 = datetime.date(year, month, day)

## get the user entered end date
date_entry = raw_input('Enter the end date in YYYY-MM-DD-HH-MM-SS format: ')
year, month, day, hour, minute, second = map(int, date_entry.split('-'))
end_date = datetime.datetime(year, month, day, hour)

# end_date that is only date
end_date1 = datetime.date(year, month, day)

# the user tells what measurement type we want
user_measurement = raw_input("Enter measurement (\"VWC\" or \"WP\") ")
user_date_list = Date_Range(begin_date, end_date)
user_date_list1 = Date_Range1(begin_date1, end_date1)

## open files
if user_measurement == "WP":
    outfile3 = open('/Users/joshuagilman/Documents/code/data/new_data_outfiles/WP_daily_new.csv', 'w')
    #outfile3 = open(f'{DATA_DIRECTORY}/new_data_outfiles/WP_daily_new.csv', 'w')
else:
    outfile1 = open('/Users/joshuagilman/Documents/code/data/new_data_outfiles/VWC_daily_new.csv', 'w')
    #outfile1 = open(f'{DATA_DIRECTORY}/new_data_outfiles/VWC_daily_new.csv', 'w')

object_list = []

## loop through the look-up file
for row in lookup_file:
    row = row.strip()
    logger_fields = row.split(",")

    ## skip the header line of the lookup file
    if logger_fields[0] == "\ufeffdatalogger ID":
        continue
    else:

        ## gets each datalogger file from the directory containing the data
        logger_number = logger_fields[0]

        # directory where the data will be on local computer
        # root_dir = f'{DATA_DIRECTORY}/new_data'
        root_dir = '/Users/joshuagilman/Documents/code/data/raw_sensor_data'
        
        ## loops through all directories in directory that contains 
        ## the data (2018 sensor_data folder)
        for subdir, dirs, files in os.walk(root_dir):
            for file_name in files:
                # print(subdir)
                if file_name == ".DS_Store":
                    continue
            
                ## this tests whether or not we have the file name that matches the file in look-up table 
                if (Title_To_LoggerNumber(file_name)) == logger_number:
                    ## read excel reads the raw.csv
                    wb = xlrd.open_workbook('{0}/{1}'.format(subdir,file_name)) 
                    sh = wb.sheet_by_index(0)

                    ## ARTIFACT
                    ## necessary for creating file date list (not used as of 9/3/2018)
                    for object in object_list:
                        object.test_bool = True

                    index = 0
                    while True:
                        try:
                            fields = sh.row_values(index)

                            ## reads fields[0] as a date
                            if index > 2:
                                fields[0] = xlrd.xldate_as_datetime(fields[0], wb.datemode)
                            
                            ## creates a dictionary and puts the top line raw data file in as value [list], using "header_one" as key
                            if fields[0] == "{}".format(logger_number):
                                header_dict = {}
                                header_dict["header_one"] = fields
                            
                            ## sets value of header_dict equal to second header line [list], using header_two as key
                            elif fields[1] == "GS3 Moisture/Temp/EC" or fields[1] == "GS1 Soil and Media Moisture" or fields[1] == "5TM Moisture/Temp" or fields[1] == "5TE Moisture/Temp/EC" or fields[1] == "MPS-6 Water Potential/Temp" or fields[1] == "MPS-2 Water Potential/Temp" or fields[1] == "EC-TM Moisture/Temp" or fields[1] == "ECRN-50 Precipitation":
                                header_dict["header_two"] = fields
                                # file_end_date = File_End_Date(file_name)
                            
                            ## sets value of header_dict equal to third header line [list], using header_three as key
                            ## determines the columns of interest in the raw data sheet
                            ## creates an object for each logger.port of interest if one has not already been created
                            elif fields[0] == "Measurement Time":
                    
                                header_dict["header_three"] = fields
                                header_two_list = Header_Two_List(header_dict, user_measurement)
                                header_three_list = Header_Three_List(header_dict, user_measurement)
                                column_list = Create_Shared_Values_List(header_two_list, header_three_list)
                                for value in column_list:
                                    object_port = Create_Object_Port(header_dict, value)
                                    object_logger = logger_number
                                    object_title = (logger_number + '.' + object_port)
                                    object_column = int(value)
                                    object_sensor = header_dict["header_two"][value]
                                    object_sensor_units = header_dict["header_three"][value]
                                    ## All of the below information comes from the lookup tables.
                                    object_mammal = logger_fields[6]
                                    object_burn = logger_fields[7]
                                    object_block = logger_fields[8] 
                                    object_prop_pressure = logger_fields[14]
                                    object_precipitation = logger_fields[int(object_port)]
                                    object_sensor_number = logger_fields[(int(object_port) + 8)]

                                    object_sensor_measurement = None
                                    if object_sensor == "GS3 Moisture/Temp/EC" or object_sensor == "GS1 Soil and Media Moisture" or object_sensor == "5TM Moisture/Temp" or object_sensor == "5TE Moisture/Temp/EC" or object_sensor == "EC-TM Moisture/Temp":
                                            object_sensor_measurement = "VWC"
                                    if object_sensor == "MPS-6 Water Potential/Temp" or object_sensor == "MPS-2 Water Potential/Temp":
                                            object_sensor_measurement = "WP"
                                                            
                                    ## this piece will prevent the control treatment loggers from being included
                                    if object_precipitation == "NA":
                                        break
                                    else:
                                        pass

                                    
                                    ## creates one object for each data logger port (depending on user measurement preference)
                                    if(Object_Not_Created(object_list, object_logger, object_title, object_column, object_sensor, object_mammal, object_burn, object_block, object_precipitation)):
                                        logger_object = Logger_Port(object_port, object_logger, object_title, object_column, object_sensor, object_sensor_units, object_mammal, object_burn,
                                         object_block, object_precipitation, object_sensor_number, object_sensor_measurement, object_prop_pressure)
                                        object_list.append(logger_object)
                                        
                                    else:
                                        pass

                            ## loops through non-header lines of the raw data file and adds them to object.dict
                            else:
                                for object in object_list:
                                    for value in column_list:
                                        if object.column == value and object.logger == logger_number:
                                            if object.sensor == "GS3 Moisture/Temp/EC": 
                                                column_value = fields[object.column]
                                                if column_value > 1:
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                                    # value_to_append = GSthree_function(float(column_value))
                                            elif object.sensor == "GS1 Soil and Media Moisture":
                                                column_value = fields[object.column]
                                                if column_value > 1:
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                                    # value_to_append = GSone_function(float(column_value))
                                            elif object.sensor == "5TM Moisture/Temp": 
                                                column_value = fields[object.column]
                                                if column_value > 1:
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                                    # value_to_append = fiveTM_function(float(column_value))
                                            elif object.sensor == "5TE Moisture/Temp/EC":
                                                column_value = fields[object.column]
                                                if column_value > 1:
                                                    # print(column_value)
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                            elif object.sensor == "EC-TM Moisture/Temp":
                                                column_value = fields[object.column]
                                                if column_value == "#N/A": 
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                            elif object.sensor == "ECRN-50 Precipitation":
                                                column_value = fields[object.column]
                                                if column_value == "#N/A": 
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                            elif object.sensor == "MPS-6 Water Potential/Temp" or object.sensor == "MPS-2 Water Potential/Temp":
                                                column_value = fields[object.column]
                                                if float(column_value) > 0:
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)
                                            else:
                                                column_value = fields[object.column]
                                                if column_value == "#N/A":
                                                    continue
                                                else:
                                                    value_to_append = float(column_value)

                                            
                                            ## prevents measurements not taken on the hour from being included in object.dict
                                            if fields[0].minute == 0:

                                                object.dict[fields[0].year][fields[0].month][fields[0].day][fields[0].hour] = (str(value_to_append))
                                                object.dict1[fields[0].year][fields[0].month][fields[0].day].append(str(value_to_append))
                                                object.dict3[fields[0].year][fields[0].month].append(str(value_to_append))

                                                # object.dict[fields[0].year][fields[0].month][fields[0].day].append(str(value_to_append))
                                                        
                            index += 1
                        except:
                            break
                        # except Exception as e:
                        #     raise e


CETE_dict = Create_CETE_Date_Dict()
BRTE_dict = Create_BRTE_Date_Dict()

Outwrite_Header_Line(user_measurement)
Outwrite_Daily_Continuous(object_list, user_date_list1, user_measurement, CETE_dict, BRTE_dict)




# Two possible ways to get errors:
# 1.) the user date list queries dates that are outside the range of when data was gathered at the site
# to solve: continue when a date is not present in the dictionary
# 2.) the user date list queries dates that are inside the range of dates when data was gathered
# but for some reason the data does not exist:
# to solve: continue when a date is not present in the dictionary





