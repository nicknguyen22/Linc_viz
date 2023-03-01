import dash                                     
from dash import Dash, dcc, html, Input, Output, callback
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date
import pandas as pd

lincoln_df = pd.read_csv('lincoln_df.csv')
lincoln_daily = lincoln_df.groupby(['ICP','ReadingDate'],as_index=False)['kWh'].sum().reset_index(drop=True)
lincoln_daily_wide = lincoln_daily.pivot(index='ReadingDate',columns='ICP',values='kWh').reset_index().rename_axis(None,axis=1)
lincoln_daily_wide['Total'] = lincoln_daily_wide['RN355']+lincoln_daily_wide['RN405']+lincoln_daily_wide['RN897']


lincoln_df_wide = pd.pivot(lincoln_df, index=['ReadingDate','ReadingTime'], columns='ICP',
        values='kWh').reset_index().rename_axis(None,axis=1)
lincoln_df_wide['Total'] = lincoln_df_wide['RN355']+lincoln_df_wide['RN405']+lincoln_df_wide['RN897']

def main_chart():
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=lincoln_daily_wide['ReadingDate'], y=lincoln_daily_wide['RN355'], name='RN355',
            hoverinfo='x+y',
            mode='lines',
            line=dict(width=0.5, color='rgba(82,139,139,1)'),
            stackgroup='one',
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Scatter(x=lincoln_daily_wide['ReadingDate'], y=lincoln_daily_wide['RN405'], name='RN405',
            hoverinfo='x+y',
            mode='lines',
            stackgroup='one',
            line=dict(width=0.5, color='rgba(110,139,61,1)'),
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Scatter(x=lincoln_daily_wide['ReadingDate'], y=lincoln_daily_wide['RN897'], name='RN897',
            hoverinfo='x+y',
            mode='lines',
            stackgroup='one',
            line=dict(width=0.5, color='rgba(105,105,105,1)'),
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Scatter(x=lincoln_daily_wide['ReadingDate'], y=lincoln_daily_wide['Total'], name='Total',
            marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
            mode="markers",
            showlegend=False,
            hovertemplate = '%{y:,.2f} kWh'),
    )

    # Add figure layout
    fig.update_layout(title_text= 'Daily Electricity Consumption year 2022 (kWh)',
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        # barmode = 'stack',
        margin = dict(r=20),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1)
        )
    fig.update_yaxes(title='Consumption(kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_xaxes(showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')

    return fig

def group_charts(df,clk_date):
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(x=df['ReadingTime'], y=df['RN355'], name='RN355',
            marker=dict(color='rgba(82,139,139,0.8)',line = dict(width=0)),
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Bar(x=df['ReadingTime'], y=df['RN405'], name='RN405',
            marker=dict(color='rgba(110,139,61,0.8)',line = dict(width=0)),
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Bar(x=df['ReadingTime'], y=df['RN897'], name='RN897',
            marker=dict(color='rgba(105,105,105,0.8)',line = dict(width=0)),
            hovertemplate = '%{y:,.2f} kWh'),
    )

    fig.add_trace(
        go.Scatter(x=df['ReadingTime'], y=df['Total'], name='Total',
            marker=dict(size=0, symbol='line-ew', line=dict(width=0.0, color='#FFFFFF')),
            mode="markers",
            showlegend=False,
            hovertemplate = '%{y:,.2f} kWh'),
    )

    # Add figure layout
    fig.update_layout(title_text= (f'Electricity Consumption on {clk_date}'),
        hovermode="x unified",
        plot_bgcolor='#FFFFFF',
        barmode = 'stack',
        margin = dict(r=20),
        xaxis = dict(tickmode = 'linear',dtick = 'M1'),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1)
        )
    fig.update_yaxes(title='Consumption(kWh)',showgrid=True, gridwidth=1, gridcolor='#f0f0f0',
                 title_font_size=12,tickfont=dict(size=12)
                 )
    fig.update_xaxes(tickangle= -45, showgrid=False, gridwidth=1, title_font_size=12,tickfont=dict(size=12), dtick='M1')

    return fig

app = Dash(__name__)
server = app.server

app.layout = dbc.Container([
    html.H2("Lincoln University Electricity Consumption", style={'font-family':'arial','textAlign':'center'}),
    html.Br(),html.Br(),
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='overview-graph', figure=main_chart())),
            ),
    ]),
    html.Br(),
    dbc.Row([  
        dcc.Loading(id='detail_loading',children=
            [dbc.Card(dcc.Graph(id='detail-graph', figure={}, clickData=None, 
                hoverData=None)
            )],
            type = 'default',
        )
    ]),
])


@app.callback(
    Output(component_id='detail-graph', component_property='figure'),
    Input(component_id='overview-graph', component_property='clickData')
)
def update_group_charts(clk_data):
    if clk_data is None:
        default = '2022-01-01'
        clk_date = default
        df2 = lincoln_df_wide[lincoln_df_wide['ReadingDate'] == clk_date]

        fig2 = group_charts(df2,clk_date)

        return fig2
    else:

        clk_date = clk_data['points'][0]['x']
        df2 = lincoln_df_wide[lincoln_df_wide['ReadingDate'] == clk_date]

        fig2 = group_charts(df2,clk_date)

        return fig2        


app.run_server(debug=False)