from ..connect_db import runQuery_tidb
from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import datetime


######### CREATE DJANGO DASH APP
app = DjangoDash(name='realtime_pw_performance', external_stylesheets=[dbc.themes.ZEPHYR])


#################################################################################
################################################ DATA
def get_raw_data():
    data = runQuery_tidb(f"""
    SELECT
    CONVERT_TZ(FROM_UNIXTIME(psc.cl_date_clicked), 'GMT', 'US/Central') AS timecl,
    DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(FLOOR(psc.cl_date_clicked/300)*300),'GMT', 'US/Central'),'%y-%m-%d %H:%i') AS datecl,
    DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(FLOOR(psc.cl_date_clicked/300)*300),'GMT', 'US/Central'),'%H:%i') AS h_m,
    psc.cl_id, psc.cl_tracked, psc.cl_approved, psc.cl_refunded, psc.cl_fraud, psc.cl_revenue_xe,

    psc.a_id AS project_id, a.a_name AS project_name, CONCAT('[',psc.a_id,'] ',a.a_name) AS project,
    a.d_id AS merchant_id, d.d_company AS merchant_name, CONCAT('[',a.d_id,'] ',d.d_company) AS merchant,
    psc.ps_id, ps.ps, 
    psc.pss_id, CASE WHEN psc.pss_id=0 OR psc.pss_id IS NULL THEN 'Unknown' ELSE pss.pss END AS pss,
    psc.co_id, co.co_code_alpha3, co.co_name

    FROM (SELECT * FROM ti_paymentwall.ps_clicks WHERE cl_date_clicked > FLOOR(UNIX_TIMESTAMP(NOW() - INTERVAL 3 HOUR)/300)*300) AS psc
    INNER JOIN ti_paymentwall.applications AS a ON psc.a_id = a.a_id
    INNER JOIN ti_paymentwall.developers AS d ON a.d_id = d.d_id
    INNER JOIN (SELECT ps_id, CONCAT('[',ps_id,'] ',ps_name) AS ps FROM ti_paymentwall.payment_systems) AS ps ON psc.ps_id = ps.ps_id
    LEFT JOIN (SELECT pss_id, CONCAT('[',pss_id,'] ',pss_name) AS pss FROM ti_paymentwall.ps_subaccounts) AS pss ON psc.pss_id = pss.pss_id
    INNER JOIN ti_paymentwall.countries AS co ON psc.co_id = co.co_id
    """)

    return data

data = get_raw_data()

### function to apply filters
def apply_filters(project_id_list, ps_id_list, co_id_list):
    global data
    df = data
    df = df if not project_id_list else df[df['project_id'].isin(project_id_list)]
    df = df if not ps_id_list else df[df['ps_id'].isin(ps_id_list)]
    df = df if not co_id_list else df[df['co_id'].isin(co_id_list)]
    return df


#################################################################################
################################################ CHARTS
def graph_overall_performance(df, click_color, conversion_color, cr_color, show_legend):
    global data
    overall = pd.DataFrame(df.groupby(['datecl']).agg(clicks=pd.NamedAgg(column="cl_id", aggfunc="count"),
                                                             conversions=pd.NamedAgg(column="cl_tracked", aggfunc="sum")
                                                             ).reset_index())
    overall['conversion_rate'] = overall['conversions'] / overall['clicks']
    all_times = pd.DataFrame(data['datecl'].unique(), columns=['datecl']).sort_values(by='datecl').reset_index()
    overall = all_times.merge(overall, on='datecl', how='left').fillna(0)
    overall_graph = make_subplots(specs=[[{"secondary_y": True}]])
    overall_graph.add_trace(go.Bar(x=overall['datecl'], y=overall['clicks'], name="#Clicks", marker_color=click_color),
                            secondary_y=False)
    overall_graph.add_trace(go.Bar(x=overall['datecl'], y=overall['conversions'], name="#Conversions", marker_color=conversion_color),
                            secondary_y=False)
    overall_graph.add_trace(
        go.Scatter(x=overall['datecl'], y=overall['conversion_rate'], name="Conversion Rate", marker_color=cr_color),
        secondary_y=True)
    overall_graph.update_layout(xaxis={'title': 'Time', 'tickformat': '%H:%M'},
                                plot_bgcolor='white', hovermode="x", margin=dict(l=20, r=20, t=0, b=0), showlegend=show_legend)
    overall_graph.update_yaxes(title_text="#Clicks", rangemode="tozero", secondary_y=False)
    overall_graph.update_yaxes(title_text="Conversion Rate (%)", rangemode="tozero", secondary_y=True, range=[0, 1],
                               tickformat=".0%")

    return overall_graph


### function to graph specific project/ps/co
### required: click_color, conversion_color, conversion_rate_color, show_legend
def graph_var_performance(**kwargs):
    project_id_list = None if not 'project_id' in kwargs else kwargs['project_id']
    ps_id_list = None if not 'ps_id' in kwargs else kwargs['ps_id']
    co_id_list = None if not 'co_id' in kwargs else kwargs['co_id']
    df = apply_filters(project_id_list, ps_id_list, co_id_list)
    return graph_overall_performance(df, kwargs['click_color'], kwargs['conversion_color'], kwargs['cr_color'], kwargs['show_legend'])

#################################################################################
################################################ LAYOUT
app.layout = html.Div([
    dcc.Interval(id='live_updating', interval=60*1000, n_intervals=0),
    html.H1("[PW] REAL-TIME PERFORMANCE DASHBOARD"),
    html.Hr(),
    html.Div(id='output'),
    dbc.Container([
        html.H3("Overall Performance"),
        dcc.Graph(id='graph_overall_performance', figure=graph_overall_performance(data, click_color='blue', conversion_color='red', cr_color='green', show_legend=True)),
    ], fluid=True),
    dbc.Row([
        dbc.Col([
            dbc.Tabs(
                [
                    dbc.Tab(tab_id='project_watchlist', label="Project Watchlist"),
                    dbc.Tab(tab_id='ps_watchlist', label="PS Watchlist"),
                ], id='tabs', active_tab='project_watchlist',
            ),
            html.Div(id='tab_content')
        ], width=11)
    ],align='center',justify="evenly"),
])

#################################################################################
################################################ CALLBACKS
@app.callback([Output('output','children'),
               Output('graph_overall_performance','figure'),
               Output('tab_content','children')
               ],
              [Input('tabs','active_tab'), Input('live_updating','n_intervals')])
def update_live_and_switch_tab(active_tab, n_intervals):
    global data
    data = get_raw_data()
    if active_tab=='project_watchlist':
        return [u'''Time now: {} --- updated {} times'''.format(datetime.datetime.now(), n_intervals),
                graph_overall_performance(data, click_color='blue', conversion_color='red', cr_color='green', show_legend=True),
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H6("[388099] Black Desert Online (NA/EU)"),
                            dcc.Graph(id='graph_project_388099_performance',
                                      figure=graph_var_performance(project_id=[388099], click_color='orange',
                                                                   conversion_color='grey', cr_color='red', show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[381469] Gameforge - Credit Cards"),
                            dcc.Graph(id='graph_project_381469_performance',
                                      figure=graph_var_performance(project_id=[381469], click_color='pink',
                                                                   conversion_color='purple', cr_color='blue', show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[390113] GI - Credit Cards"),
                            dcc.Graph(id='graph_project_390113_performance',
                                      figure=graph_var_performance(project_id=[390113], click_color='blue',
                                                                   conversion_color='orange', cr_color='green', show_legend=False)),
                        ], md=4),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H6("[43438] MMOGA Limited"),
                            dcc.Graph(id='graph_project_43438_performance',
                                      figure=graph_var_performance(project_id=[43438], click_color='blue',
                                                                   conversion_color='green', cr_color='orange',
                                                                   show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[24120] Wargaming Production EU"),
                            dcc.Graph(id='graph_project_24120_performance',
                                      figure=graph_var_performance(project_id=[24120], click_color='red',
                                                                   conversion_color='black', cr_color='grey',
                                                                   show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[23350] GTArcade"),
                            dcc.Graph(id='graph_project_23350_performance',
                                      figure=graph_var_performance(project_id=[23350], click_color='purple',
                                                                   conversion_color='grey', cr_color='blue',
                                                                   show_legend=False)),
                        ], md=4),
                    ]),
                ],fluid=True),
                ]
    elif active_tab == 'ps_watchlist':
        return [u'''Time now: {} --- updated {} times'''.format(datetime.datetime.now(), n_intervals),
                graph_overall_performance(data, click_color='blue', conversion_color='red', cr_color='green', show_legend=True),
                dbc.Row([
                        dbc.Col([
                            html.H6("[132] Gateway"),
                            dcc.Graph(id='graph_ps_132_performance',
                                      figure=graph_var_performance(ps_id=[132], click_color='orange',
                                                                   conversion_color='grey', cr_color='red', show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[1] PayPal"),
                            dcc.Graph(id='graph_ps_1_performance',
                                      figure=graph_var_performance(ps_id=[1], click_color='pink',
                                                                   conversion_color='purple', cr_color='blue', show_legend=False)),
                        ], md=4),
                        dbc.Col([
                            html.H6("[144] Mobiamo"),
                            dcc.Graph(id='graph_ps_144_performance',
                                      figure=graph_var_performance(ps_id=[144], click_color='blue',
                                                                   conversion_color='orange', cr_color='green', show_legend=False)),
                        ], md=4),
                    ]),
                ]

