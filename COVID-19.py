#!/usr/bin/python

'''
COVID-19.py: A script for assessing exposure to sites visited by confirmed COVID-19 cases in Melbourne during visit of fixed duration
A. J. McCulloch, January 2021
'''

####################################################################################################
# Import modules
####################################################################################################

import requests # Requests for retrieving html content
import pandas as pd # Pandas for importing, sorting and manipulating data
import datetime # datetime for date structures
from bs4 import BeautifulSoup # BeautifulSoup for parsing HTML

####################################################################################################
# Define functions
####################################################################################################

# function for matching dates from dataframe to list of dates
# Converting the poorly formatted strings to datatime objects was not worth it
def datematch(x):
    t = x.split(' ') # split the time and date string

    for i in t:
        if '/' in i: # take only the dates
            # This is not robust!
            if ',' in i: # fix formatting
                i = i.replace(',', '')
            elif '-' in i: # fix formatting
                i = i.replace('-', '')
            else:
                pass

            y = i.split('/')[-1] # the year

            # correct the year format depending on length
            if len(y) == 2:
                d = datetime.datetime.strptime(i, '%d/%m/%y')
            elif len(y) == 4:
                d = datetime.datetime.strptime(i, '%d/%m/%Y')
            else:
                if i.split('/')[1] == 12: # If the year is poorly formatted, check the month
                    d = datetime.datetime.strptime(i.split('/')[0]+'/12/20', '%d/%m/%y')
                else:
                    d = datetime.datetime.strptime(i.split('/')[0]+'/'+i.split('/')[1]+'/21', '%d/%m/%y')

            if d in dates_dt: # check if the dates match the relevant dates
                return True
            else:
                return False
        else:
            return False

####################################################################################################
####################################################################################################
# Program starts here
####################################################################################################
####################################################################################################

url = 'https://www.dhhs.vic.gov.au/case-locations-and-outbreaks' # site hosting the data
dates = ['01/01/21', '02/01/21', '03/01/21'] # dates of potential exposure

html = requests.get(url).content # get the HTML content
soup = BeautifulSoup(html, features='lxml') # parse the HTML
udt = [s for s in [x.text for x in soup.find_all('strong')] if '/' in s][0] # find the update time
df_list = pd.read_html(html) # read the tables from the html content
dates_dt = [datetime.datetime.strptime(d, '%d/%m/%y') for d in dates] # create datetime objects from dates

# Public exposure sites
df_HR = df_list[0] # High-risk sites
df_MR = df_list[1] # Medium-risk sites
df_LR = df_list[2] # Low-risk sites

df_HR['Risk'] = 'High'
df_MR['Risk'] = 'Medium'
df_LR['Risk'] = 'Low'

df = pd.concat([df_HR, df_MR, df_LR],ignore_index=True) # concatenate the dataframes

df_ = df[df['Exposure period'].map(datematch)] # extract only the exposures which are relevant

# print some metadata
print('\nProgram executed at {}'.format(datetime.datetime.now().strftime("%d/%m/%y %I:%M%p")))
print('DHHS website updated {}'.format(udt.upper()))

print('\n#############################################'.format(udt.upper()))
print('########## COVID-19 exposure sites ##########'.format(udt.upper()))
print('########## {} - {} ##########'.format(min(dates_dt).strftime("%d/%m/%Y"), max(dates_dt).strftime("%d/%m/%Y")))
print('#############################################'.format(udt.upper()))

# print the cases
for index, row in df_.iterrows():
    print("\nA {}-risk exposure in {} occured on {}.\nThe location was at/on {}.\nExposure note: {}.".format(row['Risk'].lower(), row['Location'], row['Exposure period'], row['Site'], row['Notes']))
