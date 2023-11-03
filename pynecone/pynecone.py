"""Welcome to Reflex!."""

from pynecone import styles

# Import all the pages.
from pynecone.pages import *

import reflex as rx

# Create the app and compile it.
app = rx.App(style=styles.base_style)
app.compile()
