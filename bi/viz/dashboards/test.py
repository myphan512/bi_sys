from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import time

app = DjangoDash(name='test', external_stylesheets=[dbc.themes.DARKLY])

### Design
table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("Astra")])

table_body = [html.Tbody([row1, row2, row3, row4])]


### Layout
app.layout = html.Div([
    dbc.Table(table_header + table_body, bordered=True)
])