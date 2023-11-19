import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

import tensorflow as tf
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, InputLayer, concatenate, Input, LSTM
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import plot_model

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from statsmodels.tsa.seasonal import seasonal_decompose


def read_gov_data(URL_LINK):
    df = pd.read_parquet(URL_LINK)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    return df


def find_date_range(datasets):
    # Ensure that all datasets have a datetime index
    for df in datasets:
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("All datasets must have a datetime index.")

    # Find the maximum start date
    max_start_date = max(df.index.min() for df in datasets)

    # Find the minimum end date
    min_end_date = min(df.index.max() for df in datasets)

    return max_start_date, min_end_date


URL_ECON_INDICATOR = 'https://storage.dosm.gov.my/econindicators/economic_indicators.parquet'
URL_CPI = 'https://storage.dosm.gov.my/cpi/cpi_headline.parquet'
URL_IPI = 'https://storage.dosm.gov.my/ipi/ipi.parquet'
URL_PPI = 'https://storage.dosm.gov.my/ppi/ppi.parquet'
URL_LABOUR = 'https://storage.dosm.gov.my/labour/labourforce_monthly.parquet'

econ_indicator_df = read_gov_data(URL_ECON_INDICATOR)
cpi_df = read_gov_data(URL_CPI)
ipi_df = read_gov_data(URL_IPI)
ppi_df = read_gov_data(URL_PPI)
lfs_df = read_gov_data(URL_LABOUR)

start_date, end_date = find_date_range(
    [econ_indicator_df, cpi_df, ppi_df, ipi_df])


def get_col_from(df, column):
    return df[column][(df.index >= start_date) & (df.index <= end_date)]


def read_data():
    data = pd.DataFrame()
    data["cpi_overall"] = get_col_from(cpi_df, "overall")

    data["ipi_overall"] = get_col_from(ipi_df, "overall")
    data["ipi_mfg"] = get_col_from(ipi_df, "mfg")
    data["ipi_elec"] = get_col_from(ipi_df, "electric")

    data["ppi_agri"] = get_col_from(ppi_df, "agriculture")
    data["ppi_mining"] = get_col_from(ppi_df, "mining")
    data["ppi_mfg"] = get_col_from(ppi_df, "manufacturing")
    data["ppi_elec"] = get_col_from(ppi_df, "electricity")
    data["ppi_water"] = get_col_from(ppi_df, "water")
    data["ppi_overall"] = get_col_from(ppi_df, "overall")

    data["labour_unemployed"] = get_col_from(lfs_df, "unemployed")
    data["labour_employed"] = get_col_from(lfs_df, "employed")

    data["cpi_trend"] = seasonal_decompose(
        data["cpi_overall"], model='additive', period=12).trend
    data['cpi_trend'].fillna(method='ffill', inplace=True)
    data['cpi_trend'].fillna(method='bfill', inplace=True)

    data["ipi_trend"] = seasonal_decompose(
        data["ipi_overall"], model='additive', period=12).trend
    data['ipi_trend'].fillna(method='ffill', inplace=True)
    data['ipi_trend'].fillna(method='bfill', inplace=True)

    data["ppi_trend"] = seasonal_decompose(
        data["ppi_overall"], model='additive', period=12).trend
    data['ppi_trend'].fillna(method='ffill', inplace=True)
    data['ppi_trend'].fillna(method='bfill', inplace=True)

    data["labour_unemployed_trend"] = seasonal_decompose(
        data["labour_unemployed"], model='additive', period=12).trend
    data['labour_unemployed_trend'].fillna(method='ffill', inplace=True)
    data['labour_unemployed_trend'].fillna(method='bfill', inplace=True)

    data["labour_employed_trend"] = seasonal_decompose(
        data["labour_employed"], model='additive', period=12).trend
    data['labour_employed_trend'].fillna(method='ffill', inplace=True)
    data['labour_employed_trend'].fillna(method='bfill', inplace=True)
    return data


data = read_data()

train_ratio = 0.6
val_ratio = 0.2
test_ratio = 0.2
# @title Loading data for model

# input_columns =  [
#     'cpi_overall',
#     'ppi_overall',
#     'ipi_overall',
#     'labour_employed',
#     'labour_unemployed',
# ]
input_columns = [
    'cpi_trend',
    'ppi_trend',
    'ipi_trend',
    'labour_employed_trend',
    'labour_unemployed_trend',
]
target_column = ['cpi_overall']
target_forecast_months = [3, 6, 9, 12]
max_forecast_months = max(target_forecast_months)

X, y = [], []
for i in range(len(data) - max_forecast_months):
    X.append(data[input_columns].iloc[i])
    y.append([data[target_column].iloc[i+j][0]
             for j in target_forecast_months])
X = np.array(X)
y = np.array(y)

train_size = int(len(X) * train_ratio)
val_size = int(len(X) * val_ratio)
test_size = int(len(X) * test_ratio)

val_size_cum = train_size + val_size
test_size_cum = len(X)

print("Train : " + str(train_size))
print("Val : " + str(val_size) + ", cumulative : " + str(val_size_cum))
print("Test : " + str(test_size) + ", cumulative : " + str(test_size_cum))

X_train_total, y_train_total = X[: val_size_cum], y[: val_size_cum]
X_train, X_val, y_train, y_val = train_test_split(
    X_train_total, y_train_total, test_size=val_ratio, random_state=42)
X_test, y_test = X[val_size_cum:], y[val_size_cum:]

scaler_x = StandardScaler()
X_train_total_scaled = scaler_x.fit_transform(X_train_total)
X_train_scaled = scaler_x.fit_transform(X_train)
X_val_scaled = scaler_x.transform(X_val)
X_test_scaled = scaler_x.transform(X_test)

scaler_y = StandardScaler()

y_train_total_scaled = scaler_y.fit_transform(y_train_total)
y_train_scaled = scaler_y.fit_transform(y_train)
y_val_scaled = scaler_y.transform(y_val)
y_test_scaled = scaler_y.transform(y_test)

input_shape = (X_train_scaled.shape[1], )
output_shape = len(target_forecast_months)

print("Train X shape : " + str(X_train_scaled.shape))
print("Train Y shape : " + str(y_train_scaled.shape))
print("Val X shape : " + str(X_val_scaled.shape))
print("Val Y shape : " + str(y_val_scaled.shape))
print("Test X shape : " + str(X_test_scaled.shape))
print("Test Y shape : " + str(y_test_scaled.shape))

model = load_model("./pynecone/model/my_model_3_6_9_12.h5")

selected_forecast_levels = [3]


def forecast_future_CPI(start_year: int, start_month: int, num_of_months: int):
    start_month = str(start_year) + "-" + str(start_month).rjust(2, "0")
    date_range = pd.date_range(start_month, freq='MS', periods=num_of_months)
    # date_range = create_date_range(start_year, start_month, num_of_months)

    data = read_data()
    model = load_model("./pynecone/model/my_model_3_6_9_12.h5")

    input_date = date_range[0]
    inputs = data.loc[input_date][input_columns]
    inputs_scaled = scaler_x.transform([inputs.array, ])

    forecast_scaled = model.predict(inputs_scaled, verbose=0)
    forecast = scaler_y.inverse_transform(forecast_scaled)[0]

    cpi_over_time = []
    initial_val = data.loc[input_date][target_column].array[0]
    previous_start_val = initial_val
    previous_months_count = 0

    for i in range(0, len(selected_forecast_levels)):
        months_count = selected_forecast_levels[i] - previous_months_count
        forecast_val = forecast[i]

        monthly_increment = (forecast_val - previous_start_val) / months_count

        for j in range(months_count):
            cpi_over_time.append(previous_start_val + (monthly_increment * j))

        previous_start_val = forecast_val
        previous_months_count = selected_forecast_levels[i]

    if len(cpi_over_time) > num_of_months:
        cpi_over_time = cpi_over_time[:num_of_months]
    else:
        monthly_increment = (max(forecast) - initial_val) / len(cpi_over_time)
        for i in range(len(cpi_over_time), num_of_months):
            cpi_over_time.append(cpi_over_time[-1] + monthly_increment)

    previous_cpi = initial_val
    inflation_over_time = []
    for cpi in cpi_over_time:
        old_cpi = previous_cpi
        new_cpi = cpi

        inflation = ((new_cpi - old_cpi) / old_cpi) * 100
        inflation_over_time.append(inflation)

        previous_cpi = new_cpi

    return inflation_over_time
