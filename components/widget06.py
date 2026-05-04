from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from utils.neo4j import w06_institute_ranking, w06_related_keywords
from utils.common import empty_figure, CHART_LAYOUT


def build_widget06():
    return dbc.Card([
        dbc.CardHeader("Institute & Keyword Ranking (Neo4j)"),
        dbc.CardBody([
            dbc.Input(id="w06-keyword", placeholder="e.g. machine learning",
                      value="machine learning", debounce=True, className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="w06-institutes", style={"height": "220px"},
                                  config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(id="w06-related", style={"height": "220px"},
                                  config={"displayModeBar": False}), md=6),
            ]),
        ])
    ])


@callback(Output("w06-institutes", "figure"), Output("w06-related", "figure"),
          Input("w06-keyword", "value"))
def update_w06(keyword):
    if not keyword:
        return empty_figure(), empty_figure()

    try:
        inst = w06_institute_ranking(keyword, 8)
    except Exception:
        inst = []

    if inst:
        df = pd.DataFrame(inst)
        fig_inst = px.bar(df, x="faculty_count", y="institute", orientation="h",
                          labels={"faculty_count": "Faculty", "institute": ""},
                          title="Top Institutes")
    else:
        fig_inst = empty_figure("No data")
    fig_inst.update_layout(**CHART_LAYOUT)

    try:
        rel = w06_related_keywords(keyword, 8)
    except Exception:
        rel = []

    if rel:
        df2 = pd.DataFrame(rel)
        fig_rel = px.bar(df2, x="faculty_count", y="related_keyword", orientation="h",
                         labels={"faculty_count": "Faculty", "related_keyword": ""},
                         title="Related Keywords")
    else:
        fig_rel = empty_figure("No data")
    fig_rel.update_layout(**CHART_LAYOUT)

    return fig_inst, fig_rel
