import json

with open('data_structure/trees.json', 'r') as json_file:
    dict_list = json.load(json_file)

'''
Load data structure to json and then read make type of some keys from int to str
Then the code should change them back to int 
'''
new_store_dict = {int(k): v for k,v in dict_list[2].items()}
dict_list[2] = new_store_dict