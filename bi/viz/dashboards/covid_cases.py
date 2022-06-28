from django_plotly_dash import DjangoDash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from .dash_functions import *


app = DjangoDash(name='covid_cases', external_stylesheets=[dbc.themes.BOOTSTRAP])

""" Get COVID data cases from github repo https://github.com/owid/covid-19-data/tree/master/public/data/
- Extract columns used for report only
- Process NaN values
"""
data = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv',sep=',')
df = data[['iso_code','continent','location','date','total_cases','new_cases','total_deaths','new_deaths',
           'total_vaccinations','people_vaccinated','people_fully_vaccinated','population','population_density','gdp_per_capita']]
df.fillna(0)
continents_data = df[df["iso_code"].str.len()>3]
countries_data = df[df["iso_code"].str.len()==3]



""" Function to draw charts
1. Total Cases big number
2. Total Deaths big number
3. Daily Cases trendline
4. Daily Deaths trendline
5. Total cases by countries
6. Daily cases by top 10 countries
7. Daily deaths by top 10 countries
"""
### 1. Total Cases big number
def total_cases(df):
    total_cases = df['new_cases'].sum()
    fig = go.Figure(go.Indicator(
        mode = "number",
        value = total_cases,
        # number = {'valueformat':'f'},
        title = {"text": "Accumulated Cases<br><span style='font-size:1em;color:gray'><br>as of {}</span>".format(max(df['date']))},
        ))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20),)
    return fig


### 2. Total Deaths big number
def total_deaths(df):
    total_deaths = df['new_deaths'].sum()
    fig = go.Figure(go.Indicator(
        mode = "number",
        value = total_deaths,
        # number = {'valueformat':'f'},
        title = {"text": "Accumulated Deaths<br><span style='font-size:1em;color:gray'><br>as of {}</span>".format(max(df['date']))},
        ))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=20, b=20),)
    return fig


### 3. Daily Cases trendline
def daily_cases(df):
    daily_cases = df.groupby("date").agg(cases=pd.NamedAgg(column="new_cases", aggfunc="sum")).reset_index()

    fig = go.Figure(go.Indicator(
        mode = "number+delta",
        value = daily_cases.sort_values(by="date",ascending=False).iloc[0,1],
        delta = {"reference": daily_cases.sort_values(by="date",ascending=False).iloc[1,1]},
        title = {"text": "#Cases on {}".format(max(daily_cases["date"]))},
        ))

    fig.add_trace(go.Scatter(
        x=daily_cases["date"], y=daily_cases["cases"], name=""
        ))

    fig.update_layout(
        xaxis=dict(title="Date", tickformat="%Y-%m-%d"),
        yaxis=dict(title="#Cases"),
        plot_bgcolor='rgba(0,0,0,0)', hovermode="x",
        margin=dict(l=20, r=20, t=20, b=20),
        )

    return fig

### 4. Daily Deaths trendline
def daily_deaths(df):
    daily_deaths = df.groupby("date").agg(deaths=pd.NamedAgg(column="new_deaths", aggfunc="sum")).reset_index()

    fig = go.Figure(go.Indicator(
        mode = "number+delta",
        value = daily_deaths.sort_values(by="date",ascending=False).iloc[0,1],
        delta = {"reference": daily_deaths.sort_values(by="date",ascending=False).iloc[1,1]},
        title = {"text": "#Deaths on {}".format(max(daily_deaths["date"]))},
        ))

    fig.add_trace(go.Scatter(
        x=daily_deaths["date"], y=daily_deaths["deaths"], name=""
        ))

    fig.update_layout(
        xaxis=dict(title="Date", tickformat="%Y-%m-%d"),
        yaxis=dict(title="#Deaths"),
        plot_bgcolor='rgba(0,0,0,0)', hovermode="x",
        margin=dict(l=20, r=20, t=20, b=20),
        )

    return fig


### 5. Total cases by countries
def total_cases_by_countries(df):
    total_cases_by_countries = pd.DataFrame(countries_data.groupby(['location','iso_code']).agg(cases=pd.NamedAgg(column="new_cases", aggfunc="sum")).reset_index())
    total_cases_by_countries["color_range"] = total_cases_by_countries["cases"]/max(total_cases_by_countries["cases"])

    total_cases_by_countries['text'] = total_cases_by_countries['location'] + '<br>' + total_cases_by_countries["cases"].map('{:,.0f}'.format)  # hover text

    fig = px.choropleth(
        locations=total_cases_by_countries['iso_code'],  # Spatial coordinates
        color=total_cases_by_countries['color_range'],  # Data to be color-coded
        color_continuous_scale='Reds',
    )

    fig.update_coloraxes(showscale=False)
    fig.update_traces(hovertemplate=total_cases_by_countries['text'])
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', autosize=True, dragmode=False)
    fig.update_geos(fitbounds="locations", visible=False, showcountries=True, showcoastlines=True, showland=True)

    return fig


### 6. Daily cases by top 10 countries
def daily_cases_by_countries(df):
    top10 = pd.DataFrame(df.groupby('location').agg(cases=pd.NamedAgg(column="new_cases", aggfunc="sum")).reset_index().sort_values(by="cases",ascending=False)).head(10)
    daily_cases_by_countries = df[df['location'].isin(top10['location'])]
    fig = px.line(daily_cases_by_countries, x="date", y="new_cases", color="location", line_group="location")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', hovermode="x", legend_title_text="Countries",
                      xaxis=dict(title='Date', tickformat='%Y-%m-%d'),
                      yaxis={'title': "#Cases", 'rangemode': "tozero"},
                      legend={'orientation': "h", 'yanchor': "bottom", 'y': 1.02, 'xanchor': "right", 'x': 1},
                      hoverlabel_namelength=-1)
    return fig


### 7. Daily deaths by top 10 countries
def daily_deaths_by_countries(df):
    top10 = pd.DataFrame(df.groupby('location').agg(deaths=pd.NamedAgg(column="new_deaths", aggfunc="sum")).reset_index().sort_values(by="deaths",ascending=False)).head(10)
    daily_deaths_by_countries = df[df['location'].isin(top10['location'])]
    fig = px.line(daily_deaths_by_countries, x="date", y="new_deaths", color="location", line_group="location")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', hovermode="x", legend_title_text="Countries",
                      xaxis=dict(title='Date', tickformat='%Y-%m-%d'),
                      yaxis={'title': "#Deaths", 'rangemode': "tozero"},
                      legend={'orientation': "h", 'yanchor': "bottom", 'y': 1.02, 'xanchor': "right", 'x': 1},
                      hoverlabel_namelength=-1)
    return fig


######################################################################################
""" APP LAYOUT
"""
app.layout = html.Div([
    html.H2("COVID-19 Cases", style={'padding': '20px', 'padding-bottom': '10px'}),
    html.Div([
        html.Div([dcc.Graph(id="total_cases", figure=total_cases(countries_data))], style={'flex': '20%'}),
        html.Div([dcc.Graph(id="total_deaths", figure=total_deaths(countries_data))], style={'flex': '20%'}),
        html.Div([dcc.Graph(id="daily_cases", figure=daily_cases(countries_data))], style={'flex': '20%'}),
        html.Div([dcc.Graph(id="daily_deaths", figure=daily_deaths(countries_data))], style={'flex': '20%'}),
    ],style={'display': 'flex', 'flex-wrap': 'wrap', 'margin': '10px', 'box-shadow': '0px 1px 3px lightgrey','border-radius': '10px'}),

    html.Div([
        html.H4("Accumulated Cases Worldwide", style={'padding': '20px', 'padding-bottom': '0px'}),
        dcc.Graph(id="total_cases_by_countries", figure=total_cases_by_countries(countries_data))
    ],style={'margin': '10px', 'box-shadow': '0px 1px 3px lightgrey','border-radius': '10px'}),

    html.Div([
        html.Div([
            html.H4("Daily Cases", style={'padding': '20px', 'padding-bottom': '0px'}),
            dcc.Graph(id="daily_cases_by_countries", figure=daily_cases_by_countries(countries_data))
        ], style={'flex': '40%'}),
        html.Div([
            html.H4("Daily Deaths", style={'padding': '20px', 'padding-bottom': '0px'}),
            dcc.Graph(id="daily_deaths_by_countries", figure=daily_deaths_by_countries(countries_data))
        ], style={'flex': '40%'})
    ],style={'display': 'flex', 'flex-wrap': 'wrap', 'margin': '10px', 'box-shadow': '0px 1px 3px lightgrey','border-radius': '10px'})
])