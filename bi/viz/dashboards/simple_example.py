import plotly.express as px
import plotly.graph_objects as go
from dash import dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import pandas as pd
from sklearn import datasets
from sklearn.cluster import KMeans


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


## 5.
iris_raw = datasets.load_iris()
iris = pd.DataFrame(iris_raw["data"], columns=iris_raw["feature_names"])

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in iris.columns
                    ],
                    value="sepal length (cm)",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Y variable"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[
                        {"label": col, "value": col} for col in iris.columns
                    ],
                    value="sepal width (cm)",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Cluster count"),
                dbc.Input(id="cluster-count", type="number", value=3),
            ]
        ),
    ],
    body=True,
)

############ LAYOUT
app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.Div(dcc.Graph(id='fig1',figure=fig1))),
        dbc.Col(html.Div(dcc.Graph(id='fig2',figure=fig2))),
        dbc.Col(html.Div(dcc.Graph(id='fig3',figure=fig3))),
    ]),
    dbc.Table(table_header + table_body, size="sm", striped=True, bordered=True, hover=True),
    dbc.CardHeader(
        dbc.Tabs([dbc.Tab(label="Tab 1", tab_id="tab-1"), dbc.Tab(label="Tab 2", tab_id="tab-2")], id="card-tabs",active_tab="tab-1",)
    ),
    dbc.CardBody(html.P(id="card-content", className="card-text")),
    dbc.Container(
        [
            html.H1("Iris k-means clustering"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(controls, md=3),
                    dbc.Col(dcc.Graph(id="cluster-graph"), md=9),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dbc.Tabs
        (
            [
                dbc.Tab(label="Scatter", tab_id="scatter"),
                dbc.Tab(label="Histograms", tab_id="histogram"),
            ],
            id="tabs",
            active_tab="scatter",
        ),
    html.Div(id="tab-content", className="p-4"),
])


############ CALLBACK
@app.callback(
    Output("card-content", "children"), [Input("card-tabs", "active_tab")]
)
def tab_content(active_tab):
    return "This is tab {}".format(active_tab)


@app.callback(
    Output("cluster-graph", "figure"),
    [
        Input("x-variable", "value"),
        Input("y-variable", "value"),
        Input("cluster-count", "value"),
    ],
)
def make_graph(x, y, n_clusters):
    # minimal input validation, make sure there's at least one cluster
    km = KMeans(n_clusters=max(n_clusters, 1))
    df = iris.loc[:, [x, y]]
    km.fit(df.values)
    df["cluster"] = km.labels_

    centers = km.cluster_centers_

    data = [
        go.Scatter(
            x=df.loc[df.cluster == c, x],
            y=df.loc[df.cluster == c, y],
            mode="markers",
            marker={"size": 8},
            name="Cluster {}".format(c),
        )
        for c in range(n_clusters)
    ]

    data.append(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode="markers",
            marker={"color": "#000", "size": 12, "symbol": "diamond"},
            name="Cluster centers",
        )
    )

    layout = {"xaxis": {"title": x}, "yaxis": {"title": y}}

    return go.Figure(data=data, layout=layout)


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option v"""
    return [
        {"label": col, "value": col, "disabled": col == v}
        for col in iris.columns
    ]


# functionality is the same for both dropdowns, so we reuse filter_options
app.callback(Output("x-variable", "options"), [Input("y-variable", "value")])(
    filter_options
)
app.callback(Output("y-variable", "options"), [Input("x-variable", "value")])(
    filter_options
)

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab:
        if active_tab == "scatter":
            return dcc.Graph(figure=fig3)
        elif active_tab == "histogram":
            return dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=fig1), width=6),
                    dbc.Col(dcc.Graph(figure=fig2), width=6),
                ]
            )
    return "No tab selected"