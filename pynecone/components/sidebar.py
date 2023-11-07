"""Sidebar component for the app."""

from pynecone import styles
from pynecone.state import State

import reflex as rx

#Ignore
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

#Ignore
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

def form_1() -> rx.Component:
    return rx.form(
        rx.text("Financial Information", class_name="text-black-500 font-bold text-2xl"),
        rx.container(
            rx.text("Household Income", class_name="text-black-500 font-bold"),
            rx.input(placeholder="Enter Expense 1", id="income"),
            rx.text("Monthly Expenses", class_name="text-black-500 font-bold"),
            rx.input(placeholder="Enter Expense 2", id="expenses"),
            rx.button("Submit", class_name="bg-blue-500 text-black mt-3", type_="submit"),
            padding="1rem",
            max_width="400px",
            border=styles.border,
            border_radius=styles.border_radius,
            box_shadow=styles.box_shadow,

            
        ),
        on_submit=State.handle_submit,
    )
def display_submitted_data() -> rx.Component:
    return rx.container(
        rx.text("Submitted Data", class_name="text-black-500 font-bold text-2xl"),
        rx.text("Household Income: " + State.submitted_data.get("income")),
        rx.text("Monthly Expenses: " + State.submitted_data.get("expenses")),
    )


#Can ignore this shit
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

#Mechanism to add new item into the form
def new_item() -> rx.Component:
    """Render the new item form.

    See: https://reflex.dev/docs/library/forms/form

    Returns:
        A form to add a new item to the todo list.
    """
    return rx.form(
        # Pressing enter will submit the form.
        rx.input(
            id="new_item",
            placeholder="Add an expense...",
            bg="white",
            is_invalid=State.invalid_item,
        ),
        # Clicking the button will also submit the form.
        rx.center(
            rx.button("Add", type_="submit", bg="green", color="white", margin_top="1rem"),
        ),
        on_submit=State.add_item,
    )

#Major Expenses section 
def todo_item(item: rx.Var[str]) -> rx.Component:
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

#To do list to render the items from the to do 
def todo_list() -> rx.Component:
    """Render the todo list.

    Returns:
        The rendered todo list.
    """
    return rx.ordered_list(
        # rx.foreach is necessary to iterate over state vars.
        # see: https://reflex.dev/docs/library/layout/foreach
        rx.foreach(State.items, lambda item: todo_item(item)),
    )


#The main place to adjust the design and add components 
#components used:
#sidebar_header, form_1, todo_list, new_item, sidebar_footer
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
                form_1(),
                # display_submitted_data(),
                rx.spacer(),
                rx.text("Major Expenses", class_name="text-black-500 font-bold text-2xl"),

                rx.container(

                todo_list(),
                new_item(),

                padding="1rem",
                border=styles.border,
                border_radius=styles.border_radius,
                box_shadow=styles.box_shadow,
                ),
                rx.divider(),

                width="100%",
                overflow_y="auto",
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

  

