import requests
from bs4 import BeautifulSoup
import json
import re
import numpy as np
import pandas as pd
import secrets

BESTBUY_URL = 'https://stores.bestbuy.com/'
APPLE_URL = 'https://www.apple.com'
APPLE_LIST_PATH = '/retail/storelist/'

STATE_DICT = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District Of Columbia",
    "FM": "Federated States Of Micronesia",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "MP": "Northern Mariana Islands",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PW": "Palau",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VI": "Virgin Islands",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

ZIP_API = 'https://www.zipcodeapi.com/rest/{api_key}/info.json/{code}/degrees'

#  functions to get apple store information

def get_bestbuy_store(store_href):
    store_response =  requests.get(BESTBUY_URL + store_href)
    store_soup = BeautifulSoup(store_response.text, 'html.parser')
    store_name = store_soup.find('span', class_='LocationName-geo')
    city = store_soup.find('meta', attrs={'itemprop':'addressLocality'}).get('content')
    address = store_soup.find('meta', attrs={'itemprop':'streetAddress'}).get('content')
    post_code = store_soup.find('span', attrs={'class':'c-address-postal-code'}).text
    state = store_href.split('/')[0]
    code = store_href.split('-')[-1].split('.')[0]
    return [{'code': code, 'state': STATE_DICT[state.upper()], 'state_abbr': state, 'city': city, 'address': address, 'post_code': post_code, 'type': 'Best Buy' }]

def get_bestbuy_storelist(city_href):
    city_response =  requests.get(BESTBUY_URL + city_href)
    city_soup = BeautifulSoup(city_response.text, 'html.parser')
    storehref_list = city_soup.find_all('a', attrs={'class':'Link Teaser-titleLink'})
    href_list = []
    store_list = []
    for store_href in storehref_list:
        hrefsplit = store_href['href'].split('/')
        result = hrefsplit[1]+'/'+hrefsplit[2]+'/'+hrefsplit[3]
        if result.endswith('.html'):
            href_list.append(result)
    for storehref in href_list:
        store_list += get_bestbuy_store(storehref)
    return store_list


def get_bestbuy_citylist(state_href):
    state_response =  requests.get(BESTBUY_URL + state_href)
    state_soup = BeautifulSoup(state_response.text, 'html.parser')
    citya_list = state_soup.find_all('a', attrs={'class':'c-directory-list-content-item-link'})
    store_list = []
    for city_a in citya_list:
        city_href = city_a['href']
        level = city_href.count('/')
        if level == 1:
            store_list += get_bestbuy_storelist(city_href)
        elif level == 2:
            store_list += get_bestbuy_store(city_href)
    return store_list

def get_bestbuy():
    bestbuy_response =  requests.get(BESTBUY_URL)
    bestbuy_soup = BeautifulSoup(bestbuy_response.text, 'html.parser')
    statea_list = bestbuy_soup.find_all('a', attrs={'class':'c-directory-list-content-item-link'})
    store_list = []
    for state_a in statea_list:
        state_href = state_a['href']
        level = state_href.count('/')
        if level == 0:
            store_list += get_bestbuy_citylist(state_href)
        elif level == 1:
            store_list += get_bestbuy_storelist(state_href)
        elif level == 2:
            store_list += get_bestbuy_store(state_href)
    return store_list  

#  functions to get apple store information

def get_apple_store(store_href, city):
    apple_store_response =  requests.get(APPLE_URL + store_href)
    apple_store_soup = BeautifulSoup(apple_store_response.text, 'html.parser')
    address_list = apple_store_soup.find('address').text.split(',')
    state = address_list[1].split(' ')[1]
    post_code = address_list[1].split(' ')[2]
    code = store_href.split('/')[2]
    return {'code': code, 'state': STATE_DICT[state.upper()], 'state_abbr': state, 'city': city, 'address': address_list[0].replace(city, ''), 'post_code': post_code, 'type': 'Apple' }

def get_apple():
    apple_response =  requests.get(APPLE_URL + APPLE_LIST_PATH)
    apple_soup = BeautifulSoup(apple_response.text, 'html.parser')
    apple_list = apple_soup.find_all('div', attrs={'class':'address-lines'})
    apple = []
    for element in apple_list:
        address = element.find('span').text
        apple.append(get_apple_store(element.find('a')['href'], element.find('span').text.split(',')[0]))
    return apple

# Use the ZIP CODE API to get county and coordinates

def add_information(store_list): 
    zip_code = pd.read_csv('uszips.csv')
    zipcode = zip_code['zip'].values
    cities = pd.read_csv('uscities.csv')
    for element in store_list:
        postcode = int(element['post_code'].split('(')[0].split('-')[0])
        if postcode in zipcode:
            element['coordinate'] = tuple(zip_code[zip_code['zip']== postcode][['lat', 'lng']].iloc[0])
            element['county_fips'] = str(zip_code[zip_code['zip']== postcode]['county_fips'].iloc[0]).zfill(5)
        else:
            element['county_fips'] = str(cities[cities['city'] == element['city']]['county_fips'].iloc[0]).zfill(5)
            zip_data = requests.get(ZIP_API.format( api_key = secrets.zip_api_key ,code = postcode)).json()
            element['coordinate'] = (zip_data['lat'], zip_data['lng'])
    return store_list

if __name__ == '__main__':
    store_path = 'store_result.json' 
    store_list = add_information(get_bestbuy() + get_apple())
    json_file = open(store_path, mode='w')
    json.dump(store_list, json_file) 

