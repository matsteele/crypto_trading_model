import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import datetime as dt
import plotly.graph_objs as go
import urllib

from initiate import pullDataForChart

app = dash.Dash(__name__)
server = app.server
app.title = "CRYPTO TRADING MODEL"
git 
app.layout = html.Div(children=[
    html.H1(children='CRYPTO TRADING MODEL'),

    html.P(children='''
        modeled using gradient boosted trees
    ''', id='subheader'),

    html.Div(
        [html.Div(
            children=[
                html.H3(
                    'holding period'
                ),
                dcc.Slider(
                    id='bin_slider',
                    min=2,
                    max=4,
                    value=2,
                    marks={
                        2: '2 days',
                        3: '3 days',
                        4: '4 days'
                    },
                    step=1
                ),
                html.H3(
                    'learning window'
                ),
                dcc.Slider(
                    id='window_slider',
                    min=1,
                    max=4,
                    value=1,
                    marks={
                        1: '1 period',
                        2: '2 periods',
                        3: '3 periods',
                        4: '4 periods'
                    },
                    step=1
                ),
                html.A(children='download data selected', id='dwnload',
                       download="crypto_data.csv", target="_blank")
                ],
            id='sidebar'
        ),
            dcc.Graph(
            id='main-graph'
        )
        ],
        id='main'
    )
])



@app.callback([Output('main-graph', 'figure'), Output('dwnload', 'href')],
              [Input('bin_slider', 'value'), Input('window_slider', 'value')])
def update_subgraph_onHover(days,window ):
    df = pullDataForChart(days, window)
    
    print(df.columns)
    
    figure = {
        'data': [
            {
                'x': df.dates,
                'y': df.account_val,
                'type': 'line',
                'name': 'crypto only balance',
                'line': {
                    'color': '#FDA192'
                }
            },
            {
                'x': df.dates,
                'y': df.valueof_intial_holding,
                'type': 'line',
                'name': 'no changes balance',
                'line': {
                    'color': '#6E8698'
                }
            },
            {
                'x': df.dates,
                'y': df.ifusd_account_val,

                'type': 'line',
                'name': 'with USD account bal',
                'line': {
                    'color': '#328BCA'
                },
                
            },
            {
                'x': df.dates,
                'y': (1-df.error)*100,
                'type': 'bar',
                'name': 'incorrect prediction',
                'line': {
                    'color': '#CA3031'
                }
            },
        ],
        'layout': {
            'width': '50%',
            'legend': dict(x=.5, y=1.2),
            'yaxis': {'title': 'balance'},
            'font': {
                'size': '8',
                'color': 'grey'
            }
        }
    }


    csvString = df.to_csv(index=False, encoding='utf-8')
    csvString = "data:text/csv;charset=utf-8," + urllib.parse.quote(csvString)

    return figure, csvString




if __name__ == '__main__':
    app.run_server(debug=True)
