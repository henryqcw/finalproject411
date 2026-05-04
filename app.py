import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
import dash_bootstrap_components as dbc

import components.widget01
import components.widget02
import components.widget03
import components.widget04
import components.widget05
import components.widget06
import components.widget07
import components.widget08

from components.layout import build_layout
from utils.setup import run_all_setup

run_all_setup()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Academic World Explorer"
app.layout = build_layout()

if __name__ == "__main__":
    app.run(debug=True, port=8050)
