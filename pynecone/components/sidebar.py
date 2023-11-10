"""Sidebar component for the app."""

from pynecone import styles
from pynecone.state import State

import reflex as rx


def sidebar_header() -> rx.Component:
    return rx.hstack(
        # The logo.
        rx.text(
            "EconoMe",
            background_image="linear-gradient(271.68deg, #4CAF50 0.75%, #81C784 88.52%)",
            background_clip="text",
            font_weight="bold",
            font_size="2em",
        ),
        rx.spacer(),
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
            href="https://github.com/AndrewKzx/Techlympics",
        ),
        width="400px",
        border_bottom=styles.border,
        padding="1em",
    )


def sidebar_footer() -> rx.Component:
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


def final_form() -> rx.Component:
    return rx.form(
        rx.text("Financial Information",
                class_name="text-black-500 font-bold text-2xl mt-4 mb-2"),
        rx.container(
            # User input for Income
            rx.text("Household Income", class_name="text-black-500 font-bold"),
            rx.input(placeholder="Enter Current Household Income", id="income",
                     #  on_change=State.handle_change
                     ),

            # User input for Expenses
            rx.text("Monthly Expenses (Not inclusive of loan(s))",
                    class_name="text-black-500 font-bold"),
            rx.input(placeholder="Enter Usual Monthly Expenses", id="expenses"),

            rx.button(
                "Submit", class_name="bg-blue-500 text-black mt-3", type_="submit"),
            padding="1rem",
            max_width="400px",
            border=styles.border,
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
        ),

        # When user click submit, this is sent to state.py/handle_submit function
        on_submit=State.handle_submit,
    )


def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
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

# Mechanism to add new item into the form


def new_loan() -> rx.Component:
    """Render the new item form.

    See: https://reflex.dev/docs/library/forms/form

    Returns:
        A form to add a new item to the todo list.
    """
    return rx.form(
        # User input for Starting Date info
        rx.text("Starting Date Info",
                class_name="text-black-500 font-bold"),
        rx.input(
            placeholder="Enter Starting Year and Month (2023/05)", id="sym", class_name="mb-4"),

        # User input for Loan Info
        rx.text("Relevant Loan Info",
                class_name="text-black-500 font-bold"),
        rx.input(placeholder="Enter Loan Name",
                 id="name", class_name="mb-4"),
        rx.input(placeholder="Enter Loan Amount (RM)",
                 id="loan", class_name="mb-4"),
        rx.input(placeholder="Enter Interest Rate (%)",
                 id="interest", class_name="mb-4"),
        rx.input(placeholder="Installment (Months)", id="installment"),

        # Clicking the button will also submit the form.
        rx.center(
            rx.button("Add", type_="submit", bg="green",
                      color="white", margin_top="1rem"),
        ),
        on_submit=State.add_item,
    )

# Major Expenses section


def todo_loan(item: rx.Var[str]) -> rx.Component:
    """Render an item in the todo list.

    NOTE: When using `rx.foreach`, the item will be a Var[str] rather than a str.

    Args:
        item: The todo list item.

    Returns:
        A single rendered todo list item.
    """
    return rx.list_item(
        rx.hstack(
            # A button to finish the item.
            rx.text(item, font_size="1.25em"),
            rx.button(
                "❌",
                on_click=lambda: State.finish_item(item),
                height="1.5em",
                background_color="white",
                text_color="white",  # Set the text color to white
                font_size="1em",  # Adjust the font size as needed
            ),
            # The item text.
        )
    )

# To do list to render the items from the to do


def loans_list() -> rx.Component:
    return rx.ordered_list(
        rx.container(
        rx.foreach(State.show_loans, lambda loan: todo_loan(loan)),
        border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,
            width="100%",
        ),
    )

# The main place to adjust the design and add components
# components used:
# sidebar_header, final_form, loans_list, new_loan, sidebar_footer


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
            rx.vstack(
                rx.text("Loan Information",
                        class_name="text-black-500 font-bold text-2xl"),
                rx.container(

                    loans_list(),
                    new_loan(),

                    padding="1rem",
                    border=styles.border,
                    border_radius=styles.border_radius,
                    box_shadow=styles.box_shadow,
                ),

                # Form 1 is called here as a component to put into the side bar
                final_form(),
                rx.spacer(),
                rx.divider(),

                width="400px",
                align_items="flex-start",
                padding="1em",
            ),
            rx.spacer(),
            sidebar_footer(),
            height="100dvh",
        ),
        display=["none", "none", "block"],
        min_width=styles.sidebar_width,
        height="100%",
        position="sticky",
        top="0px",
        border_right=styles.border,
    )
