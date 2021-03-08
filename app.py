## Import packages
import pandas as pd
import numpy as np
import csv
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.offline as py
import plotly.graph_objs as go

from colour import Color
import plotly.express as px
import dash_bootstrap_components as dbc

## set tokens
mapbox_access_token = "pk.eyJ1IjoiYmVubnlmcmllZG1hbjIiLCJhIjoiY2tscWFkNjJkMG0weDJwbzBqZWIwdGo1YyJ9.uv09LILlWEtSukyyXeoUzQ"

intersections = pd.read_csv(r"F:\Projects\CollisoinTool\subset_instersections_w_count_2.csv", low_memory=False)
collisions = pd.read_csv(r"F:\Projects\CollisoinTool\collisions_data_w_intID_year.csv")

## create intersections color ramp
collision_min = intersections['Collisions'].min()
collision_max = intersections['Collisions'].max()
collision_range = collision_max - collision_min
steps = np.linspace(0, collision_max * 0.3, 10).tolist()
print(steps)

start = Color("#f2df91")
stop = Color('#4C0D3E')
color_list = list(start.range_to(stop,10))
print(color_list)



def get_color(val):
    for i in range(0, len(steps)):
        # color = start
        if steps[i] < val < steps[i + 1]:
            return color_list[i + 1].hex
        if val == steps[0]:
            return color_list[0].hex
        if val >= steps[-1]:
            return color_list[-1].hex



color_map = []
for index, row in intersections.iterrows():
    count = row['Collisions']
    color = get_color(count)
    color_map.append(color)

intersections['Color Map'] = color_map
print(intersections.head())

## app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.Title('NC Collision Tool'),

    ## Header
    html.Div([
        html.H1('Neighborhood Council Collisions Explorer')
    ], style={'width' : '60%', 'marginLeft' : 'auto', 'marginRight' : 'auto', 'padding-top' : '3%', 'marginBottom' : '7%', 'text-align' : 'center'}),

    ## ROW 1
    dbc.Row([
        dbc.Col([
            ## neighborhood checkbox
            html.Div([
                html.Label(children=["Select Neighborhood Council District: "], style={'color' : 'black', 'font-weight' : 'bold'}),
                dcc.Checklist(id='neighborhood',
                    options=[{'label' : b, 'value' :b} for b in sorted(intersections['name'].replace(np.nan, "NA").unique())],
                    # value=[b for b in sorted(df['Area Name'].unique())],
                    value=[],
                    labelStyle= {'marginLeft' : '10px'}
                    ),
            ], style={'marginTop' : '40%', 'marginBottom' : '15%'}),

        ], width={'size': 3}),

        dbc.Col([
            ## Map
            # html.Div([
                dcc.Graph(id='map', config={'displayModeBar' : False, 'scrollZoom': True},
                    style={'background': 'white', 'padding-bottom': '2px', 'padding-left' : '2px', 'height' : '100vh'})
            # ]),

        ], width={'size' : 9})
    ], style={'margin-left' : 'auto', 'margin-right' : 'auto', 'width' : '80%'}),


    html.Div([
        dcc.Graph(id='collisionsbyyear', config={'displayModeBar' : False, 'scrollZoom': True},
            style={'background': 'white', 'height' : '60vh'})
    ], style={'width': '80%', 'height' : '20%', 'margin-left': 'auto', 'margin-right' : 'auto', 'margin-top' : '1%'}),

    html.Div([
        dcc.Graph(id='collisionsbyage', config={'displayModeBar' : False, 'scrollZoom': True},
            style={'background': 'white', 'padding-bottom': '2px', 'padding-left' : '2px', 'height' : '60vh'})
    ], style={'width': '80%', 'height' : '20%', 'margin-left': 'auto', 'margin-right' : 'auto', 'margin-top' : '1%'}),

    html.Div([
        dcc.Graph(id='collisionsbyType', config={'displayModeBar' : False, 'scrollZoom': True},
            style={'background': 'white', 'padding-bottom': '2px', 'padding-left' : '2px', 'height' : '60vh'})
    ], style={'width': '80%', 'height' : '20%', 'margin-left': 'auto', 'margin-right' : 'auto', 'margin-top' : '1%'}),

    # html.Div([
    #     dash_table.DataTable(
    #         id= 'table',
    #         columns=[{"name" : i, 'id' : i} for i in collisions.columns],
    #         data = []
    #     )
    # ])

], style={'background' : '#F1F1F1'})

## --------------------------------------------------------------------
@app.callback(Output('map', 'figure'),
    [Input('neighborhood', 'value')])

def update_figure(chosen_dist):
    intersections_sub = intersections[(intersections['name'].isin(chosen_dist))]
    print(intersections_sub.shape)
    ## Create figure
    locations=[go.Scattermapbox(
                lon = intersections_sub['Long'],
                lat = intersections_sub['Lat'],
                mode = 'markers',
                marker={'color': intersections_sub['Color Map'], 'opacity' : 0.30, 'size': 15},
                unselected={'marker': {'opacity': 0.20, 'size' : 15}},
                selected={'marker': {'opacity' : 0.7, 'size' : 25}},
                showlegend=False,
                hoverinfo='text',
                hovertext=intersections_sub['Collisions'],
                customdata = intersections_sub['int_id']
    )]

    ## return figure
    return {
        'data' : locations,
        'layout' : go.Layout(
            uirevision = 'foo',
            clickmode= 'event+select',
            hovermode= 'closest',
            hoverdistance=2,
            title= dict(text="Collision Map", font=dict(size=24, color='black')),
            mapbox=dict(
                accesstoken = mapbox_access_token,
                bearing=0,
                style = 'light',
                center= dict(
                    lat=34.05223,
                    lon = -118.24368
                ),
                pitch=40,
                zoom=11.5
            ),
        )
    }

## Callback for plots
@app.callback(
    Output('collisionsbyyear', 'figure'),
    [Input('map', 'clickData')])
def display_click_data(clickData):
    print('Callback Active')
    if clickData == None:
        print('no data selected')
        return {
            'data' : [],
            'layout' : go.Layout(
                title= dict(text='Collisions by Year', font=dict(size=24, color='black'))
            )
        }

    else:
        intersection_id = clickData['points'][0]['customdata']
        this_intersection_sub = collisions[collisions['int_id'] == intersection_id]
        by_year = this_intersection_sub.groupby('Year Occurred').count()
        # print(by_year.index)

        datapoints = [go.Bar(
                        x = by_year.index,
                        y = by_year['count'],
                        marker = {'color': 'red'}
        )]

        return {
            'data' : datapoints,
            'layout' : go.Layout(
                title= dict(text='Collisions by Year', font=dict(size=24, color='black'),
                )
            )
        }


@app.callback(
    Output('collisionsbyage', 'figure'),
    [Input('map', 'clickData')])
def display_click_data(clickData):
    print('Callback Active')
    if clickData == None:
        print('no data selected')
        return {
            'data' : [],
            'layout' : go.Layout(
                title= dict(text='Collisions by Victim Age', font=dict(size=24, color='black'))
            )
        }

    else:
        intersection_id = clickData['points'][0]['customdata']
        this_intersection_sub = collisions[collisions['int_id'] == intersection_id]
        hist,bins = np.histogram(this_intersection_sub['Victim_Age'],bins = [0,20,40,60,80,100])
        formatted_bin_names = []
        for i in range(1, len(bins + 1)):
            prev_bin = bins[i - 1]
            cur_bin = bins[i]
            formatted_bin_names.append("{}-{}".format(prev_bin, cur_bin))

        print(formatted_bin_names)





        datapoints = [go.Bar(
                        x = formatted_bin_names,
                        y = hist,
                        marker = {'color': 'red'}
        )]

        return {
            'data' : datapoints,
            'layout' : go.Layout(
                title= dict(text='Collisions by Victim Age', font=dict(size=24, color='black'),
                )
            )
        }

@app.callback(
    Output('collisionsbyType', 'figure'),
    [Input('map', 'clickData')])
def display_click_data(clickData):
    print('Callback Active')
    if clickData == None:
        print('no data selected')
        return {
            'data' : [],
            'layout' : go.Layout(
                title= dict(text='Collisions by Type', font=dict(size=24, color='black'))
            )
        }

    else:
        intersection_id = clickData['points'][0]['customdata']
        this_intersection_sub = collisions[collisions['int_id'] == intersection_id]
        type_codes = pd.read_csv('type_codes.csv')
        type_dict = {}
        for index, row in type_codes.iterrows():
            type_code = row['code']
            collision_type = row['type']
            type_dict[type_code] = collision_type

        print(type_dict)
        mo_codes = this_intersection_sub['MO_Codes']
        collision_types = []
        for codes in mo_codes:
            codes_arr = str(codes).split(' ')
            this_collision_type = "Not Specified"
            for code in codes_arr:
                try:
                    this_collision_type = type_dict[int(code)]
                except:
                    pass
            collision_types.append(this_collision_type)

        this_intersection_sub['collision_type'] = collision_types

        by_type = this_intersection_sub.groupby('collision_type').count()



        datapoints = [go.Bar(
                        x = by_type.index,
                        y = by_type['count'],
                        marker = {'color': 'red'}
        )]

        return {
            'data' : datapoints,
            'layout' : go.Layout(
                title= dict(text='Collisions by Type', font=dict(size=24, color='black'),
                )
            )
        }



# @app.callback(
#     Output('table', 'data'),
#     [Input('map', 'clickData')])
#
# def update_table(clickData):
#     if clickData == None:
#         print('no data selected')
#         return []
#     else:
#         intersection_id = clickData['points'][0]['customdata']
#         this_intersection_sub = collisions[collisions['int_id'] == intersection_id]
#         # print(this_intersection_sub.to_dict('rows'))
#         return this_intersection_sub.to_dict('rows')











if __name__ == '__main__':
    app.run_server(debug=True)
