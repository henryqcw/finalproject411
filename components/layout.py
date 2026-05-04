from dash import html
import dash_bootstrap_components as dbc

from components.widget01 import build_widget01
from components.widget02 import build_widget02
from components.widget03 import build_widget03
from components.widget04 import build_widget04
from components.widget05 import build_widget05
from components.widget06 import build_widget06
from components.widget07 import build_widget07
from components.widget08 import build_widget08


def build_layout():
    return html.Div([
        dbc.Navbar(
            dbc.Container(dbc.NavbarBrand("Academic World Explorer"), fluid=True),
            color="dark", dark=True, className="mb-4"
        ),
        dbc.Container([
            dbc.Row([dbc.Col(build_widget01(), md=7), dbc.Col(build_widget08(), md=5)], className="g-3 mb-3"),
            dbc.Row([dbc.Col(build_widget02(), md=5), dbc.Col(build_widget03(), md=7)], className="g-3 mb-3"),
            dbc.Row([dbc.Col(build_widget05(), md=7), dbc.Col(build_widget06(), md=5)], className="g-3 mb-3"),
            dbc.Row([dbc.Col(build_widget04(), md=6), dbc.Col(build_widget07(), md=6)], className="g-3 mb-3"),
        ], fluid=True),
    ])
