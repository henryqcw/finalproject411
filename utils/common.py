from dash import html
import plotly.graph_objects as go


def make_table(columns, rows):
    thead = html.Thead(html.Tr([html.Th(c) for c in columns]))
    tbody = html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in rows])
    return html.Table([thead, tbody], className="table table-hover table-sm")


CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8e8e8"),
    xaxis=dict(color="#e8e8e8", gridcolor="#3a3a4a"),
    yaxis=dict(color="#e8e8e8", gridcolor="#3a3a4a"),
    margin=dict(l=10, r=10, t=30, b=10),
)


def empty_figure(msg="No data"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(color="#e8e8e8", size=13))
    fig.update_layout(**CHART_LAYOUT)
    return fig
