"""The home page of the app."""

from pynecone import styles
from pynecone.templates import template
from ..state import State

import reflex as rx


@template(route="/", title="Home", image="/github.svg")
def index() -> rx.Component:
        bard_output_html = rx.html(State.bard_output.replace("\n", "<br><br>")) if hasattr(State, 'bard_output') and State.bard_output else rx.text(" ")

        return rx.container(

                rx.text("Real Monthly Income vs Real Monthly Expenses",
                        font_weight="bold",
                        font_size="1em",
                        color="forestgreen"
                        ),
                rx.plotly(data=State.figure_plt_1),
                rx.container(
                        
                rx.text(State.figure_description_1),
                border=styles.border,
                border_radius=styles.border_radius,
                box_shadow=styles.box_shadow,
                ),
                


                rx.text("Breakdown of Real Monthly Expenses (Stacked)",
                        font_weight="bold",
                        font_size="1em",
                        color="forestgreen",
                        margin_top="2rem"
                        ),
                rx.plotly(data=State.figure_plt_2),
                rx.text(State.figure_description_2),
                rx.container(
                rx.text(State.bard_ouput),
                border=styles.border,
                border_radius=styles.border_radius,
                box_shadow=styles.box_shadow,
                ),
                
                bard_output_html,
        )
