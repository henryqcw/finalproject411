from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from utils.mysql import w02_get_university_profile, w02_get_university_list
from utils.common import empty_figure, CHART_LAYOUT

_UNI_LIST = w02_get_university_list()


def build_widget02():
    return dbc.Card([
        dbc.CardHeader("University Research Profile (MySQL)"),
        dbc.CardBody([
            dcc.Dropdown(id="w02-uni",
                         options=[{"label": u, "value": u} for u in _UNI_LIST],
                         value="University of Illinois at Urbana Champaign",
                         className="mb-3"),
            html.Div(id="w02-stats"),
            dcc.Graph(id="w02-chart", style={"height": "220px"},
                      config={"displayModeBar": False}),
        ])
    ])


@callback(Output("w02-stats", "children"), Output("w02-chart", "figure"),
          Input("w02-uni", "value"))
def update_w02(uni):
    if not uni:
        return "", empty_figure()
    stats, keywords = w02_get_university_profile(uni)
    if not stats:
        return html.P("No data found."), empty_figure()

    summary = dbc.Row([
        dbc.Col(html.Div([html.H5(f"{stats.get('faculty_count',0):,}"), html.Small("Faculty")]),   width=4),
        dbc.Col(html.Div([html.H5(f"{stats.get('pub_count',0):,}"),     html.Small("Publications")]), width=4),
        dbc.Col(html.Div([html.H5(f"{int(stats.get('total_citations') or 0):,}"), html.Small("Citations")]), width=4),
    ], className="mb-3 text-center")

    if keywords:
        df = pd.DataFrame(keywords)
        fig = px.bar(df, x="cnt", y="keyword_name", orientation="h",
                     labels={"cnt": "Publications", "keyword_name": ""})
        fig.update_layout(**CHART_LAYOUT)
    else:
        fig = empty_figure()

    return summary, fig
