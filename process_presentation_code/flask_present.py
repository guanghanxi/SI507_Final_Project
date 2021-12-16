import process as p
import numpy as np
import pandas as pd
import plotly.graph_objects as go 
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request
import base64
from io import BytesIO

# The function to show the percentage of different counties

def get_percent_data():
    pie_data = go.Pie(labels=p.percent_df['group'], values = p.percent_df['percent'])
    basic_layout = go.Layout(title="US County Distribution")
    fig = go.Figure(data=[pie_data], layout=basic_layout)
    graphJSON = fig.to_json()
    return graphJSON

# The function to show the percentage of different counties

def figure_data(county_df, store_type):
    '''
    Save the figure for the 
    '''
    if store_type == 1:
        store_choice = 'With_Best_Buy'
        picture_name = 'bestbuy_county.png'
    else:
        store_choice = 'With_Apple'
        picture_name = 'apple_county.png'
    store_df = county_df[['POP', 'DENSITY', 'Median Home Income', store_choice]]
    fig= plt.figure()
    plt.rcParams.update({"font.size":10})
    axes = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223) ]
    fig.set_figheight(10)
    fig.set_figwidth(14)
    fig.suptitle("Distribution of US Counties' Population, Population Density and Median Home Income")
    sns.kdeplot(data = store_df, x='POP', hue = store_choice, ax=axes[0], shade='Ture', log_scale=(True, False))
    axes[0].set_xlabel('Population')
    sns.kdeplot(data = store_df, x='DENSITY', hue = store_choice, ax=axes[1], shade='Ture', log_scale=(True, False))
    axes[1].set_xlabel('Population Density')
    sns.kdeplot(data = store_df, x='Median Home Income', hue = store_choice, ax=axes[2], shade='Ture', log_scale=(True, False))
    axes[2].set_xlabel('Median Home Income ($)')
    plt.subplots_adjust(hspace=0.2)
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    imb = base64.b64encode(plot_data) 
    ims = imb.decode()
    imd = "data:image/png;base64," + ims
    return imd

# The following function is used to show the Bestbuy and Apple Stores distribution in the USA

def distribution_data(num):
    state_df = p.statedata
    if num == '1':
        fig = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Best_Buy_Num'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Number of Best Buy Stores")) 
        fig.update_layout( title_text = 'Number of Best Buy Stores in USA States', geo_scope='usa')
    elif num == '2':
        fig = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Apple'].astype(int), 
            locationmode = 'USA-states', colorscale = 'Greys', colorbar_title = "Number of Apple Stores")) 
        fig.update_layout( title_text = 'Number of Apple Stores in USA States', geo_scope='usa')
    elif num == '3':
        fig = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Best_Buy'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Population / Num of Best Buy")) 
        fig.update_layout( title_text = 'Rate Between Population and Number of Best Buy Stores in USA States', geo_scope='usa')
    else:
        fig = go.Figure(data=go.Choropleth(locations=state_df['ABR'], z = state_df['Pop_Apple'].astype(int), 
            locationmode = 'USA-states', colorscale = 'YlGnBu', colorbar_title = "Population / Num of Apple")) 
        fig.update_layout( title_text = 'Rate Between Population and Number of Apple Stores in USA States', geo_scope='usa')
    graphJSON = fig.to_json()
    return graphJSON


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') # The page for users to choose presentation options

@app.route('/state')
def state_form():
    return render_template('state.html', state_list = p.dict_list[0].values()) # Choose the state

@app.route('/county', methods=['POST']) # Choose the County
def handle_state():
    state = request.form["states"]
    county_fips_list = p.dict_list[0][state]['county_list']
    county_list = []
    for fipscode in county_fips_list:
        county_list.append( p.dict_list[1][fipscode])
    return render_template('county.html', countylist=county_list)

@app.route('/store', methods=['POST']) # Show Stores
def handle_county():
    county = request.form["county"]
    bestbuy_code_list = p.dict_list[1][county]['bestbuy_list']
    apple_code_list = p.dict_list[1][county]['apple_list']
    bestbuy_list = []
    for bb_code in  bestbuy_code_list:
        bestbuy_list.append( p.dict_list[2][bb_code])
    apple_list = []
    for a_code in  apple_code_list:
        apple_list.append( p.dict_list[2][a_code])
    return render_template('store.html', county = p.dict_list[1][county]['NAME'], bestbuylist=bestbuy_list, applelist=apple_list)

@app.route('/percentage')
def percentage():
    piedata = get_percent_data()
    return render_template('percent.html', pie = piedata)


@app.route('/bestbuy_county')
def bestbuy_county():
    content = ['Best Buy', 'bestbuy_county.png']
    content.append('Counties with larger population are more likely to have Best Buy Stores')
    content.append('Counties with higher population densities are more likely to have Best Buy Stores')
    content.append("Whether a County has Best Buy has little to do with the County's Median Home Income")
    return render_template('store_county.html', context = content, image = figure_data(p.countydata, 1)) 

@app.route('/apple_county')
def apple_county():
    content = ['Apple', 'apple_county.png']
    content.append('Counties with larger population are more likely to have Apple Stores')
    content.append('Counties with higher population densities are more likely to have Apple Stores')
    content.append("Whether a County has Apple Stores has little to do with the County's Median Home Income")
    return render_template('store_county.html', context = content, image = figure_data(p.countydata, 2)) 

@app.route('/distribution')
def distribution():
    return render_template('distribution.html') # Let user choose the distribution kind

@app.route('/distribution_show', methods=['POST'])
def show_distribution():
    k = request.form["dist_type"]
    titile_list = ['Number of Best Buy Stores in the Different States Respectively', 'Distribution of Apple Stores in the Different States Respectively',
    'How Much Population Does One Best Buy Store Serve in the Different States Respectively?', 
    'How Much Population Does One Apple Store Serve in the Different States Respectively?']
    content = [titile_list[int(k)-1]]
    return render_template('map.html', plot = distribution_data(k), context = content)

if __name__ == "__main__":
    app.run(debug=True) 