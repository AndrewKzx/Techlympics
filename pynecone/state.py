"""Base state for the app."""

from datetime import datetime
import reflex as rx
import plotly.express as px
import plotly.graph_objects as go
import pynecone.model as model_code
from bardapi import Bard


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

    figure_description_1_constant: str = "The gap between real monthly income and real monthly expenses represents your real disposable income adjusted for inflation. "

    figure_description_1: str = ""
    figure_description_2: str = ""
    bard_ouput: str = ""
    # ===== Figure Data =====

    # ===== State Fields =====

    def add_item(self, form_data: dict[str, str]):
        # Create a new item string with new lines
        new_item = f"Name: {form_data['name']}<br>" \
            f"Date: {form_data['sym']}<br>" \
            f"Value: {form_data['loan']}<br>" \
            f"Interest: {form_data['interest']}<br>" \
            f"Installment: {form_data['installment']}<br>"

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
        for m in range(1, len(months)):
            real_income.append(
                # previous real_income * current predicted_inflation
                real_income[m - 1] * ((100 - predicted_inflation[m]) / 100)
            )

            # Add 5% if January
            if (months[m].split("/")[1] == "1"):
                print(months[m])
                real_income[-1] *= 1.03

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

        # The figure, initial disposable income, final disposal income
        return figure, real_income[0] - real_full_expenses[0], real_income[-1] - real_full_expenses[-1]

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
            processedLoanData["installment_payment"] * ((100 - predicted_inflation[start_offset]) / 100)]

        for i in range(1, len(processedLoanData["months_x"])):
            processedLoanData["real_monthly_payment"].append(
                processedLoanData["real_monthly_payment"][i - 1] * ((100 - predicted_inflation[start_offset + i]) / 100))

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
            model_sm = 6
        elif (lowest_start_year == 2023):
            # is 2023
            if (lowest_start_month > 6):
                # if month bigger than 6, set it to 6 and set offset
                model_sm = 6

        # Model sy and sm will only be lower than 2023 Aug if a loan is lower than that. Offset is difference between required start date of loans,
        # and actual date of model considerations
        offset = self.diff_month(datetime(
            lowest_start_year, lowest_start_month, 1), datetime(model_sy, model_sm, 1))
        offset = offset if offset > 0 else 0

        # offset is from model_sy and model_sm considerations
        predicted_inflation = model_code.forecast_future_CPI(
            model_sy, model_sm, period_from_starting_date + offset
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
        self.figure_plt_1, initial_disposal, final_disposal = self.create_figure_one(
            household_income, data_of_loans, monthly_expenses, months, predicted_inflation
        )

        self.figure_description_1 = self.figure_description_1_constant + \
            f"Start of loan(s) disposable income: RM{'{:.2f}'.format(initial_disposal)}. Ebd of loan(s) disposable income: RM{'{:.2f}'.format(final_disposal)}."

        # Expenses breakdown data
        self.figure_plt_2 = self.create_figure_two(
            data_of_loans, monthly_expenses, months
        )

        print("creation done")

        lowest_start_year = min([x["start_year"] for x in data_of_loans])
        lowest_start_month = min(
            [x["start_month"] for x in data_of_loans if x["start_year"] == lowest_start_year])

        # Comment out for Bard
        self.chat_ask(household_income, monthly_expenses, initial_disposal, [
                      lowest_start_month, lowest_start_year], final_disposal, [highest_end_month, highest_end_year])

    def chat_ask(self, household_income, monthly_expenses, initial_disposal, initial_date, final_disposal, final_date):
        bard = Bard(
            "dQiLlaJ7FiLrgeKfMxQ2CBdadHOFgSqdiska6PT1RerIhfd2HnvFs6FX9SOIFPUdIUFVCA."
        )
        prompt = f"Given the following financial data, assess the feasiblity of someone with a monthly household income of RM{household_income} and monthly expesnes of RM{monthly_expenses} affording the following loans. Provide professional financial advice on whether or not they should take these loans. Consider the change in disposal income from RM{'{:.2f}'.format(initial_disposal)} in {initial_date[1]}/{initial_date[0]} to RM{'{:.2f}'.format(final_disposal)} in {final_date[1]}/{final_date[0]} after accounting for inflation.\n"

        for loanData in self.loans_from_user:
            prompt += f"{loanData['name']} "
            prompt += f"Date: {loanData['sym']} "
            prompt += f"Loan Value: RM{loanData['loan']} "
            prompt += f"Interest Rate: {loanData['interest']}% "
            prompt += f"Installment Period: {loanData['installment']} months\n"

        prompt += "Analyze the financial impact of these loans on the individual's budget, considering the gradual reduction in dosposable income and the long-term implications of managing these loans alongside other living expenses. Don't give additional number analysis and calculations, just paragraph of words and only in one short paragraphs"
        print(prompt)

        answer = bard.get_answer(prompt)
        self.bard_ouput = answer['content']
