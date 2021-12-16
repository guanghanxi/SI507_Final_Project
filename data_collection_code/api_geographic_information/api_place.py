import json
import requests
import pandas as pd
import numpy as np

param={'get':"NAME,POP,DENSITY", 'for':{'state':'*'}, 'key':'44cd8d30dab5840e9faa58797c2d61e23033b4f7'}
state_pop = requests.get('https://api.census.gov/data/2019/pep/population', param).json()

param={'get':"NAME,POP,DENSITY,STATE", 'for':{'COUNTY':'*'}, 'key':'44cd8d30dab5840e9faa58797c2d61e23033b4f7'}
county_pop = requests.get('https://api.census.gov/data/2019/pep/population', param).json()

param={'get':"NAME,B19013_001E", 'for':{'state':'*'}, 'key':'44cd8d30dab5840e9faa58797c2d61e23033b4f7'}
state_income = requests.get('https://api.census.gov/data/2019/acs/acs5', param).json()

param={'get':"NAME,B19013_001E,STATE", 'for':{'county':'*'}, 'key':'44cd8d30dab5840e9faa58797c2d61e23033b4f7'}
county_income = requests.get('https://api.census.gov/data/2019/acs/acs5', param).json()

state_pop_df = pd.DataFrame(state_pop[1:], columns = state_pop[0])
state_income_df = pd.DataFrame(state_income[1:], columns = state_income[0])
state_pop_df.join(state_income_df[['state','B19013_001E']].set_index('state'), on = 'state').to_json('state_data.json')

county_pop_df = pd.DataFrame(county_pop[1:], columns = county_pop[0])
county_income_df = pd.DataFrame(county_income[1:], columns = county_income[0])
county_pop_df.join(county_income_df[['county','STATE', 'B19013_001E']].set_index(['county','STATE']), on = ['county', 'STATE']).to_json('county_data.json')