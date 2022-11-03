import csv
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
def edge_case_dictionary(serial_list, employees_info_data):
    dict={}
    for serial in serial_list:
        edge_dict={}
        edge_dict['ibm_serial']= serial

        employee_data= employees_info_data.loc[employees_info_data['ibm_serial']==serial]
        first_name= employee_data.iloc[0]['first_name']
        last_name= employee_data.iloc[0]['last_name']
        full_name= (first_name+last_name)
        edge_dict['name']= full_name

        edge_dict['claimed_hours']={
            'sat':{
                'hours': 0.0,
                'is-missing': True
            },
            'sun':{
                'hours': 0.0,
                'is-missing': True
            },
            'mon':{
                'hours': 0.0,
                'is-missing': True
            },
            'tue':{
                'hours': 0.0,
                'is-missing': True
            },
            'wed':{
                'hours': 0.0,
                'is-missing': True
            },
            'thu':{
                'hours': 0.0,
                'is-missing': True
            },
            'fri':{
                'hours': 0.0,
                'is-missing': True
            }
        }
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
def condense_hours(new_ilc_data):
    serial_list= new_ilc_data['ibm_serial'].tolist()
    serial_list = list(dict.fromkeys(serial_list))
    full_hours_dict= {}

    for i in range(len(serial_list)):
        # filter data frame by serial number 
        x= serial_list[i]
        new_data= new_ilc_data.loc[(new_ilc_data['ibm_serial']== x)]

        sat_total = new_data.loc[:, 'sat'].sum()
        sun_total = new_data.loc[:, 'sun'].sum()
        mon_total = new_data.loc[:, 'mon'].sum()
        tue_total = new_data.loc[:, 'tue'].sum()
        wed_total = new_data.loc[:, 'wed'].sum()
        thu_total = new_data.loc[:, 'thu'].sum()
        fri_total = new_data.loc[:, 'fri'].sum()

        dic= {'sat_total': sat_total, 'sun_total': sun_total, 'mon_total': mon_total, 'tue_total': tue_total, 'wed_total': wed_total, 'thu_total': thu_total, 'fri_total': fri_total,}
        full_hours_dict[x]= dic
    return(full_hours_dict)
#condense_hours()


# Find who is missing and save the hours for those missing
def find_missing_hours(full_hours_dict):
    serial_list=[]
    hours_dic={}
    for index in full_hours_dict: 
        hours=full_hours_dict[index]
        if hours['mon_total']==0.0 or hours['tue_total']==0.0 or hours['wed_total'] ==0.0 or hours['thu_total'] ==0.0 or hours['fri_total'] == 0.0:
            serial_list.append(index)
    for i in serial_list:
        hours_dic[i]= full_hours_dict[i]
    return serial_list, hours_dic
#find_missing_hours()


# Create Claimed Hours Dictionary
# Make key the serial Number
def claimed_hours(serial_list, hours_dic):
    claimed_hours_dict={}
    for i in serial_list:
        sat_hours= hours_dic[i]['sat_total']
        if sat_hours ==0.0:
            sat_is_missing= True
        else:
            sat_is_missing= False

        sun_hours= hours_dic[i]['sun_total']
        if sun_hours ==0.0:
            sun_is_missing= True
        else:
            sun_is_missing= False
        
        mon_hours= hours_dic[i]['mon_total']
        if mon_hours ==0.0:
            mon_is_missing= True
        else:
            mon_is_missing= False

        tue_hours= hours_dic[i]['tue_total']
        if tue_hours ==0.0:
            tue_is_missing= True
        else:
            tue_is_missing= False
        
        wed_hours= hours_dic[i]['wed_total']
        if wed_hours ==0.0:
            wed_is_missing= True
        else:
            wed_is_missing= False
        
        thu_hours= hours_dic[i]['thu_total']
        if thu_hours ==0.0:
            thu_is_missing= True
        else:
            thu_is_missing= False

        fri_hours= hours_dic[i]['fri_total']
        if fri_hours ==0.0:
            fri_is_missing= True
        else:
            fri_is_missing= False
        
        week_dict={ 
            'sat':{'hours':sat_hours, 'is-missing':sat_is_missing},
            'sun':{'hours':sun_hours, 'is-missing':sun_is_missing},
            'mon':{'hours':mon_hours, 'is-missing':mon_is_missing},
            'tue':{'hours':tue_hours, 'is-missing':tue_is_missing},
            'wed':{'hours':wed_hours, 'is-missing':wed_is_missing},
            'thu':{'hours':thu_hours, 'is-missing':thu_is_missing},
            'fri':{'hours':fri_hours, 'is-missing':fri_is_missing}
        }
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

    new_serial_list= edge_cases(data, employees_info_data, country)
    edge_dict, edge_serial_list= edge_case_dictionary(new_serial_list, employees_info_data)
    new_ilc_data= filter_ilc(country, week, data)
    full_hours_dict= condense_hours(new_ilc_data)
    serial_list, hours_dic=find_missing_hours(full_hours_dict )
    claimed_hours_dict= claimed_hours(serial_list, hours_dic)
    names_dict= names(serial_list, employees_info_data)

    final_dataframe(serial_list, edge_dict, edge_serial_list, names_dict, claimed_hours_dict)

if __name__ == "__main__":
    main()
