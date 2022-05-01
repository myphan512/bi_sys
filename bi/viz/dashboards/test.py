from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import dash_table
import dash_bootstrap_components as dbc
from datetime import date, timedelta
from ..connect_db import runQuery_tidb
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

app = DjangoDash(name='test', external_stylesheets=[dbc.themes.BOOTSTRAP])

### Design
# 1.
table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("Astra")])

table_body = [html.Tbody([row1, row2, row3, row4])]

# 2.
df2 = px.data.gapminder()

fig2 = px.scatter(df2.query("year==2007"), x="gdpPercap", y="lifeExp",size="pop", color="continent",hover_name="country", log_x=True, size_max=60)
fig2.update_layout(plot_bgcolor='white')
fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                   legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
                   )

# 3.
df3 = px.data.gapminder().query("year==2007")
fig3 = px.choropleth(df3, locations="iso_alpha",
                    color="lifeExp", # lifeExp is a column of gapminder
                    hover_name="country", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma,
                     )
fig3.update_coloraxes(showscale=False)
fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0), autosize=False)
fig3.update_geos(fitbounds="locations", visible=False)

# 4.
df4 = pd.DataFrame({
  "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
  "Contestant": ["Alex", "Alex", "Alex", "Jordan", "Jordan", "Jordan"],
  "Number Eaten": [2, 1, 3, 1, 3, 2],
})
fig4 = px.bar(df4, x="Fruit", y="Number Eaten", color="Contestant", barmode="group")
fig4.update_layout(plot_bgcolor='white')
fig4.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                   legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
                   )



### Layout
app.layout = html.Div(
    [
        dbc.Row(dbc.Col(html.Div(dbc.Table(table_header + table_body, bordered=False)))),


        dbc.Row([
            dbc.Col(dbc.Row([html.H4("Bubble chart"), dcc.Graph(id='fig2',figure=fig2)]) ,md=4),
            dbc.Col(dbc.Row([html.H4("Map chart"), dcc.Graph(id='fig3',figure=fig3)]) ,md=4),
            dbc.Col(dbc.Row([html.H4("Bar chart"), dcc.Graph(id='fig4',figure=fig4)]) ,md=4),
        ])
    ]
)

