import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import inspect
import os
import sys

# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)

from ..connect_db import runQuery_tidb

######### CREATE DJANGO DASH APP
app = DjangoDash(name='pw_performance', external_stylesheets=[dbc.themes.ZEPHYR])

#################################################################################
################################################
default_start = date.today() - timedelta(days=8)
default_end = date.today() - timedelta(days=1)

### function to run query
def get_raw_data(start, end):
    data = runQuery_tidb(f"""
    SELECT
    DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(psc.cl_date_clicked), 'GMT', 'US/Central'), '%Y-%m-%d') AS datecl,

    psc.a_id AS project_id, a.a_name AS project_name, CONCAT('[',psc.a_id,'] ',a.a_name) AS project,
    a.d_id AS merchant_id, d.d_company AS merchant_name, CONCAT('[',a.d_id,'] ',d.d_company) AS merchant,
    psc.ps_id, ps.ps, psc.pss_id, CASE WHEN psc.pss_id=0 OR psc.pss_id IS NULL THEN 'Unknown' ELSE pss.pss END AS pss,
    psc.co_id, co.co_code_alpha3, co.co_name,

    round(SUM(psc.cl_revenue_xe * (a.d_id != 162784) * (psc.ps_id NOT IN (45, 288)) * (psc.pss_id NOT IN (80)
    OR psc.pss_id IS null) * (psc.cl_refunded = 0)* ((cl_recurring_type != 'repeat') * (cl_recurring_type != 'post_trial'))), 2) AS PV,

    round(SUM(if((a.a_custom_settings RLIKE 'vat'
    AND a.a_custom_settings RLIKE 'mor')
    AND d.d_rolling_reserve_payable=1, (psc.cl_commission_xe-psc.cl_user_commission_xe)-IFNULL((tt_tax_amount/cu.cu_rate),tt_tax_amount), IF((a.a_custom_settings RLIKE 'vat'
    AND a.a_custom_settings RLIKE 'mor')
    AND d.d_rolling_reserve_payable=0, (cl_gross_margin_xe-cl_user_commission_xe) - IFNULL((tt_tax_amount/cu.cu_rate),tt_tax_amount), IF(d.d_rolling_reserve_payable=1, (cl_commission_xe-cl_user_commission_xe), (cl_gross_margin_xe-cl_user_commission_xe))))), 2) AS rev

    FROM 
    (
        SELECT * FROM ti_paymentwall.ps_clicks 
        WHERE cl_date_clicked >= UNIX_TIMESTAMP(CONVERT_TZ('{start}', 'US/Central', 'GMT'))
        AND cl_date_clicked < UNIX_TIMESTAMP(CONVERT_TZ('{end}' + INTERVAL 1 DAY, 'US/Central', 'GMT'))
        AND cl_tracked = 1 AND cl_approved = 1 AND cl_fraud = 0
        AND (pss_id NOT IN (69) OR pss_id IS NULL)
    ) psc

    INNER JOIN 
    (
        SELECT * FROM ti_paymentwall.applications
        WHERE a_internal_usage != 1
    ) a ON psc.a_id = a.a_id

    INNER JOIN 
    (
        SELECT * FROM ti_paymentwall.developers
    ) d ON a.d_id = d.d_id

    LEFT JOIN 
    (
        SELECT pss_id, CONCAT('[',pss_id,'] ',pss_name) AS pss FROM ti_paymentwall.ps_subaccounts
    ) pss ON psc.pss_id = pss.pss_id

    INNER JOIN 
    (
        SELECT ps_id, CONCAT('[',ps_id,'] ',ps_name) AS ps FROM ti_paymentwall.payment_systems 
    ) ps ON psc.ps_id = ps.ps_id

    INNER JOIN 
    (
        SELECT co_id, co_code_alpha3, co_name FROM ti_paymentwall.countries 
    ) co ON psc.co_id = co.co_id

    LEFT JOIN ti_paymentwall.taxable_transactions tt ON psc.cl_id = tt.cl_id
    LEFT JOIN ti_paymentwall.currencies cu on psc.cu_id = cu.cu_id

    GROUP BY datecl, psc.a_id, a.a_name, project, a.d_id, d.d_company, merchant, psc.ps_id, ps.ps, psc.pss_id, pss.pss, psc.co_id, co.co_code_alpha3, co.co_name
    """)

    return data

### function to apply filters
def apply_filters(start_date, end_date, project_list, ps_list, co_list):
    global data
    if start_date < min(data['datecl']) or end_date > max(data['datecl']):
        print("Running Again")
        data = get_raw_data(start_date,end_date)
        print(data['datecl'].unique())
        df = data
    else:
        df = data[(data['datecl']>=start_date) & (data['datecl']<=end_date)]
    df = df if not project_list else df[df['project'].isin(project_list)]
    df = df if not ps_list else df[df['ps'].isin(ps_list)]
    df = df if not co_list else df[df['co_name'].isin(co_list)]
    return df

### prepare default data
data = get_raw_data(default_start, default_end)

#################################################################################
################################################ GRAPHS
### GRAPH DAILY REV AND PV
def graph_daily_rev_PV(df):
    by_dates = pd.DataFrame(df.groupby('datecl').agg(rev=pd.NamedAgg(column="rev", aggfunc="sum"),
                                                       PV=pd.NamedAgg(column="PV", aggfunc="sum")
                                                       ).reset_index())

    by_dates_graph = make_subplots(specs=[[{"secondary_y": True}]])
    by_dates_graph.add_trace(go.Bar(x=by_dates['datecl'], y=by_dates['PV'], name="Processing Volume ($)"),
                             secondary_y=False)
    by_dates_graph.add_trace(go.Scatter(x=by_dates['datecl'], y=by_dates['rev'], name="Revenue ($)"),
                             secondary_y=True)
    by_dates_graph.update_layout(xaxis={'title':'Date'},
                                 plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20))
    by_dates_graph.update_yaxes(title_text="Processing Volume", rangemode="tozero", tickformat="$,", secondary_y=False)
    by_dates_graph.update_yaxes(title_text="Revenue", rangemode="tozero", tickformat="$,", secondary_y=True)
    return by_dates_graph

### GRAPH PROJECT DISTRIBUTION OVERTIME
def graph_project_distribution(df):
    by_projects = df
    by_projects['project_id_str'] = '[' + by_projects['project_id'].astype(str) + ']'
    by_projects = pd.DataFrame(by_projects.groupby(['project','project_id_str']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index())
    by_projects_graph = px.pie(by_projects, values='PV', names='project')
    by_projects_graph.update_traces(direction='clockwise', text=by_projects['project_id_str'], textposition='inside', textinfo='text+percent',
                                    hovertemplate=None, hoverinfo="label+value+percent")
    by_projects_graph.update_layout(uniformtext_minsize=11, uniformtext_mode='hide', showlegend=False, #, legend_title_text="Project", title_text="Projects' Contribution to Total Volume",
                                    margin=dict(l=20, r=20, t=20, b=20))
    return by_projects_graph

### GRAPH TOP PROJECT DAILY PV
def graph_top_project_daily_PV(df):
    by_projects = pd.DataFrame(
        df.groupby(['project', 'datecl']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index())
    top10 = pd.DataFrame(
        df.groupby(['project']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index()).sort_values(by="PV",
                                                                                                           ascending=False).head(
        10)
    by_projects = by_projects[by_projects['project'].isin(top10['project'])]

    by_projects_graph = px.area(by_projects, x="datecl", y="PV", color="project", line_group="project")
    by_projects_graph.update_traces(hovertemplate=None)
    by_projects_graph.update_layout(plot_bgcolor='white', hovermode="x", legend_title_text="Project",
                                    xaxis={'title': 'Date'},
                                    yaxis={'title': "Processing Volume", 'rangemode': "tozero", 'tickformat': "$,"})

    return by_projects_graph

### GRAPH PS DISTRIBUTION OVERTIME
def graph_ps_distribution(df):
    by_ps = pd.DataFrame(df.groupby(['ps','pss']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index())
    by_ps_graph = px.treemap(by_ps, path=[px.Constant("TOTAL"),'ps', 'pss'], values='PV', color='ps' #,title="Payment Systems' Contribution to Total Volume"
                            )
    by_ps_graph.update_traces(hovertemplate=None, hoverinfo="label+value+percent root+percent entry+percent parent")
    by_ps_graph.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    return by_ps_graph

### GRAPH PS DAILY PV
def graph_top_ps_daily_PV(df):
    by_ps = pd.DataFrame(df.groupby(['ps', 'datecl']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index())
    top10 = pd.DataFrame(df.groupby(['ps']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index()).sort_values(
        by="PV", ascending=False).head(10)
    by_ps = by_ps[by_ps['ps'].isin(top10['ps'])]

    by_ps_graph = px.area(by_ps, x="datecl", y="PV", color="ps", line_group="ps")
    by_ps_graph.update_traces(hovertemplate=None)
    by_ps_graph.update_layout(plot_bgcolor='white', hovermode="x", legend_title_text="Payment System",
                              xaxis={'title': 'Date'},
                              yaxis={'title': "Processing Volume", 'rangemode': "tozero", 'tickformat': "$,"})

    return by_ps_graph

### GRAPH COUNTRY DISTRIBUTION OVERTIME
def graph_countries_distribution(df):
    by_countries = pd.DataFrame(
        df.groupby(['co_name', 'co_code_alpha3']).agg(PV=pd.NamedAgg(column="PV", aggfunc="sum")).reset_index())
    by_countries['PV'] = by_countries['PV'].astype(float)
    by_countries['text'] = by_countries['co_name'] + '<br>' + by_countries["PV"].map('{:,.2f}'.format)  # hover text

    graph_countries_distribution = px.choropleth(
        locations=by_countries['co_code_alpha3'],  # Spatial coordinates
        color=by_countries['PV'],  # Data to be color-coded
        color_continuous_scale=[(0.0, "#e5e5e5"), (0.0001, "#e5e5e5"),
                                (0.0001, "#ffe5f0"), (0.0075, "#ffe5f0"),
                                (0.0075, "#facfdf"), (0.01, "#facfdf"),
                                (0.01, "#f3b8ce"), (0.025, "#f3b8ce"),
                                (0.025, "#eca2bf"), (0.05, "#eca2bf"),
                                (0.05, "#e37fb1"), (1, "#e37fb1")
                                ]
    )
    graph_countries_distribution.update_coloraxes(showscale=False)
    graph_countries_distribution.update_traces(hovertemplate=by_countries['text'])
    graph_countries_distribution.update_layout(margin={"r": 20, "t": 20, "l": 20, "b": 20}, autosize=False)
    graph_countries_distribution.update_geos(fitbounds="locations", visible=False)

    return graph_countries_distribution

### PIVOT PROJECT DAILY PV
def pivot_project_daily_PV(df):
    project_daily_PV = pd.pivot_table(df, values='PV', index=['project'], columns=['datecl'], aggfunc=np.sum).reset_index()
    project_daily_PV['total'] = project_daily_PV.iloc[:,1:].sum(axis=1)
    project_daily_PV = project_daily_PV.sort_values(by="total", ascending=False)
    project_daily_PV.rename(columns={'project':'Project', 'total':'Total Volume for the Period ($)'}, inplace = True)
    return project_daily_PV

### PIVOT PS DAILY PV
def pivot_ps_daily_PV(df):
    ps_daily_PV = pd.pivot_table(df, values='PV', index=['ps'], columns=['datecl'], aggfunc=np.sum).reset_index()
    ps_daily_PV['total'] = ps_daily_PV.iloc[:,1:].sum(axis=1)
    ps_daily_PV = ps_daily_PV.sort_values(by="total", ascending=False)
    ps_daily_PV.rename(columns={'ps':'Payment System', 'total':'Total Volume for the Period ($)'}, inplace=True)
    return ps_daily_PV

#################################################################################
################################################ APP DASH
### FILTERS
filters = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Date Range"),
                dcc.DatePickerRange(id='filter_date', max_date_allowed=date.today(),
                                    start_date=default_start, end_date=default_end,
                                    start_date_placeholder_text="Start Date",
                                    end_date_placeholder_text="End Date")
            ]
        ),
        html.Div(
            [
                dbc.Label("Projects"),
                dcc.Dropdown(options=data.sort_values(by='project_id')['project'].unique(),
                             placeholder="Select Projects",
                             multi=True, id='filter_project')
            ]
        ),
        html.Div(
            [
                dbc.Label("Payment Systems"),
                dcc.Dropdown(options=data.sort_values(by='ps_id')['ps'].unique(), placeholder="Select Payment Systems",
                             multi=True,
                             id='filter_ps')
            ]
        ),
        html.Div(
            [
                dbc.Label("Click Countries"),
                dcc.Dropdown(options=data.sort_values(by='co_id')['co_name'].unique(),
                             placeholder="Select Click Countries",
                             multi=True, id='filter_co')
            ]
        ),
        # html.Button('Apply', id='apply_filters', n_clicks=0),
        dbc.Button("Apply", id="apply_filters", n_clicks=0),
    ],
    body=True,
)


### OUTPUT

app.layout = html.Div([
    html.Div
        ([
            dbc.Container
                (
                    [
                        html.H1("[PW] PERFORMANCE DASHBOARD"),
                        html.Hr(),
                        dbc.Row(
                            [
                                dbc.Col(filters, md=3),
                                dbc.Col(dbc.Row([html.H4("Daily Performance"),
                                                dcc.Graph(id='graph_daily_rev_PV', figure=graph_daily_rev_PV(data))]), md=9),
                            ],
                            align="center",
                        ),
                    ],
                    fluid=True,
                ),

            dbc.Row
                ([
                    dbc.Col(dbc.Row([html.H4("Processing Projects"), dcc.Graph(id='graph_project_distitribution', figure=graph_project_distribution(data))]), md=4),
                    dbc.Col(dbc.Row([html.H4("Processing Payment Systems"), dcc.Graph(id='graph_ps_distribution', figure=graph_ps_distribution(data))]), md=4),
                    dbc.Col(dbc.Row([html.H4("Processing Click Countries"), dcc.Graph(id='graph_countries_distribution', figure=graph_countries_distribution(data))]), md=4),
                ]),
        ]),

    dbc.CardHeader
        (
        dbc.Tabs
            (
                [
                    dbc.Tab(label="Projects' Performance", tab_id="tab_project_performance"),
                    dbc.Tab(label="Payment Systems' Performance", tab_id="tab_ps_performance"),
                ],
                id="tabs",
                active_tab="tab_project_performance",
            ),
        ),
    html.Div(id="tab-content"),
])

########## CALLBACKS
##### FILTERS
@app.callback([Output('graph_daily_rev_PV', 'figure'),
               Output('graph_project_distitribution', 'figure'),
               Output('graph_ps_distribution', 'figure'),
               Output('graph_countries_distribution', 'figure'),
               Output('pivot_project_daily_PV', 'data'),
               Output('pivot_project_daily_PV', 'columns'),
               Output('pivot_ps_daily_PV', 'data'),
               Output('pivot_ps_daily_PV', 'columns'),
               Output('graph_top_project_daily_PV', 'figure'),
               Output('graph_top_ps_daily_PV', 'figure'),
               ],
              Input('apply_filters', 'n_clicks'),
              [State('filter_date', 'start_date'), State('filter_date', 'end_date'),
               State('filter_project', 'value'), State('filter_ps', 'value'), State('filter_co', 'value')]
              )
def update_conditions(n_clicks, start_date, end_date, project_list, ps_list, co_list):
    df = apply_filters(start_date, end_date, project_list, ps_list, co_list)

    figure_graph_daily_rev_PV = graph_daily_rev_PV(df)
    figure_graph_project_distribution = graph_project_distribution(df)
    figure_graph_ps_distribution = graph_ps_distribution(df)
    figure_graph_countries_distribution = graph_countries_distribution(df)
    data_pivot_project_daily_PV = pivot_project_daily_PV(df).to_dict("records")
    columns_pivot_project_daily_PV = [{"name": i, "id": i} for i in pivot_project_daily_PV(df).columns]
    data_pivot_ps_daily_PV = pivot_ps_daily_PV(df).to_dict("records")
    columns_pivot_ps_daily_PV = [{"name": i, "id": i} for i in pivot_ps_daily_PV(df).columns]
    figure_graph_top_project_daily_PV = graph_top_project_daily_PV(df)
    figure_graph_top_ps_daily_PV = graph_top_ps_daily_PV(df)

    return [figure_graph_daily_rev_PV, figure_graph_project_distribution, figure_graph_ps_distribution,
            figure_graph_countries_distribution,
            data_pivot_project_daily_PV, columns_pivot_project_daily_PV, data_pivot_ps_daily_PV,
            columns_pivot_ps_daily_PV,
            figure_graph_top_project_daily_PV, figure_graph_top_ps_daily_PV
            ]


#### TABS
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    if active_tab:
        if active_tab == "tab_project_performance":
            return html.Div([dcc.Graph(id='graph_top_project_daily_PV', figure=graph_top_project_daily_PV(data)),
                             dash_table.DataTable(id='pivot_project_daily_PV',
                                                  data=pivot_project_daily_PV(data).to_dict("records"),
                                                  columns=[{"name": i, "id": i} for i in
                                                           pivot_project_daily_PV(data).columns],
                                                  style_table={'minWidth': '100%'},
                                                  style_cell_conditional=[
                                                      {'if': {'column_id': 'Project'}, 'width': '25%',
                                                       'textAlign': 'left'},
                                                  ],
                                                  style_cell={
                                                      'height': 'auto',
                                                      'whiteSpace': 'normal'
                                                  },
                                                  filter_action="native",
                                                  sort_action="native", sort_mode='multi',
                                                  page_action='native', page_current=0,
                                                  page_size=20)

                             ])
        elif active_tab == "tab_ps_performance":
            return html.Div([dcc.Graph(id='graph_top_ps_daily_PV',figure=graph_top_ps_daily_PV(data)),
                dash_table.DataTable(id='pivot_ps_daily_PV',
                                     data=pivot_ps_daily_PV(data).to_dict("records"),
                                     columns=[{"name": i, "id": i} for i in pivot_ps_daily_PV(data).columns],
                                     style_table={'overflowX': 'auto'},
                                     style_cell={
                                         'height': 'auto',
                                         # all three widths are needed
                                         'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                         'whiteSpace': 'normal'
                                     },
                                     filter_action="native",
                                     sort_action="native",
                                     sort_mode='multi',
                                     page_action='native',
                                     page_current=0, page_size=20),
                ])
    return "No tab selected"



