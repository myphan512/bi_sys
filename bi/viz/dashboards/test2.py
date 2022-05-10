from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

app = DjangoDash(name='test2', external_stylesheets=[dbc.themes.BOOTSTRAP])

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

# Filters
default_start = date.today() - timedelta(days=8)
default_end = date.today() - timedelta(days=1)
filters = dbc.Row(
    [
        html.H4("Filters", style={'margin-bottom':'1rem', 'margin-top':'1rem'}),
        dbc.Row([
                dbc.Label("Date Range", style={'font-weight':'bold'}),
                dcc.DatePickerRange(id='filter_date', max_date_allowed=date.today(),
                                    start_date=default_start, end_date=default_end,
                                    start_date_placeholder_text="Start Date",
                                    end_date_placeholder_text="End Date")
            ], style={'margin-bottom':'1rem'}),
        dbc.Row([
                dbc.Label("Projects", style={'font-weight':'bold'}),
                dcc.Dropdown(options=[123,456,789,321,654,987],
                             placeholder="Select Projects",
                             multi=True, id='filter_project')
            ], style={'margin-bottom':'1rem'}),
        dbc.Row(
            [
                dbc.Label("Payment Systems", style={'font-weight':'bold'}),
                dcc.Dropdown(options=[1,2,3,4,5,6,7,8,9],
                             multi=True,
                             id='filter_ps')
            ], style={'margin-bottom':'1rem'}),
        dbc.Row(
            [
                dbc.Label("Click Countries", style={'font-weight':'bold'}),
                dcc.Dropdown(options=['US','CA','VN'],
                             placeholder="Select Click Countries",
                             multi=True, id='filter_co')
            ], style={'margin-bottom':'1rem'}),

        dbc.Button("Apply", id="apply_filters", n_clicks=0, style={'float': 'right'}),
    ]
)

dropdown_options = [
                        {'label': 'New York City', 'value': 'NYC'},
                        {'label': 'Montréal', 'value': 'MTL'},
                        {'label': 'San Francisco', 'value': 'SF'}
                    ]

#################################################################################
################################################ LAYOUT
app.layout = html.Div([
    html.Div([
        html.H1("Test Dashboard", style={'font-family':'Arial', 'font-weight':'bold', 'padding-left':'1rem', 'margin':'0px'}),
        html.Hr(),
    ], style={'margin':'0rem',}),


    

    dbc.Row([
        ### FILTERS
        dbc.Col([
            html.H4("Filters", style={'margin-left':'0.5rem'}),
            html.Div([
                html.Div([
                    dbc.Label("Date Range", style={'font-weight':'bold'}),
                    dcc.DatePickerRange(id='filter_date', max_date_allowed=date.today(),
                                        start_date=default_start, end_date=default_end,
                                        start_date_placeholder_text="Start Date", end_date_placeholder_text="End Date",)
                ], style={'margin':'0.5rem'}),
                html.Div([
                    dbc.Label("Projects", style={'font-weight':'bold'}),
                    dcc.Dropdown(options=dropdown_options,
                                placeholder="Select Projects", multi=True, id='filter_project', 
                                style={'width':'100%', 'font-family':'Arial'})
                ], style={'margin':'0.5rem'}),
                html.Div(
                    [
                        dbc.Label("Payment Systems", style={'font-weight':'bold'}),
                        dcc.Dropdown(options=dropdown_options,
                                    multi=True,
                                    id='filter_ps')
                    ], style={'margin':'0.5rem'}),
                html.Div(
                    [
                        dbc.Label("Click Countries", style={'font-weight':'bold'}),
                        dcc.Dropdown(options=dropdown_options,
                                    placeholder="Select Click Countries",
                                    multi=True, id='filter_co')
                    ], style={'margin':'0.5rem'}),
            ], style={'margin':'0.5rem'}),
            dbc.Button("Apply", id="apply_filters", n_clicks=0, style={'float': 'right', 'margin':'1rem'}),
        ], width=3, style={'box-shadow':'0px 1px 3px lightgrey', 'background-color':'#F9F9F9', 'margin':'1rem'}),

        ### 1st CHART
        dbc.Col([html.H4("Fi1"), dcc.Graph(id='fig1', figure=fig1)]),
    ]),




    dbc.Row([
            dbc.Col([html.H4("Fig2"), dcc.Graph(id='fig2', figure=fig2)], width=4, style={'padding': '5rem'}),
            dbc.Col([html.H4("Fig3"), dcc.Graph(id='fig3', figure=fig3)], width=4, style={'padding': '5rem'}),
            dbc.Col([html.H4("Fig4"), dcc.Graph(id='fig4', figure=fig2)], width=4, style={'padding': '5rem'}),
    ],align='center',justify="evenly"),
], style={'overflow-x':'hidden', 'background-color':'#F2F2F2'})