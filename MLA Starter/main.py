from typing import OrderedDict
from xml.etree.ElementPath import find
import pandas as pd
import pprint
from collections import OrderedDict


# Treat the case where there exists employees who aren't in the ilc
# Find who is missing and create the accurate data
def edge_cases(data, employees_info_data, country):
    new_serial_list= []
    ilc_serial_list= data['ibm_serial'].tolist()
    # Iterate through excel sheet to gather everyone's serial number
    filtered_employees= employees_info_data.loc[(employees_info_data['country_code']==country)] 

    for index, row in filtered_employees.iterrows():
        serial = row['ibm_serial']
        if serial not in ilc_serial_list:
            new_serial_list.append(serial)
    return(new_serial_list)

# Create dictionary result for edge cases (serials not in ilc)
def edge_case_dictionary(serial_list, employees_info_data, days):
    dict={}
    for serial in serial_list:
        edge_dict={}
        edge_dict['ibm_serial']= serial
        employee_data= employees_info_data.loc[employees_info_data['ibm_serial']==serial]
        first_name= employee_data.iloc[0]['first_name']
        last_name= employee_data.iloc[0]['last_name']
        full_name= (first_name+last_name)
        edge_dict['name']= full_name
        
        # Create dictionary including the hours and hours missing data for each day
        inner_dict={}
        for day in days:
            inner_dict[day]={
                'hours': 0.0,
                'is-missing': True
                }
        edge_dict['claimed_hours']= inner_dict
        dict[serial]=edge_dict
    return(dict, serial_list)


# Filter the data according to the country code and 
# week of interest
def filter_ilc(country, week, data):
    #new_data= data.query('country_code == @country and week_ending_date== @week')
    new_ilc_data= data.loc[(data['country_code']==country) & (data['week_ending_date']==week)] 
    return(new_ilc_data)

# Create a dataframe for each serial number 
# Then create a dictionary of total hours for the multiple entries of each serial number
def condense_hours(new_ilc_data, days):
    serial_list= new_ilc_data['ibm_serial'].tolist()
    serial_list = list(dict.fromkeys(serial_list))
    full_hours_dict= {}

    for x in serial_list:
        # filter data frame by serial number
        dic={}
        new_data= new_ilc_data.loc[(new_ilc_data['ibm_serial']== x)]
        for day in days:
            total= new_data.loc[:, day].sum()
            dic[f'{day}_total']= total
        full_hours_dict[x]= dic
    return(full_hours_dict)
#condense_hours()


# Find who is missing and save the hours for those missing
def find_missing_hours(full_hours_dict):
    serial_list=[]
    hours_dic={}
    for index in full_hours_dict: 
        hours=full_hours_dict[index]
        days_index=['mon_total', 'tue_total', 'wed_total', 'thu_total', 'fri_total']
        for day_index in days_index:
            if hours[day_index] == 0.0:
                serial_list.append(index)
                break    
    for i in serial_list:
        hours_dic[i]= full_hours_dict[i]
    return serial_list, hours_dic
#find_missing_hours()


# Create Claimed Hours Dictionary
# Make key the serial Number
def claimed_hours(serial_list, hours_dic, days):
    claimed_hours_dict={}
    week_dict={}

    #Find and create dictionary of claimed hours components for each day
    n_dict={}
    for i in serial_list:
        for day in days:
            hours = hours_dic[i][f'{day}_total']
            is_missing= False
            if hours== 0.0:
                is_missing= True
            n_dict[day]={
                'hours': hours,
                'is-missing': is_missing
            }
            week_dict[day]= n_dict[day]

        claimed_hours_dict[i]={}
        claimed_hours_dict[i]['claimed-hours']= week_dict
    return(claimed_hours_dict)
#claimed_hours()

# Grab the first and last names relating to the ibm serial number
# Make sure to convert serial_n to string before submitting to this function
def names(serial_list, employees_info_data):
    names_dict={}
    for i in serial_list:
        employee_data= employees_info_data.loc[employees_info_data['ibm_serial']== i] 
        first_name= employee_data.iloc[0]['first_name']
        last_name= employee_data.iloc[0]['last_name']
        full_name= (first_name+last_name)
        names_dict[i]={}
        names_dict[i]['name']=full_name
    return(names_dict)
#names()


# Create a Dataframe with all the necessary information 
def final_dataframe(serial_list, edge_dict, edge_serial_list, names_dict, claimed_hours_dict):
    final_df={}
    for i in serial_list:
        final_df[i]={}
        final_df[i]['name']= names_dict[i]['name']
        final_df[i]['ibm-serial']= i
        final_df[i]['claimed-hours']= claimed_hours_dict[i]['claimed-hours']
    for index in serial_list:
        pprint.pprint(final_df[index]) 
    for index in edge_serial_list:
        pprint.pprint(edge_dict[index]) 
   

def main():
    data = pd.read_csv('ilc.csv')
    employees_info_data= pd.read_excel('employees.xlsx')
    country= 897
    week='2022-09-30'
    days= ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri']


    new_serial_list= edge_cases(data, employees_info_data, country)
    edge_dict, edge_serial_list= edge_case_dictionary(new_serial_list, employees_info_data, days)
    new_ilc_data= filter_ilc(country, week, data)
    full_hours_dict= condense_hours(new_ilc_data, days)
    serial_list, hours_dic=find_missing_hours(full_hours_dict )
    claimed_hours_dict= claimed_hours(serial_list, hours_dic, days)
    names_dict= names(serial_list, employees_info_data)

    final_dataframe(serial_list, edge_dict, edge_serial_list, names_dict, claimed_hours_dict)

if __name__ == "__main__":
    main()
