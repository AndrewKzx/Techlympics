"""Base state for the app."""

import reflex as rx


class State(rx.State):
    """Base state for the app.

    The base state is used to store general vars used throughout the app.
    """

    # The current items in the todo list.
    items = ["Write Code", "Sleep", "Have Fun"]

    # The new item to add to the todo list.
    new_item: str

    # whether an item entered is valid
    invalid_item: bool = False

    def add_item(self, form_data: dict[str, str]):
        """Add a new item to the todo list.

        Args:
            form_data: The data from the form.
        """
        # Add the new item to the list.
        new_item = form_data.pop("new_item")
        if not new_item:
            self.invalid_item = True
            return

        self.items.append(new_item)
        # set the invalid status to False.
        self.invalid_item = False
        # Clear the value of the input.
        return rx.set_value("new_item", "")

    def finish_item(self, item: str):
        """Finish an item in the todo list.

        Args:
            item: The item to finish.
        """
        self.items.pop(self.items.index(item))


    pass
