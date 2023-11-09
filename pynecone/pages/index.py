"""The home page of the app."""

from pynecone import styles
from pynecone.templates import template
from ..state import State

import reflex as rx


@template(route="/", title="Home", image="/github.svg")
def index() -> rx.Component:

    return rx.container(

        rx.plotly(data=State.figure_plt_1),
        rx.text("Real Monthly Income vs Real Monthly Expenses"),

        rx.plotly(data=State.figure_plt_2),
        rx.text("Breakdown of Real Monthly Expenses (Stacked)"),
    )
