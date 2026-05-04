from dash import html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
from utils.mongodb import w08_search_publications, w08_add_favorite, w08_remove_favorite, w08_get_favorites


def build_widget08():
    return dbc.Card([
        dbc.CardHeader("Favorite Publications (MongoDB)"),
        dbc.CardBody([
            dbc.InputGroup([
                dbc.Input(id="w08-keyword", placeholder="Search publications...",
                          value="neural network", debounce=True),
                dbc.Button("Search", id="w08-search-btn", color="primary"),
            ], className="mb-2"),
            html.Div(id="w08-search-results"),
            html.Hr(),
            html.P("Saved Papers:"),
            html.Div(id="w08-favorites"),
            dcc.Store(id="w08-refresh", data=0),
            dcc.Store(id="w08-search-store", data=[]),
        ])
    ])


@callback(Output("w08-search-results", "children"),
          Output("w08-search-store", "data"),
          Input("w08-search-btn", "n_clicks"),
          Input("w08-keyword", "value"),
          prevent_initial_call=False)
def search_pubs(_, keyword):
    if not keyword:
        return "", []
    data = w08_search_publications(keyword, 10)
    if not data:
        return html.P("No results found."), []

    rows = []
    for p in data:
        pub_id = str(p.get("_id", ""))
        rows.append(dbc.Row([
            dbc.Col(str(p.get("title",""))[:60] + "…", width=10),
            dbc.Col(dbc.Button("+", id={"type": "w08-add", "index": pub_id},
                               color="success", size="sm"), width=2),
        ], className="mb-1 align-items-center"))

    store = [{"id": str(p.get("_id","")), "title": str(p.get("title","")),
              "year": str(p.get("year","")), "venue": str(p.get("venue","") or "")}
             for p in data]
    return html.Div(rows), store


@callback(Output("w08-refresh", "data"),
          Input({"type": "w08-add", "index": ALL}, "n_clicks"),
          State("w08-search-store", "data"),
          State("w08-refresh", "data"),
          prevent_initial_call=True)
def add_pub(n_clicks, store_data, refresh):
    from dash import ctx
    if not ctx.triggered_id or not any(n for n in n_clicks if n):
        return refresh
    pub_id = ctx.triggered_id["index"]
    title, year, venue = pub_id, "", ""
    for p in (store_data or []):
        if p["id"] == pub_id:
            title, year, venue = p["title"], p["year"], p["venue"]
            break
    w08_add_favorite(pub_id, title, year, venue)
    return refresh + 1


@callback(Output("w08-favorites", "children"),
          Input("w08-refresh", "data"),
          Input({"type": "w08-remove", "index": ALL}, "n_clicks"),
          prevent_initial_call=False)
def show_favorites(refresh, _):
    from dash import ctx
    if (ctx.triggered_id and isinstance(ctx.triggered_id, dict)
            and ctx.triggered_id.get("type") == "w08-remove"):
        w08_remove_favorite(ctx.triggered_id["index"])

    favs = w08_get_favorites()
    if not favs:
        return html.P("No saved papers yet.")

    rows = [html.Tr([
        html.Td(str(f.get("title",""))[:50] + "…"),
        html.Td(str(f.get("year",""))),
        html.Td(dbc.Button("Remove", id={"type": "w08-remove", "index": f["publication_id"]},
                            color="danger", size="sm", outline=True)),
    ]) for f in favs]

    return dbc.Table([html.Tbody(rows)], bordered=True, hover=True,
                     responsive=True, size="sm")
