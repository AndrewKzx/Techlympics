"""Base state for the app."""

from datetime import datetime
import reflex as rx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, BatchNormalization, Activation
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping


class State(rx.State):

    # ===== State Fields =====
    # The current items in the todo list.
    loans_from_user = []
    show_loans = []

    # The new item to add to the todo list.
    new_item: str

    # ===== Figure Data =====
    figure_plt_1: go.Figure = go.Figure(
        data=[],

        layout=go.Layout(
            title='Financial Report',
            height=400,
            width=600,
        )
    )

    figure_plt_2: go.Figure = go.Figure(
        data=[],

        layout=go.Layout(
            title='Financial Report',
            height=400,
            width=600,
        )
    )

    figure_loading: str = "Ready for input"
    # ===== Figure Data =====

    # ===== State Fields =====

    def add_item(self, form_data: dict[str, str]):
        # Create a new item string with new lines
        new_item = f"Name: {form_data['name']}\n" \
            f"Date: {form_data['sym']}\n" \
            f"Value: {form_data['loan']}\n" \
            f"Interest: {form_data['interest']}\n" \
            f"Installment: {form_data['installment']}"

        # Add the new item to the list
        self.show_loans.append(new_item)
        self.loans_from_user.append(form_data)

        # Clear the value of the input.
        return [
            rx.set_value("sym", ""),
            rx.set_value("name", ""),
            rx.set_value("loan", ""),
            rx.set_value("interest", ""),
            rx.set_value("installment", "")
        ]

    def finish_item(self, item: str):
        index = self.show_loans.index(item)
        self.show_loans.pop(index)
        self.loans_from_user.pop(index)

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
        if not self.loans_from_user:
            self.figure_loading = "Ready for input"
            print("No Loans")
            return

        household_income = int(form_data["income"])
        monthly_expenses = int(form_data["expenses"])

        # Change figures
        self.create_figures(household_income, monthly_expenses)

        # Clear the value of the input.
        return [
            rx.set_value("income", ""),
            rx.set_value("expenses", ""),
        ]

    # ===== Figure related =====
    def create_figure_one(self, household_income, data_of_loans, monthly_expenses, months, predicted_inflation) -> go.Figure:

        real_full_expenses = [monthly_expenses for i in range(len(months))]

        # From the required starting loan date to final loan end date, add all loans to full_expenses
        for loan_focused in data_of_loans:
            offset = loan_focused["start_offset"]

            for j in range(loan_focused["installment_months"]):
                real_full_expenses[
                    offset + j] += loan_focused["real_monthly_payment"][j]

        real_income = [household_income]
        for m in range(len(months)):
            real_income.append(
                real_income[m - 1] * (1 - predicted_inflation[m] / 100)
            )

        monthly_income_trace = go.Scatter(x=months, y=real_income, mode='lines',
                                          name='Real Monthly Income', fill='tozeroy',
                                          marker=dict(color='green', line=dict(
                                              color='green', width=2)),
                                          fillcolor='rgba(0, 255, 0, 0.3)')
        full_expenses_trace = go.Scatter(x=months, y=real_full_expenses, mode='lines',
                                         name='Real Monthly Expenses', fill='tozeroy',
                                         marker=dict(color='red', line=dict(
                                             color='red', width=2)),
                                         fillcolor='#ff0000')

        figure = go.Figure(
            data=[monthly_income_trace, full_expenses_trace],

            layout=go.Layout(
                title='Financial Report',
                xaxis=dict(
                    tickvals=months,
                    ticktext=months,
                    dtick=1
                ),
                yaxis=dict(range=[0, 20000], dtick=1000),
                height=400,
                width=600,
                hovermode="x unified"
            )
        )

        return figure

    def create_figure_two(self, data_of_loans, monthly_expenses, months) -> go.Figure:
        # Create a stacked chart, with basic neccesity at the bottom, and stacked on top are loans
        real_basic_neccesity = [monthly_expenses for i in range(len(months))]
        cum_cost = real_basic_neccesity.copy()

        basic_neccesity_trace = go.Scatter(x=months, y=real_basic_neccesity, mode='lines',
                                           name='Real Basic Neccesity',
                                           marker=dict(color='#ffcc00', line=dict(
                                               color='orange', width=2)),
                                           fillcolor='#ffcc00', stackgroup='one'
                                           )

        # Initialize Tracers Holder
        tracers = [basic_neccesity_trace]

        # Initialize hover information
        hover_text_months = [
            f'<b>{months[i]}</b></br></br> <b>Real Basic Necessity</b>: {real_basic_neccesity[i]}</br>' for i in range(len(months))]

        # Run loans requirements
        for loan_focused in data_of_loans:
            offset = loan_focused["start_offset"]
            loan_name = loan_focused['name']
            real_monthly_payment = loan_focused['real_monthly_payment']

            for j in range(loan_focused["installment_months"]):
                cum_cost[offset + j] += round(real_monthly_payment[j], 2)
                hover_text_months[
                    offset + j] += f'<b>{loan_name}</b>: {real_monthly_payment[j]}</br>'

            tracers.append(
                go.Scatter(x=loan_focused["months_x"], y=loan_focused["real_monthly_payment"], mode='lines',
                           line=dict(width=2), name=loan_focused["name"], stackgroup='one'
                           )
            )

        for i in range(len(hover_text_months)):
            hover_text_months[i] += f'<b>Real Cumulated Expense</b>: {cum_cost[i]}</br>'

        figure = go.Figure(
            data=tracers,
            layout=go.Layout(
                title='Financial Report',
                xaxis=dict(
                    tickvals=months,
                    ticktext=months,
                    dtick=1
                ),
                height=400,
                width=600,
            )
        )

        figure.update_layout(
            hoverlabel=dict(
                namelength=-1  # Set namelength to -1 to expand hover label size dynamically
            )
        )

        for data in figure.data:
            data.hoverinfo = 'text'
            data.hovertext = hover_text_months

        figure.update_layout(hovermode='closest')

        return figure

    def diff_month(self, d1, d2):
        # d1 should be HIGHER or EQUAL to d2
        return (abs(d1.year - d2.year) * 12 + d1.month - d2.month)

    def process_loan_data(self, loanData):
        processed = {}

        processed["name"] = loanData["name"]
        start_year, start_month = loanData["sym"].split("/")
        processed["start_year"], processed["start_month"] = int(
            start_year), int(start_month)

        loan_amt = int(loanData["loan"])
        loan_interest = 1.0 + (int(loanData["interest"]) / 100)
        processed["installment_months"] = int(loanData["installment"])
        processed["installment_payment"] = (
            loan_amt * loan_interest
        ) / processed["installment_months"]

        processed["end_year"] = processed["start_year"] + \
            (processed["start_month"] +
             processed["installment_months"] - 1) // 12
        processed["end_month"] = (
            processed["start_month"] + processed["installment_months"] - 1) % 12 + 1

        return processed

    def calculate_real_loan(self, processedLoanData, predicted_inflation, months, start_y, start_m):
        # 1) Get the real monthly installment until end 2) Find out the range of months it's in (x-axis)

        # From the global required start offset, where should THIS loan start?
        start_offset = abs(self.diff_month(datetime(
            processedLoanData["start_year"], processedLoanData["start_month"], 1), datetime(start_y, start_m, 1)))

        processedLoanData["months_x"] = months[start_offset: start_offset +
                                               processedLoanData["installment_months"]]
        processedLoanData["start_offset"] = start_offset

        # Initialise with the first value (because its compounding)
        processedLoanData["real_monthly_payment"] = [
            processedLoanData["installment_payment"] * (1 - predicted_inflation[start_offset] / 100)]

        for i in range(1, len(processedLoanData["months_x"])):
            processedLoanData["real_monthly_payment"].append(
                processedLoanData["real_monthly_payment"][i - 1] * (1 - predicted_inflation[start_offset + i] / 100))

    def create_figures(self, household_income, monthly_expenses) -> go.Figure:
        # Get the loans (recalculates all loans, if new loan added would re-calculate)
        data_of_loans = []

        for loanData in self.loans_from_user:
            data_of_loans.append(self.process_loan_data(loanData))

        # Check the starting of each loans Year and Month
        lowest_start_year = min([x["start_year"] for x in data_of_loans])
        lowest_start_month = min(
            [x["start_month"] for x in data_of_loans if x["start_year"] == lowest_start_year])

        highest_end_year = max([x["end_year"] for x in data_of_loans])
        highest_end_month = max(
            [x["end_month"] for x in data_of_loans if x["end_year"] == highest_end_year])

        period_from_starting_date = self.diff_month(datetime(highest_end_year, highest_end_month, 1), datetime(
            lowest_start_year, lowest_start_month, 1))

        # just in case if started at an earlier year / month
        model_sy = lowest_start_year
        model_sm = lowest_start_month

        # NOTICE: model's maximum / highest start date: 2023, 8 (Constraints of LSTM model)
        if (lowest_start_year > 2023):
            # bigger than 2023 (constant 5 for from August 2023)
            model_sy = 2023
            model_sm = 8
        elif (lowest_start_year == 2023):
            # is 2023
            if (lowest_start_month > 8):
                # if month bigger than 8, set it to 8 and set offset
                model_sm = 8

        # Model sy and sm will only be lower than 2023 Aug if a loan is lower than that. Offset is difference between required start date of loans,
        # and actual date of model considerations
        offset = self.diff_month(datetime(
            lowest_start_year, lowest_start_month, 1), datetime(model_sy, model_sm, 1))
        offset = offset if offset > 0 else 0

        # offset is from model_sy and model_sm considerations
        predicted_inflation, predicted_overall_inflation = predict_inflation(
            create_date_range(model_sy, model_sm,
                              period_from_starting_date + offset)
        )

        # now only predicted inflation from required loan start date till the end of all loans
        predicted_inflation = predicted_inflation[offset:]

        months = []
        copy_lsy = lowest_start_year
        for i in range(lowest_start_month, lowest_start_month+len(predicted_inflation)):
            if i % 12 != 0:
                # 1 - 11
                months.append(f"{copy_lsy}/{i % 12}")
            else:
                months.append(f"{copy_lsy}/12")
                copy_lsy += 1

        # Calculate Real Loan Data
        for i in range(len(data_of_loans)):
            self.calculate_real_loan(
                data_of_loans[i], predicted_inflation, months, lowest_start_year, lowest_start_month)

        # ===== Figure Drawing =====
        # Income vs Loan
        self.figure_plt_1 = self.create_figure_one(
            household_income, data_of_loans, monthly_expenses, months, predicted_inflation
        )

        self.figure_plt_2 = self.create_figure_two(
            data_of_loans, monthly_expenses, months
        )

        print("creation done")

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
