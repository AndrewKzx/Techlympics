"""Base state for the app."""

import reflex as rx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, BatchNormalization, Activation
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping


class State(rx.State):

    # ===== State Fields =====
    # The current items in the todo list.
    items = ["Write Code", "Sleep", "Have Fun"]

    # The new item to add to the todo list.
    new_item: str

    # whether an item entered is valid
    invalid_item: bool = False

    # ===== Figure Data =====
    figure_plt: go.Figure = go.Figure(
        data=[],

        layout=go.Layout(
            title='Financial Report',
            minreducedheight=800,
            minreducedwidth=800,
        )
    )

    figure_loading: str = "Ready for input"
    # ===== Figure Data =====

    # ===== State Fields =====

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
        self.items.pop(self.items.index(item))

    # Handle submit function to handle the data of the user input, it is put into this
    def handle_submit(self, form_data: dict):
        self.figure_loading = "Data is loading..."

        for value in form_data.values():
            if value:
                continue
            else:
                self.figure_loading = "Ready for input"
                print("At least one of the values is empty")
                return

        # Change figure
        self.run_figure(form_data)

    # ===== Figure related =====
    def run_figure(self, form_data: dict) -> go.Figure:
        start_year, start_month = form_data["sym"].split("/")
        start_year, start_month = int(start_year), int(start_month)

        household_income = int(form_data["income"])
        monthly_expenses = int(form_data["expenses"])

        loan_amt = int(form_data["loan"])
        loan_interest = 1.0 + (int(form_data["interest"]) / 100)
        installment_months = int(form_data["installment"])
        real_loan_cost_montly = (
            loan_amt * loan_interest
        ) / installment_months

        # Get end of year and month
        end_year = start_year + (start_month + installment_months - 1) // 12
        end_month = (start_month + installment_months - 1) % 12 + 1

        offset_months = 0

        # just in case if started at an earlier year / month
        model_sy = start_year
        model_sm = start_month
        # model's minimum start date: 2023, 8
        if (start_year > 2023):
            # bigger than 2023 (constant 5 for from August 2023)
            offset_months = 5 + end_month + 12 * (start_year - 2024)
            model_sy = 2023
            model_sm = 8
        elif (start_year == 2023):
            # is 2023
            if (start_month > 8):
                # if month bigger than 8, set it to 8 and set offset
                offset_months = end_month - start_month
                model_sm = 8

        predicted_inflation, predicted_overall_inflation = predict_inflation(
            create_date_range(model_sy, model_sm,
                              installment_months + offset_months)
        )

        predicted_inflation = predicted_inflation[offset_months:]

        months = []
        for i in range(start_month, start_month+installment_months):

            if i % 12 != 0:
                # 1 - 11
                months.append(f"{start_year}/{i % 12}")
            else:
                months.append(f"{start_year}/12")
                start_year += 1

        real_income = [household_income]
        real_debt_cost = [real_loan_cost_montly]
        real_monthly_expenses = [monthly_expenses + real_debt_cost[0]]

        for m in range(1, len(predicted_inflation)):
            real_income.append(
                real_income[m - 1] * (1 - predicted_inflation[m] / 100)
            )
            real_debt_cost.append(
                real_debt_cost[m - 1] * (1 - predicted_inflation[m] / 100)
            )
            real_monthly_expenses.append(monthly_expenses + real_debt_cost[-1])

        trace1 = go.Scatter(x=months, y=real_income, mode='lines',
                            name='Real Monthly Income', fill='tozeroy')
        trace2 = go.Scatter(x=months, y=real_monthly_expenses, mode='lines',
                            name='Real Monthly Expenses', fill='tozeroy')
        trace3 = go.Scatter(x=months, y=real_debt_cost, mode='lines',
                            name='Real Monthly Debt', fill='tozeroy')

        fig = go.Figure(
            data=[trace1, trace2, trace3],

            layout=go.Layout(
                title='Financial Report',
                xaxis=dict(
                    tickvals=months,
                    ticktext=months,
                    dtick=1
                ),
                yaxis=dict(range=[0, 20000], dtick=1000),
                minreducedheight=800,
                minreducedwidth=800,
            )
        )
        fig.update_layout(yaxis_range=[0, 20000])

        self.figure_plt = fig
        self.figure_loading = "Data is ready"


# ===== Model Code =====

def read_data():
    df = pd.read_csv('./pynecone/model/cleaned_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df


def create_date_range(start_year: int, start_month: int, num_of_months: int):
    start_month = str(start_year) + "-" + str(start_month).rjust(2, "0")
    return pd.date_range(start_month, freq='M', periods=num_of_months)


df = read_data()
sequence_length = 12

# Model initialise
model = Sequential()
model.add(LSTM(64, input_shape=(12, 1),
          kernel_regularizer=l2(0.01), return_sequences=False))
model.add(Dense(32, kernel_regularizer=l2(0.01)))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')
model.load_weights("./pynecone/model/cp.ckpt")


def predict_inflation(date_range):
    number_of_months = len(date_range)

    start_date = date_range[0] - pd.DateOffset(months=sequence_length)

    date_range = pd.date_range(start_date, freq="M", periods=sequence_length)
    initial_data = df["base_inflation"][date_range]
    initial_inflation = df["overall_inflation"][date_range]

    predicted_inflation = []
    predicted_overall_inflation = []
    previous_inflation = initial_inflation[-1]
    for i in range(number_of_months):
        # Slice the portion of initial_data for prediction
        input_sequence = initial_data[i: i + sequence_length]
        prediction = model.predict(input_sequence, verbose=0)
        predicted_value = prediction[0][0]

        predicted_inflation.append(predicted_value)
        previous_inflation = previous_inflation * (1 + predicted_value / 100)
        predicted_overall_inflation.append(previous_inflation)

        initial_data = pd.concat([initial_data, pd.Series([predicted_value])])
        initial_inflation = pd.concat(
            [initial_inflation, pd.Series([previous_inflation])])

    return predicted_inflation, predicted_overall_inflation
# ===== Model Code =====
