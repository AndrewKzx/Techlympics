"""The home page of the app."""

from pynecone import styles
from pynecone.templates import template
from ..state import State

import reflex as rx


@template(route="/", title="Home", image="/github.svg")
def index() -> rx.Component:

    return rx.container(

        rx.text("Real Monthly Income vs Real Monthly Expenses",
                font_weight="bold",
                font_size="1em",
                color="forestgreen"
                ),
        rx.plotly(data=State.figure_plt_1),


        rx.text("Breakdown of Real Monthly Expenses (Stacked)",
                font_weight="bold",
                font_size="1em",
                color="forestgreen",
                margin_top="2rem"
                ),
        rx.plotly(data=State.figure_plt_2),
    )
