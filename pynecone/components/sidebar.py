"""Sidebar component for the app."""

from pynecone import styles
from pynecone.state import State

import reflex as rx

from typing import List

options: List[str] = ["1", "2", "3", "4"]


def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar header component.
    """
    return rx.hstack(
        # The logo.
        rx.text(
            "EconoMe",
            background_image="linear-gradient(271.68deg, #EE756A 0.75%, #756AEE 88.52%)",
            background_clip="text",
            font_weight="bold",
            font_size="2em",
        ),
        rx.spacer(),
        # Link to Reflex GitHub repo.
        rx.link(
            rx.center(
                rx.image(
                    src="/github.svg",
                    height="3em",
                    padding="0.5em",
                ),
                box_shadow=styles.box_shadow,
                bg="transparent",
                border_radius=styles.border_radius,
                _hover={
                    "bg": styles.accent_color,
                },
            ),
            href="https://github.com/reflex-dev/reflex",
        ),
        width="100%",
        border_bottom=styles.border,
        padding="1em",
    )


def sidebar_footer() -> rx.Component:
    """Sidebar footer.

    Returns:
        The sidebar footer component.
    """
    return rx.hstack(
        rx.spacer(),
        rx.link(
            rx.text("Docs"),
            href="https://reflex.dev/docs/getting-started/introduction/",
        ),
        rx.link(
            rx.text("Blog"),
            href="https://reflex.dev/blog/",
        ),
        width="100%",
        border_top=styles.border,
        padding="1em",
    )


def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    """Sidebar item.

    Args:
        text: The text of the item.
        icon: The icon of the item.
        url: The URL of the item.

    Returns:
        rx.Component: The sidebar item component.
    """
    # Whether the item is active.
    active = (State.router.page.path == f"/{text.lower()}") | (
        (State.router.page.path == "/") & text == "Home"
    )

    return rx.link(
        rx.hstack(
            rx.image(
                src=icon,
                height="2.5em",
                padding="0.5em",
            ),
            rx.text(
                text,
            ),
            bg=rx.cond(
                active,
                styles.accent_color,
                "transparent",
            ),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
            width="100%",
            padding_x="1em",
        ),
        href=url,
        width="100%",
    )



def sidebar() -> rx.Component:
    """The sidebar.

    Returns:
        The sidebar component.
    """

    # Get all the decorated pages and add them to the sidebar.
    from reflex.page import get_decorated_pages

    return rx.box(
    rx.vstack(
        sidebar_header(),

        rx.container(
            rx.text("Household Income", class_name="text-black-500 font-bold"),  # Add a text element as a title
            rx.input(
            placeholder="RM",
            margin_top="8px",
            border_color="#eaeaef",

            ),
            rx.text("Monthly Income", class_name="text-black-500 font-bold mt-3"),  # Add a text element as a title
            rx.input(
            placeholder="RM",
            margin_top="8px",
            border_color="#eaeaef",

            ),
            rx.button("Generate", class_name="bg-blue-500 mt-5", background_color="#24A148", text_color="white"),  # Center align and make it green
            padding="1rem",
            margin="1rem",  # Add margin property here
            max_width="400px",
            border=styles.border,
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
            
        ),
        rx.spacer(),
        rx.container(

            rx.container(
            rx.text("Your Monthly Payment: RM3000", class_name="text-black-500 font-bold"),  # Add a text element as a title

            max_width="250px",
            margin="2%",
            border=styles.border,
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
            ),
            rx.text("Loan Tenure", class_name="text-black-500 font-bold"),  # Add a text element as a title
            rx.slider(
           
            ),
        

            rx.text("Interest Rate", class_name="text-black-500 font-bold"),  # Add a text element as a title
            rx.input(
            placeholder="            %",
            margin_top="8px",
            border_color="#eaeaef",
            max_width="100px",
            ),
            
            rx.select(
                options,
               
            ),
            rx.text("Monthly Income", class_name="text-black-500 font-bold mt-3"),  # Add a text element as a title
            rx.input(
            placeholder="RM",
            margin_top="8px",
            border_color="#eaeaef",

            ),

            
            rx.button("Generate", class_name="bg-blue-500 mt-5", background_color="#24A148", text_color="white"),  # Center align and make it green
            padding="1rem",
            margin="1rem",  # Add margin property here
            max_width="400px",
            border=styles.border,
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
        ),

        sidebar_footer(),
        height="100dvh",
    ),
    display=["none", "none", "block"],
    min_width=styles.sidebar_width,
    height="100%",
    width="60%",
    position="sticky",
    top="0px",
    border_right=styles.border,
)


