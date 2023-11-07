"""The home page of the app."""

from pynecone import styles
from pynecone.templates import template

import reflex as rx
import plotly.express as px
import plotly.graph_objects as go


@template(route="/", title="Home", image="/github.svg")
def index() -> rx.Component:

    x = [1, 2, 3, 4, 5]
    y1 = [2, 4, 1, 7, 4]
    y2 = [1, 3, 2, 5, 6]

    trace1 = go.Scatter(x=x, y=y1, mode='lines', name='Line 1', fill='tozeroy')
    trace2 = go.Scatter(x=x, y=y2, mode='lines', name='Line 2', fill='tozeroy')

    # Create layout
    layout = go.Layout(
        title='Multiple Line Graph with Area Fill',
        xaxis=dict(title='X-axis Label'),
        yaxis=dict(title='Y-axis Label'),
    )

    # Combine traces and layout to create the figure
    fig = go.Figure(data=[trace1, trace2], layout=layout)

    return rx.container(
        rx.plotly(data=fig, height="400px")
    )
