from dash import html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
from utils.mysql import w07_add_favorite, w07_remove_favorite, w07_get_favorites, w04_get_faculty_list


def build_widget07():
    return dbc.Card([
        dbc.CardHeader("Favorite Professors (MySQL + Trigger)"),
        dbc.CardBody([
            dbc.InputGroup([
                dcc.Dropdown(id="w07-faculty",
                             options=[{"label": f, "value": f} for f in w04_get_faculty_list()[:300]],
                             placeholder="Select faculty...",
                             style={"flex": "1", "minWidth": "0"}),
                dbc.Button("Add", id="w07-add-btn", color="warning"),
            ], className="mb-2"),
            html.Div(id="w07-msg", className="mb-2"),
            html.Div(id="w07-list"),
            dcc.Store(id="w07-refresh", data=0),
        ])
    ])


@callback(Output("w07-msg", "children"), Output("w07-refresh", "data"),
          Input("w07-add-btn", "n_clicks"),
          State("w07-faculty", "value"), State("w07-refresh", "data"),
          prevent_initial_call=True)
def add_favorite(_, name, refresh):
    if not name:
        return dbc.Alert("Select a faculty member first.", color="warning", duration=3000), refresh
    ok, msg = w07_add_favorite(name)
    return dbc.Alert(msg, color="success" if ok else "warning", duration=3000), refresh + 1


@callback(Output("w07-list", "children"),
          Input("w07-refresh", "data"),
          Input({"type": "w07-remove", "index": ALL}, "n_clicks"),
          prevent_initial_call=False)
def refresh_list(refresh, remove_clicks):
    from dash import ctx
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict):
        w07_remove_favorite(ctx.triggered_id["index"])

    favs = w07_get_favorites()
    if not favs:
        return html.P("No favorites yet.")

    rows = [html.Tr([
        html.Td(f["name"]),
        html.Td(f["university"]),
        html.Td(dbc.Button("Remove", id={"type": "w07-remove", "index": f["faculty_id"]},
                            color="danger", size="sm", outline=True)),
    ]) for f in favs]

    return dbc.Table([html.Tbody(rows)], bordered=True, hover=True,
                     responsive=True, size="sm")
