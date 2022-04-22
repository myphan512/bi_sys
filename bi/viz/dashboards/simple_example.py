import plotly.express as px
import plotly.graph_objects as go
from dash import dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash

############ REGISTER APP
app = DjangoDash(name='SimpleExample', external_stylesheets=[dbc.themes.ZEPHYR])


############ CODE
## 1.
df = px.data.gapminder()
fig1 = px.scatter(df.query("year==2007"), x="gdpPercap", y="lifeExp",
	         size="pop", color="continent",
                 hover_name="country", log_x=True, size_max=60)
fig1.update_layout(plot_bgcolor="white")

## 2.
data_canada = px.data.gapminder().query("country == 'Canada'")
fig2 = px.bar(data_canada, x='year', y='pop')
fig2.update_layout(plot_bgcolor="white")

## 3.
labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
values = [4500, 2500, 1053, 500]
fig3 = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0])])

## 4.
table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("Astra")])

table_body = [html.Tbody([row1, row2, row3, row4])]


############ LAYOUT
app.layout = html.Div([
    dcc.Graph(id='fig1',figure=fig1),
    dcc.Graph(id='fig2',figure=fig2),
    dcc.Graph(id='fig3',figure=fig3),
    dbc.Table(table_header + table_body, bordered=False, size="sm"),
    dbc.CardHeader(
        dbc.Tabs([dbc.Tab(label="Tab 1", tab_id="tab-1"), dbc.Tab(label="Tab 2", tab_id="tab-2")], id="card-tabs",active_tab="tab-1",)
    ),
    dbc.CardBody(html.P(id="card-content", className="card-text")),
])


############ CALLBACK
@app.callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    return "This is tab {}".format(active_tab)