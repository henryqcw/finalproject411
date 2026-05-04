from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from utils.mysql import w04_get_faculty_profile, w04_get_faculty_list


def build_widget04():
    return dbc.Card([
        dbc.CardHeader("Faculty Profile (MySQL)"),
        dbc.CardBody([
            dcc.Dropdown(id="w04-faculty",
                         options=[{"label": f, "value": f} for f in w04_get_faculty_list()[:300]],
                         placeholder="Select a faculty member...",
                         className="mb-3"),
            html.Div(id="w04-profile"),
        ])
    ])


@callback(Output("w04-profile", "children"), Input("w04-faculty", "value"))
def update_w04(name):
    if not name:
        return html.P("Select a faculty member above.")
    profile = w04_get_faculty_profile(name)
    if not profile:
        return html.P("Profile not found.")

    keywords = [dbc.Badge(k["name"], color="secondary", className="me-1")
                for k in profile.get("keywords", [])]
    papers = html.Ul([
        html.Li(f"{p['title'][:60]}… ({p['year']}, {p['num_citations']:,} citations)")
        for p in profile.get("papers", [])
    ])

    return html.Div([
        html.H6(f"{profile['name']} — {profile.get('university','')}"),
        html.P(f"Publications: {int(profile.get('pub_count') or 0):,}  |  "
               f"Citations: {int(profile.get('total_citations') or 0):,}"),
        html.P("Keywords:"), html.Div(keywords, className="mb-2"),
        html.P("Top Papers:"), papers,
    ])
