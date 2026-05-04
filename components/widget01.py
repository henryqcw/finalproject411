from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.mysql import w01_search_publications
from utils.common import make_table


def build_widget01():
    return dbc.Card([
        dbc.CardHeader("Keyword Publication Search (MySQL)"),
        dbc.CardBody([
            dbc.InputGroup([
                dbc.Input(id="w01-keyword", placeholder="e.g. machine learning",
                          value="machine learning", debounce=True),
                dbc.Button("Search", id="w01-btn", color="primary"),
            ], className="mb-3"),
            html.Div(id="w01-results"),
        ])
    ])


@callback(Output("w01-results", "children"),
          Input("w01-btn", "n_clicks"),
          Input("w01-keyword", "value"),
          prevent_initial_call=False)
def update_w01(_, keyword):
    if not keyword:
        return html.P("Enter a keyword to search.")
    data = w01_search_publications(keyword, 15)
    if not data:
        return html.P("No results found.")
    rows = [[r.get("title","")[:70], r.get("year",""),
             r.get("num_citations", 0), r.get("venue","")[:30]] for r in data]
    return make_table(["Title", "Year", "Citations", "Venue"], rows)
