# In[]:
# Import required libraries
import os
import copy
import datetime as dt
# import flask

import pandas as pd
from flask_cors import CORS
from flask import send_from_directory, Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dashInterface
from controls import CATEGORY_NAME, CATEGORY_COLORS
import dash_table_experiments as dte



# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
server = app.server


# app.config.suppress_callback_exceptions = True
app.title = 'Dashboard Demo'
CORS(server)


@server.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(server.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# if 'DYNO' in os.environ:
#     app.scripts.append_script({
#         'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
#     })

# Create controls

df = pd.read_csv('../data/userTable.csv')
DF_GAPMINDER = df
DF_GAPMINDER.loc[:20]

category_name_options = [{'label': str(CATEGORY_NAME[category_name]),
                        'value': str(category_name)}
                       for category_name in CATEGORY_NAME]



# Create global chart template

layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
)

test=''

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns ])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col] ) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def get_header():
    header=html.Div(
        [
            html.H1(
                'Admin Dashboard \n',
                className='eight columns',
            ),
            html.Img(
                src="https://www.covetly.com/Content/images/covetly-logo-trans-with-slight-space-top-and-bottom.png",
                className='one columns',
                style={
                    'height': '80',
                    'width': '225',
                    'float': 'right',
                    'position': 'relative',
                },
            ),
        ],
        className='row'
    )
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Demo   ', href='/demo', className="tab first"),

        dcc.Link('About Myself   ', href='/myself', className="tab"),

    ], className="row ")
    return menu

# In[]:
# Create app layout
app.layout = html.Div(
    [   #Top text and logo
        get_header(),
        html.Br([]),
        # get_menu(),
        html.Div(
            [
                html.H2(''),
                html.H2(
                    'Inventory health report',
                    className='twelve columns',
                    style={'textAlign': 'center',}
                ),
            ],
        ),
        html.Div(
            [
                html.P('Filter by categories:'),
                dcc.RadioItems(
                    id='category_name_selector',
                    options=[
                        {'label': 'All   ', 'value': 'all'},
                        {'label': '  LowInventory(top3)  ', 'value': 'LowInventory(top3)'},
                        {'label': '  Customize ', 'value': 'custom'}
                    ],
                    value='LowInventory(top3)',
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.Dropdown(
                    id='category_name_dropdown',
                    options=category_name_options,
                    multi=True,
                    value=[]
                ),
                # dcc.Checklist(
                #     id='lock_selector',
                #     options=category_name_options,
                #     values=[],
                # )
            ],
            className='twelve columns'
        ),


        # Fig.1 and Fig. 2
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="category_inventory_graph")
                    ],
                    className='eight columns',
                    style={'margin-top': '20', 'marginBottom': 40}
                ),
                html.Div(
                    [
                        dcc.Graph(id='subcategory_inventory_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '20', 'marginBottom': 40}
                ),
            ],
        ),
        html.Div(
            [
                html.H2(''),
                html.H2(
                    '\nPotential high-impact sellers\n',
                    style={'text-align': 'center'},
                    className='twelve columns',
                ),
            ],
            className='row'
        ),




        html.Div([
            # html.H4('Gapminder DataTable'),
            dte.DataTable(
                rows=[{}],
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='datatable-gapminder'
            # optional - sets the order of columns
                # columns=sorted(DF_GAPMINDER.columns)
            ),
            html.Div(id='selected-indexes'),
        ], className="container"),



        # Overview Section
        html.Div(
            [
                html.H2(''),
                html.H2(
                    'Business Overview ',
                    className='twelve columns',
                    style={'text-align': 'center','margin-top': '40', 'marginBottom': 20},
                ),
            ],
            className='row'
        ),

    # Fig.1 and Fig. 2
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="summary_graph")
                    ],
                    className='eight columns',
                    style={'margin-top': '20', 'marginBottom': 40}
                ),
                html.Div(
                    [
                        dcc.Graph(id='byCategory_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '20', 'marginBottom': 40}
                ),
            ],
        ),

        # Users and Sellers section
        html.Div(
            [
                html.H1(''),
                html.H1(
                    'Users and Sellers',
                    className='eight columns',
                ),
            ],
            className='row'
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='user_seller_graph')
                    ],
                    className='twelve columns',
                    style={'margin-top': '20', 'marginBottom': 40}
                ),
            ]),
    ],
    className='ten columns offset-by-one',
)

# Describe the layout, or the UI, of the app







@app.callback(Output('datatable-gapminder', 'rows'),
              [Input('category_name_dropdown', 'value')],)
def update_table(category_name_dropdown):
    """
    For user selections, return the relevant table
    """
    df = pd.read_csv('../data/userTable.csv')
    selectedCategories = [CATEGORY_NAME[idx] for idx in category_name_dropdown]
    selected_weight = list(df[selectedCategories].sum(axis=1))
    df['score'] = [int(selected_weight[idx] * list(df['likelihood'])[idx] * 100) / 100 for idx in range(df.shape[0])]
    df_to_print = df.iloc[:, :3].join(df.loc[:, selectedCategories]).join(df['score'])
    df_to_print = df_to_print.sort_values(by='score', ascending=False)
    return df_to_print.to_dict('records')




@app.callback(Output('category_name_dropdown', 'value'),
              [Input('category_name_selector', 'value')])
def display_type(selector):
    if selector == 'all':
        return list(CATEGORY_NAME.keys())
    elif selector == 'LowInventory(top3)':
        return ['Funko', 'Amiibo',  'Dorbz']
    else:
        return ['Funko', 'Amiibo', 'Dorbz']




###############################
#Inventory graphs
##############################

@app.callback(Output('category_inventory_graph', 'figure'),
              [Input('category_name_dropdown', 'value')],
              [State('summary_graph', 'relayoutData')])  # No input this time. [Input('main_graph', 'hoverData')]
def make_category_inventory_figure(category_name_dropdown, category_inventory_graph_layout):
    data=[]
    category_inventory_df= pd.read_csv("../data/category_inventory.csv", index_col=0)
    for idx in range(len(category_name_dropdown)):
        print(CATEGORY_NAME[category_name_dropdown[idx]])

        data.append(dict(
            type='scatter',
            mode='lines+markers',
            name=category_name_dropdown[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in category_inventory_df.columns[1:]],
            y=[int(y) for y in list(category_inventory_df.loc[CATEGORY_NAME[category_name_dropdown[idx]]])],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color=CATEGORY_COLORS[idx]
            ),
            marker=dict(symbol='diamond-open')
        ))
    # What's the function of selector? "and 'locked' in selector"
    # print(category_inventory_graph_layout)
    # if (category_inventory_graph_layout is not None):
    #     lon = float(category_inventory_graph_layout['mapbox']['center']['lon'])
    #     lat = float(category_inventory_graph_layout['mapbox']['center']['lat'])
    #     zoom = float(category_inventory_graph_layout['mapbox']['zoom'])
    #     layout['mapbox']['center']['lon'] = lon
    #     layout['mapbox']['center']['lat'] = lat
    #     layout['mapbox']['zoom'] = zoom
    # else:
    lon = -78.05
    lat = 42.54
    zoom = 7

    layout_individual = copy.deepcopy(layout)
    layout_individual['title'] = 'Inventory Health Report (wishlist/inventory)'  # noqa: E501
    figure = dict(data=data, layout=layout_individual)
    return figure

######################################################################



#Figure 2##############################################################
# data: [collection, new_order, new_wishlist]

@app.callback(Output('subcategory_inventory_graph', 'figure'),
              [Input('category_inventory_graph', 'hoverData'),
               Input('category_name_dropdown', 'value')])   # No input this time. [Input('main_graph', 'hoverData')]
def make_subcategory_inventory_graph(category_inventory_graph_hover,category_name_dropdown):
    if category_inventory_graph_hover is None:
        category_inventory_graph_hover = {'points': [{'curveNumber': 0,
                                        'pointNumber': 569,
                                        'customdata': 31101173130000}]}
    print(category_inventory_graph_hover['points'])
    chosenFigure = 1   # Initialize figure to show as new orders by category
    chosen = [point['curveNumber'] for point in category_inventory_graph_hover['points']]
    chosenFigure = chosen[0]
    chosenName = CATEGORY_NAME[category_name_dropdown[chosenFigure]]

    subcategory_inventory_df = pd.read_csv("../data/sub_category_inventory.csv")
    subcategory_inventory_df = subcategory_inventory_df[subcategory_inventory_df["Category"]==chosenName].iloc[:,1:]
    # Plot collection to data
    colors = ['#F9ADA0', '#849E68', '#59C3C3','#67BD65','#FDBF6F',]

    # Plot user to data1
    data=[]
    names = list(subcategory_inventory_df['subcategory'])
    for idx in range(min(subcategory_inventory_df.shape[0],3)):
        data.append(dict(
            type='scatter',
            mode='lines+markers',
            name=names[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in subcategory_inventory_df.columns[1:]],
            y=[int(y) for y in subcategory_inventory_df.iloc[idx,1:]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color=colors[idx]
            ),
            marker=dict(symbol='diamond-open')
        ))


    layout_individual = copy.deepcopy(layout)
    layout_individual['title'] = '%s Sub-category Inventory' %(chosenName.capitalize())  # noqa: E501
    figure = dict(data=data, layout=layout_individual)
    return figure

######################################################################



@app.callback(Output('summary_graph', 'figure'),
              [Input('category_name_dropdown', 'value')],
              [State('summary_graph', 'relayoutData')])  # No input this time. [Input('main_graph', 'hoverData')]
def make_summary_figure(userId,summary_graph_layout):
    data=[]
    summary_df = dashInterface.summary()
    names=['New orders', 'New Collections (k)', 'New Wishlist (k)']
    colors=['#F9ADA0','#849E68','#59C3C3','#fac1b7']
    for idx in range(3):
        data.append(dict(
            type='scatter',
            mode='lines+markers',
            name=names[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in summary_df.columns[1:]],
            y=[int(y) for y in summary_df.iloc[idx,1:]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color= colors[idx]
            ),
            marker=dict(symbol='diamond-open')
        ))

    # What's the function of selector? "and 'locked' in selector"
    if (summary_graph_layout is not None and 'locked' in selector):

        lon = float(summary_graph_layout['mapbox']['center']['lon'])
        lat = float(summary_graph_layout['mapbox']['center']['lat'])
        zoom = float(summary_graph_layout['mapbox']['zoom'])
        layout['mapbox']['center']['lon'] = lon
        layout['mapbox']['center']['lat'] = lat
        layout['mapbox']['zoom'] = zoom
    else:
        lon = -78.05
        lat = 42.54
        zoom = 7

    layout_individual = copy.deepcopy(layout)
    layout_individual['title'] = 'Business Overview'  # noqa: E501
    figure = dict(data=data, layout=layout_individual)
    return figure

######################################################################



#Figure 2##############################################################
# data: [collection, new_order, new_wishlist]

@app.callback(Output('byCategory_graph', 'figure'),
              [Input('summary_graph', 'hoverData')])   # No input this time. [Input('main_graph', 'hoverData')]
def make_byCategory_graph(summary_graph_hover):
    if summary_graph_hover is None:
        summary_graph_hover = {'points': [{'curveNumber': 0,
                                        'pointNumber': 569,
                                        'customdata': 31101173130000}]}
    print(summary_graph_hover['points'])
    chosenFigure = 1   # Initialize figure to show as new orders by category
    chosen = [point['curveNumber'] for point in summary_graph_hover['points']]
    chosenFigure = chosen[0]

    # Plot collection to data
    colors = ['#F9ADA0', '#849E68', '#59C3C3','#67BD65','#FDBF6F',]

    # Plot user to data1
    data0=[]
    users_df = dashInterface.ordersGroupbyCategory()
    names = list(users_df['CategoryName'])
    for idx in range(users_df.shape[0]):
        data0.append(dict(
            type='scatter',
            mode='lines+markers',
            name=names[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in users_df.columns[1:]],
            y=[int(y) for y in users_df.iloc[idx,1:]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color=colors[idx]
            ),
            marker=dict(symbol='diamond-open')
        ))


    data1=[]
    collections_df = dashInterface.collectionGroupbyModule()
    names = list(collections_df.module)
    for idx in range(collections_df.shape[0]):
        data1.append(dict(
            type='scatter',
            mode='lines+markers',
            name=names[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in collections_df.columns[1:-1]],
            y=[int(y) for y in collections_df.iloc[idx,1:-1]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color=colors[idx]
            ),
            marker=dict(symbol='diamond-open')
        ))

    data2=[]
    users_df = dashInterface.wishlistGroupbyModule()
    names = list(users_df['category'])
    for idx in range(users_df.shape[0]):
        data2.append(dict(
            type='scatter',
            mode='lines+markers',
            name=names[idx],
            x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in users_df.columns[1:]],
            y=[int(y) for y in users_df.iloc[idx,1:]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color=colors[idx]
            ),
            marker=dict(symbol='circle-open')
        ))

    data=[data0, data1, data2]

    layout_individual = copy.deepcopy(layout)
    layout_individual['title'] = ['New Collections by Category','New Orders by Category', 'New Wishlist by Category'][chosenFigure]  # noqa: E501
    figure = dict(data=data[chosenFigure], layout=layout_individual)
    return figure

######################################################################



@app.callback(Output('user_seller_graph', 'figure'),
              [Input('category_name_dropdown', 'value')])   # No input this time. [Input('main_graph', 'hoverData')]
def make_user_seller_graph(summary_graph_hover):

    data=[]
    df_user_seller = dashInterface.summary()
    print(df_user_seller)
    df_user_seller = df_user_seller.iloc[3:5,:]
    names=['New users', 'New sellers']
    colors=['#59C3C3','#fac1b7']

    data.append(dict(
        type='scatter',
        mode='lines+markers',
        name='New users (*100)',
        x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in df_user_seller.columns[1:]],
        y=[int(y*10) for y in df_user_seller.iloc[0,1:]],
        line=dict(
            shape="spline",
            smoothing=2,
            width=1,
            color= colors[0]
        ),
        marker=dict(symbol='diamond-open')
    ))

    data.append(dict(
        type='scatter',
        mode='lines+markers',
        name='New sellers',
        x=[dt.datetime(year=2017+int(int(x)/12),month=1+int(int(x)%12),day=1) for x in df_user_seller.columns[1:]],
        y=[int(y) for y in df_user_seller.iloc[1,1:]],
        line=dict(
            shape="spline",
            smoothing=2,
            width=1,
            color= colors[1]
        ),
        marker=dict(symbol='diamond-open')
    ))

    layout_individual = copy.deepcopy(layout)
    layout_individual['title'] = 'New users and sellers'  # noqa: E501
    figure = dict(data=data, layout=layout_individual)
    return figure


#
#
#
# # Selectors, main graph -> pie graph
# @app.callback(Output('pie_graph', 'figure'),
#               [Input('CATEGORY_NAME', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value')])
# def make_pie_figure(CATEGORY_NAME, well_types, year_slider):
#
#     layout_pie = copy.deepcopy(layout)
#
#     dff = filter_dataframe(df, CATEGORY_NAME, well_types, year_slider)
#
#     selected = dff['API_WellNo'].values
#     index, gas, oil, water = fetch_aggregate(selected, year_slider)
#
#     aggregate = dff.groupby(['Well_Type']).count()
#
#     data = [
#         dict(
#             type='pie',
#             labels=['Gas', 'Oil', 'Water'],
#             values=[sum(gas), sum(oil), sum(water)],
#             name='Production Breakdown',
#             text=['Total Gas Produced (mcf)', 'Total Oil Produced (bbl)', 'Total Water Produced (bbl)'],  # noqa: E501
#             hoverinfo="text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(
#                 colors=['#fac1b7', '#a9bb95', '#92d8d8']
#             ),
#             domain={"x": [0, .45], 'y':[0.2, 0.8]},
#         ),
#         dict(
#             type='pie',
#             labels=[WELL_TYPES[i] for i in aggregate.index],
#             values=aggregate['API_WellNo'],
#             name='Well Type Breakdown',
#             hoverinfo="label+text+value+percent",
#             textinfo="label+percent+name",
#             hole=0.5,
#             marker=dict(
#                 colors=[WELL_COLORS[i] for i in aggregate.index]
#             ),
#             domain={"x": [0.55, 1], 'y':[0.2, 0.8]},
#         )
#     ]
#     layout_pie['title'] = 'Production Summary: {} to {}'.format(year_slider[0], year_slider[1])  # noqa: E501
#     layout_pie['font'] = dict(color='#777777')
#     layout_pie['legend'] = dict(
#         font=dict(color='#CCCCCC', size='10'),
#         orientation='h',
#         bgcolor='rgba(0,0,0,0)'
#     )
#
#     figure = dict(data=data, layout=layout_pie)
#     return figure
#
#
# # Selectors -> count graph
# @app.callback(Output('count_graph', 'figure'),
#               [Input('CATEGORY_NAME', 'value'),
#                Input('well_types', 'value'),
#                Input('year_slider', 'value')])
# def make_count_figure(CATEGORY_NAME, well_types, year_slider):
#
#     layout_count = copy.deepcopy(layout)
#
#     dff = filter_dataframe(df, CATEGORY_NAME, well_types, [1960, 2017])
#     g = dff[['API_WellNo', 'Date_Well_Completed']]
#     g.index = g['Date_Well_Completed']
#     g = g.resample('A').count()
#
#     colors = []
#     for i in range(1960, 2018):
#         if i >= int(year_slider[0]) and i < int(year_slider[1]):
#             colors.append('rgb(192, 255, 245)')
#         else:
#             colors.append('rgba(192, 255, 245, 0.2)')
#
#     data = [
#         dict(
#             type='scatter',
#             mode='markers',
#             x=g.index,
#             y=g['API_WellNo'] / 2,
#             name='All Wells',
#             opacity=0,
#             hoverinfo='skip'
#         ),
#         dict(
#             type='bar',
#             x=g.index,
#             y=g['API_WellNo'],
#             name='All Wells',
#             marker=dict(
#                 color=colors
#             ),
#         ),
#     ]
#
#     layout_count['title'] = 'Completed Wells/Year'
#     layout_count['dragmode'] = 'select'
#     layout_count['showlegend'] = False
#
#     figure = dict(data=data, layout=layout_count)
#     return figure


# In[]:
# Main
if __name__ == '__main__':
    app.server.run(host= '0.0.0.0',debug=True)