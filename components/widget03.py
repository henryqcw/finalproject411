from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.mysql import w03_compare_universities, w02_get_university_list
from utils.common import make_table

_UNI_LIST = w02_get_university_list()


def build_widget03():
    return dbc.Card([
        dbc.CardHeader("University Comparison (MySQL View)"),
        dbc.CardBody([
            dcc.Dropdown(id="w03-unis",
                         options=[{"label": u, "value": u} for u in _UNI_LIST],
                         value=["University of Illinois at Urbana Champaign",
                                "Carnegie Mellon University", "Stanford University"],
                         multi=True, className="mb-2"),
            dbc.Button("Compare", id="w03-btn", color="secondary", size="sm", className="mb-3"),
            html.Div(id="w03-table"),
        ])
    ])


@callback(Output("w03-table", "children"),
          Input("w03-btn", "n_clicks"),
          Input("w03-unis", "value"),
          prevent_initial_call=False)
def update_w03(_, unis):
    if not unis:
        return html.P("Select at least one university.")
    data = w03_compare_universities(unis)
    if not data:
        return html.P("No data found.")
    rows = [[r["university"], f"{r['faculty_count']:,}", f"{r['pub_count']:,}",
             f"{int(r['total_citations'] or 0):,}", f"{r['recent_pubs']:,}"] for r in data]
    return make_table(["University", "Faculty", "Publications", "Citations", "Recent (2020+)"], rows)
