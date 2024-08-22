import pickle

def prediction(start_date, end_date):
    with open('sarima_auto_bridge_opn_issues.pkl', 'rb') as file:
        model = pickle.load(file)

    # Specify the start and end dates for the forecast and call the loaded model to get the confidences

    # start_date = '2025-04-01'
    # end_date = '2025-04-30'

    # Forecast between the given dates
    forecast = model.get_prediction(start=start_date, end=end_date)

    # Retrieve the predicted mean values
    forecast_values = forecast.predicted_mean

    # Optionally, get confidence intervals
    # conf_int = forecast.conf_int()

    # print(forecast_values)
    # print(conf_int)

    # We shall take a threshold of 0.25 and anything above it would mean the incident would happen
    forecast_yn = forecast_values.apply(lambda x: 1 if x >= 0.25 else 0)

    # finally, filter the dates to a list for ease of display.
    incident_dates = forecast_yn[forecast_yn == 1].index.strftime('%Y-%m-%d').tolist()

    return incident_dates
