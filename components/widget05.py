from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from utils.mysql import w05_top_faculty_for_keyword
from utils.mongodb import w05_publication_trend_mongo
from utils.common import empty_figure, CHART_LAYOUT


def build_widget05():
    return dbc.Card([
        dbc.CardHeader("Research Trends (MySQL Stored Procedure + MongoDB)"),
        dbc.CardBody([
            dbc.Input(id="w05-keyword", placeholder="e.g. deep learning",
                      value="deep learning", debounce=True, className="mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="w05-trend", style={"height": "220px"},
                                  config={"displayModeBar": False}), md=6),
                dbc.Col(dcc.Graph(id="w05-faculty", style={"height": "220px"},
                                  config={"displayModeBar": False}), md=6),
            ]),
        ])
    ])


@callback(Output("w05-trend", "figure"), Output("w05-faculty", "figure"),
          Input("w05-keyword", "value"))
def update_w05(keyword):
    if not keyword:
        return empty_figure(), empty_figure()

    mongo_data = w05_publication_trend_mongo(keyword)
    if mongo_data:
        df = pd.DataFrame(mongo_data).rename(columns={"_id": "year"})
        df = df[df["year"].notna()].sort_values("year")
        fig_trend = px.area(df, x="year", y="count",
                            labels={"count": "Publications", "year": "Year"},
                            title="Publications per Year (MongoDB)")
    else:
        fig_trend = empty_figure("No data")
    fig_trend.update_layout(**CHART_LAYOUT)

    fac_data = w05_top_faculty_for_keyword(keyword, 8)
    if fac_data:
        df2 = pd.DataFrame(fac_data)
        fig_fac = px.bar(df2, x="total_citations", y="faculty_name", orientation="h",
                         labels={"total_citations": "Citations", "faculty_name": ""},
                         title="Top Faculty (MySQL Stored Procedure)")
    else:
        fig_fac = empty_figure("No data")
    fig_fac.update_layout(**CHART_LAYOUT)

    return fig_trend, fig_fac
