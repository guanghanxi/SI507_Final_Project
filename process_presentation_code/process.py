import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go 
import matplotlib.pyplot as plt
import seaborn as sns
from read_tree import dict_list

# The dictionary of the State Name and Abbreviation  
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

def correct_input(num):
    '''
    The function to modify users' inputs in command line presentation
    '''
    while True:
        ans = input("Please Input the Number Corresponding to the Choice, or 'e' to Go Back to Previous: ")
        if ans.isdigit():
            ans = int(ans) 
            if ans>0 and ans<=num:
                break
        elif ans.lower() == 'e':
            break
        print("Sorry, invalid input, please try again.")
    return ans

def print_address(store_data, num):
    '''
    Print Address of Store
    '''
    print(str(num) + ' - ' + store_data['address'] + ', ' + store_data['city'] + ', ' + store_data['state'] + ' ' + store_data['post_code'])
    return num+1

# The following function is used to find stores in a county 

def show_information(dict_list):
    while True:
        print("Please Choose the State You Want to Search")
        i=1
        for state in dict_list[0].values():
            print(str(i) + ' - ' + state['NAME'], end = '\t')
            i += 1
            if i%4 == 0:
                print()
        print('\n')
        index_selected = correct_input(len(dict_list[0].values()))
        if index_selected == 'e':
            break
        state_selected = list(dict_list[0].values())[index_selected-1] # Get the information dictionary of the chosen state
        print("Please Choose the County You Want to Search")
        j=1
        for county in state_selected['county_list']:
            print(str(j) + ' - ' + dict_list[1][county]['NAME'], end = '\t')
            j += 1
            if j%3 == 0:
                print()
        print('\n')
        while True:
            index_selected = correct_input(len(state_selected['county_list']))
            if index_selected == 'e':
                break
            county_selected = dict_list[1][state_selected['county_list'][index_selected-1]] # Get the information dictionary of the chosen county
            k=1
            print("The Best Buy Stores and Apple Stores in " + county_selected['NAME'])
            print("Best Buy Store List: ")
            for store in county_selected['bestbuy_list']:
                k = print_address(dict_list[2][store],k)
            print("Apple Store List: ")
            for store in county_selected['apple_list']:
                k = print_address(dict_list[2][store],k)
    
# The following two functions are used to show the percent of different kinds of Counties in the US                  

def get_percent(county_dict):
    '''
    Generate data to draw the pie chart
    '''
    percent_list = [0,0,0,0]
    length = 0
    for county in county_dict.values():
        length += 1
        if len(county['bestbuy_list']) != 0 and len(county['apple_list']) !=0:
            percent_list[0] += 1
        elif len(county['bestbuy_list']) != 0:
            percent_list[1] += 1
        elif len(county['apple_list']) !=0:
            percent_list[2] += 1
        else:
            percent_list[3] += 1
    labels = ['Counties with Both Best Buy and Apple Stores', 'Counties with Only Best Buy Stores', 'Counties with Only Apple Stores', 'Counties with neither Best Buy nor Apple Stores']
    return pd.DataFrame({'group': labels, 'percent':[x/length for x in percent_list]})

def draw_pie(percent_df):
    '''
    Draw the pie chart
    '''
    wedges, texts, autotexts = plt.pie(percent_df['percent'], 
        autopct='%.2f%%', 
        radius = 1.1, 
        counterclock = False)
    plt.legend(wedges, percent_df['group'], title="US Counties")
    plt.setp(autotexts, size=8, weight="bold")
    plt.title('US County Distribution') 
    plt.show()

# The following three functions are used to show influence of population, population density and Median Home Income on Best Buy's or Apple's decision 

def data_store(county_dict):
    '''
    Generate the dataframe to draw the distribution of US counties' population, population density and Median Home Income
    '''
    county_df = pd.DataFrame(list(county_dict.values()))
    county_df.rename(columns={'B19013_001E': 'Median Home Income'}, inplace = True)
    county_df['With_Best_Buy'] = county_df['bestbuy_list'].apply(lambda x: 'At Least One Best Buy Store' if len(x)==0 else 'No Best Buy Store')
    county_df['With_Apple'] = county_df['apple_list'].apply(lambda x: 'At Least One Apple Store' if len(x)==0 else 'No Apple Store')
    return county_df


def show_trend(county_df, store_type):
    '''
    Function to show influence of population, population density and Median Home Income on Best Buy's or Apple's decision 
    '''
    if store_type == 1:
        store_choice = 'With_Best_Buy'
    else:
        store_choice = 'With_Apple'
    store_df = county_df[['POP', 'DENSITY', 'Median Home Income', store_choice]]
    fig= plt.figure()
    axes = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223) ]
    fig.set_figheight(16)
    fig.set_figwidth(20)
    fig.suptitle("Distribution of US Counties' Population, Population Density and Median Home Income")
    sns.kdeplot(data = store_df, x='POP', hue = store_choice, ax=axes[0], shade='Ture', log_scale=(True, False))
    axes[0].set_xlabel('Population')
    sns.kdeplot(data = store_df, x='DENSITY', hue = store_choice, ax=axes[1], shade='Ture', log_scale=(True, False))
    axes[1].set_xlabel('Population Density')
    sns.kdeplot(data = store_df, x='Median Home Income', hue = store_choice, ax=axes[2], shade='Ture', log_scale=(True, False))
    axes[2].set_xlabel('Median Home Income ($)')
    plt.subplots_adjust(hspace=0.2)
    plt.show()

# The following two functions are used to show influence of population, population density and Median Home Income on Best Buy's or Apple's decision
    
def save_gradientmap(dictlist):
    for state in dictlist[0].values():
        state['Best_Buy_Num'] = 0
        state['Apple_Num'] = 0
        for county in state['county_list']:
            state['Best_Buy_Num'] += len(dictlist[1][county]['bestbuy_list'])
            state['Apple_Num'] += len(dictlist[1][county]['apple_list'])
        state['Pop_Best_Buy'] = state['POP']/(state['Best_Buy_Num'])
        state['Pop_Apple'] = state['POP']/(state['Apple_Num']+0.5)
    state_df = pd.DataFrame(list(dictlist[0].values()))
    abr_dict = {v:k for k,v in STATE_DICT.items()}
    state_df['ABR'] = state_df['NAME'].apply(lambda x:abr_dict[x.title()])
    fig_bestbuy = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Best_Buy_Num'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Number of Best Buy Stores")) 
    fig_bestbuy.update_layout( title_text = 'Number of Best Buy Stores in USA States', geo_scope='usa')
    fig_bestbuy.write_image(file = 'picture/bestbuy.png', format='png')
    fig_apple = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Apple'].astype(int), 
            locationmode = 'USA-states', colorscale = 'Greys', colorbar_title = "Number of Apple Stores")) 
    fig_apple.update_layout( title_text = 'Number of Apple Stores in USA States', geo_scope='usa')
    fig_apple.write_image(file = 'picture/apple.png', format='png')
    fig_density_bestbuy = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Best_Buy'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Population / Num of Best Buy")) 
    fig_density_bestbuy.update_layout( title_text = 'Rate Between Population and Number of Best Buy Stores in USA States', geo_scope='usa')
    fig_density_bestbuy.write_image(file = 'picture/density_bestbuy.png', format='png')
    fig_density_bestbuy = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Apple'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Population / Num of Apple")) 
    fig_density_bestbuy.update_layout( title_text = 'Rate Between Population and Number of Apple Stores in USA States', geo_scope='usa')
    fig_density_bestbuy.write_image(file = 'picture/density_apple.png', format='png')
    return state_df

def show_gradientmap(present_type):
    '''
    Show the Data Visualization in Command Line Presentation
    '''
    img_path = ['picture/bestbuy.png', 'picture/apple.png', 'picture/density_bestbuy.png', 'picture/density_apple.png']
    x = plt.imread(img_path[present_type])
    plt.imshow(x)
    plt.show()

# The following function is used to perform the presentation in command line.

def comandline_show(dictlist, percentdf, countydf):
    while True:
        print("Please Choose the Presentation You Want to See: ")
        print("1 - Find Best Buy and Apple Stores in a County")
        print("2 - How Much Counties Have Both Apple and Best Buy")
        print("3 - Where Does Best Buy Tend to Open Stores")
        print("4 - Where Does Apple Tend to Open Stores")
        print("5 - Overall Distribution of Best Buy Stores and Apple Stores")
        ans = correct_input(5)
        if ans == 1:
            show_information(dictlist)
        elif ans == 2:
            draw_pie(percentdf)
        elif ans == 3:
            show_trend(countydf, 1)
        elif ans == 4:
            show_trend(countydf, 2)
        elif ans == 5:
            print("Please Choose the Presentation You Want to See: ")
            print("1 - Number of Best Buy Stores in USA States")
            print("2 - Number of Apple Stores in USA States")
            print("3 - Rate Between Population and Number of Best Buy Stores in USA States")
            print("4 - Rate Between Population and Number of Apple Stores in USA States")
            while True:
                collected_map = correct_input(4)
                if collected_map == 'e':
                    break
                else:
                    show_gradientmap(collected_map-1)
        else:
            break
        print('_________________________________________')


# Generate global variables, which are also used in the Flask presentation

save_gradientmap(dict_list)
percent_df = get_percent(dict_list[1])
countydata = data_store(dict_list[1])
statedata = save_gradientmap(dict_list)

if __name__ == '__main__':
    comandline_show(dict_list, percent_df, countydata)


