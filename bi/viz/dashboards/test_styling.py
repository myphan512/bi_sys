from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import datetime


######### CREATE DJANGO DASH APP
app = DjangoDash(name='test_styling', external_stylesheets=[dbc.themes.BOOTSTRAP])


#################################################################################
################################################ CHARTS
## 1.
df = px.data.gapminder()
fig1 = px.scatter(df.query("year==2007"), x="gdpPercap", y="lifeExp",
	         size="pop", color="continent",
                 hover_name="country", log_x=True, size_max=60)
fig1.update_layout(plot_bgcolor="white", paper_bgcolor='white',
                   margin=dict(l=20, r=20, t=0, b=0))

## 2.
data_canada = px.data.gapminder().query("country == 'Canada'")
fig2 = px.bar(data_canada, x='year', y='pop')
fig2.update_layout(plot_bgcolor="white", paper_bgcolor='white',
                   margin=dict(l=20, r=20, t=0, b=0))

## 3.
labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
values = [4500, 2500, 1053, 500]
fig3 = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0])])
fig3.update_layout(plot_bgcolor="white", paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=0, b=0))


# F7F9F9
#################################################################################
################################################ LAYOUT
app.layout = html.Div([
    dbc.Row([
        html.H1("Testing Styling", style={'font-family':'Arial', 'font-weight':'bold'}),
        html.Hr(),
    ], className='row', style={'padding-left': '2rem', 'padding-right':'2rem', 'padding-top':'1rem', 'padding-bottom':'1rem'}),
    dbc.Row([
            html.H4("Sample Chart", style={'font-family':'Arial', 'font-weight':'bold', 'padding-top':'1rem', 'padding-left':'1rem', 'padding-right':'1rem'}),
            dcc.Graph(id='chart1', figure=fig1, style={'padding-top':'1rem', 'padding-left':'1rem', 'padding-right':'1rem', 'padding-bottom':'1rem'})
    ],style={'background-color':'white' ,'margin-left':'3rem', 'margin-right':'3rem',
             'box-shadow':'2px 2px 2px lightgrey'}),
    dbc.Row([
            dbc.Col([html.H4("Fig2"), dcc.Graph(id='fig2', figure=fig2)], width=4, style={'padding': '5rem'}),
            dbc.Col([html.H4("Fig3"), dcc.Graph(id='fig3', figure=fig3)], width=4, style={'padding': '5rem'}),
            dbc.Col([html.H4("Fig4"), dcc.Graph(id='fig4', figure=fig2)], width=4, style={'padding': '5rem'}),
    ],align='center',justify="evenly"),
], style={'background-color':'#eaeaea', 'overflow-x':'hidden', 'overflow-y':'hidden'})