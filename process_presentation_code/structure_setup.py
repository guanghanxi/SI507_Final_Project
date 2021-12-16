import numpy as np
import pandas as pd
import json

def connect_county_state(county_dict, state_dict):
    '''
    Connect County Element with State Element
    '''
    for state in state_dict.values():
        state['county_list']=[]
    for county in county_dict.values():
        state_dict[county['state']]['county_list'].append(county['state'] + county['county'])

def connect_county_store(county_dict, store_dict):
    '''
    Connect store elements with the County Element
    '''
    for county in county_dict.values():
        county['bestbuy_list']=[]
        county['apple_list']=[]
    for key, value in store_dict.items():
        if value['type'] == 'Best Buy':
            county_dict[value['county_fips']]['bestbuy_list'].append(key)
        else:
            county_dict[value['county_fips']]['apple_list'].append(key)
    for v in county_dict.values():
        for element in v['bestbuy_list']:
            bestbuy_list = v['bestbuy_list'].copy()
            store_dict[element]['bestbuy_nrb'] = bestbuy_list.remove(element)
        for element in v['apple_list']:
            apple_list = v['apple_list'].copy()
            store_dict[element]['apple_nrb'] = apple_list.remove(element)


def data_process():
    '''
    Read data from .json file and then process them
    '''
    with open('database/store_result.json', 'r') as json_file:
        store_list = json.load(json_file)
    county_df = pd.read_json("database/county_data.json").sort_values(by=['NAME'])
    state_df = pd.read_json("database/state_data.json").sort_values(by=['NAME'])
    county_df['state'] = county_df['state'].apply(lambda x: str(x).zfill(2))
    county_df['county'] = county_df['county'].apply(lambda x: str(x).zfill(3))
    county_df['fips'] = county_df.apply(lambda x: x['state'] + x['county'], axis = 1)
    state_df['state'] = state_df['state'].apply(lambda x: str(x).zfill(2))
    state_dict = dict(zip(state_df['state'], state_df.to_dict('records')))
    county_dict = dict(zip(county_df.apply(lambda x: x['state'] + x['county'], axis = 1), county_df.to_dict('records')))
    store_dict = dict(zip(list(range(len(store_list))),store_list)) # Use automatically increasing digital code as key for stores
    return [state_dict, county_dict, store_dict]

if __name__ == '__main__':
    dict_list = data_process()
    connect_county_state(dict_list[1], dict_list[0])
    connect_county_store(dict_list[1], dict_list[2])
    json_file_path = './data_structure/trees.json'
    json_file = open(json_file_path, mode='w')
    json.dump(dict_list, json_file, indent=4) 
