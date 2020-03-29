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
    ),


    html.Div(
        [dcc.Markdown('''

                # description

                ### guiding question: 

                #### *HOW COULD CAINS BE IMPROVED BY THE ABILITY TO TRADE INTO A US PEGGED STABLE COIN?*

                To answer this question, I built a naive model that learns based on only historical trading data for Bitcoin (BTC), Ethereum (ETH), and Litecoin (LTC). The goal of the model was to MAXIMIZE RETURNS of an investment STARTING WITH 1000, and it assumed no friction (trade cost is 0). 

                The model would be built with three variations: 

                >1) assume YOU CAN ONLY TRADE IN CRYPTO, but hold the same position without shifting balances. The initial holdings reflect the best predicted share of crypto based on historical growth averages up until Jan 1st. 

                >2) assume YOU CAN ONLY TRADE IN CRYPTO, but shift balances based on which crypto was expected to perform best under the expected market conditions. 

                >3) allow the model to TRADE INTO A STABLE COIN, thus shifting out of the crypto market when it appeared to be down, and then strategically shifting into crypto with high up potential when the crypto market appeared to be shifting upwards. 

                The period of interest was between January 1st 2018 and September 2019. The data available crossed multiple periods ensuring the model could adapt in the presence of new information.  

                A different distinct model was built for each period based on available data up until that point. As such, the model for first period, starting the first of January, was trained on all previous trading history for ethereum and bitcoin prior. A new instance of the model was created for each period thereafter and included an additional set of data from the previous period. Thus the final trading suggestions was the output of over a hundred instances of distinct models. The feature data was a rolling average aggregation of data from previous periods. The label data was the current period. The training period and the number of periods to aggregate over were hyperperamters that the user can shift in the final dashboard.  

                The model used classification models for multilayered predictions. 

                The R2 and soft outputs (probabilities) of these models were used to designate how much of the investment pool to shift. The stronger the predictions the more of the funds were designated accordingly. 

                    '''
        , id='description'),
        html.Img(src=app.get_asset_url('readmeimgs/crypto_data_overview.png')),
        html.Img(src=app.get_asset_url('readmeimgs/decision_framework.png'))
        
        ],


    id='outer_container'
    )



],




)



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
