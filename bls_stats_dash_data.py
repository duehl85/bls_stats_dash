import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Read BLS API key from environment (set as a GitHub secret)
BLS_API_KEY = os.environ.get('BLS_API_KEY')

# create dictionary of the series that will be utilized
series_ids = {
    "Total Non-Farm Workers": "CEU0000000001",
    "Unemployment Rates": "LNS14000000",
    "Average Hourly Earnings": "CES0500000003",
    "National Unemployment Rate": "LNS14000000",
    "Men Unemployment Rate (20+)": "LNS14000006",
    "Women Unemployment Rate (20+)": "LNS14000007",
    "Black or African American Unemployment Rate": "LNS14000003",
    "Hispanic or Latino Unemployment Rate": "LNS14000009",
    "Long-Term Unemployment (27 weeks or more)": "LNS13008756",
    "Underemployment Rate (U-6)": "LNS13327709",
    "Youth Unemployment Rate (16-24)": "LNU04000012",
    "Labor Force Participation Rate": "LNS11300000",
    "Discouraged Workers": "LNS15026645"
}

CSV_FILENAME = "bls_data.csv"


def fetch_bls_data(series_list, start_year, end_year, bls_key):
    url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    headers = {'Content-type': 'application/json'}
    data = {
        "seriesid": series_list,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": bls_key
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    json_data = response.json()

    if json_data.get('status') == 'REQUEST_NOT_PROCESSED':
        raise ValueError(f"Error from BLS API: {json_data.get('message')}")
    return json_data


def bls_response_to_df(json_data, series_map):
    records = []
    for s in json_data['Results']['series']:
        series_id = s['seriesID']
        name = [k for k, v in series_map.items() if v == series_id]
        name = name[0] if name else series_id
        for entry in s['data']:
            period = entry['period']  # e.g. 'M11'
            if period.startswith('M'):
                year = entry['year']
                month_str = period[1:]
                date_str = f"{year}-{month_str}-01"
                date = datetime.strptime(date_str, "%Y-%m-%d")
                value = float(entry['value'])
                records.append([date, series_id, name, value])
    df = pd.DataFrame(records, columns=['date', 'series_id', 'series_name', 'value'])
    df.sort_values(by='date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_next_month(date):
    """Given a datetime (always first of month in our case), return the datetime for the next month."""
    year = date.year
    month = date.month
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    return datetime(next_year, next_month, 1)


if __name__ == "__main__":
    if not os.path.exists(CSV_FILENAME):
        # Initial run: Fetch data from November 2023 to November 2024
        # We'll fetch entire years 2023 and 2024 and then filter.
        initial_data = fetch_bls_data(list(series_ids.values()), 2023, 2024, BLS_API_KEY)
        df = bls_response_to_df(initial_data, series_ids)

        start_date = datetime(2023, 11, 1)
        end_date = datetime(2024, 11, 1)
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        df.to_csv(CSV_FILENAME, index=False)
        print("Initial data fetched and saved.")
    else:
        # Subsequent runs: Fetch the next month's data after the last recorded date
        existing_df = pd.read_csv(CSV_FILENAME, parse_dates=['date'])
        latest_date = existing_df['date'].max()  # last month in the CSV

        # Determine next month to fetch
        next_month_date = get_next_month(latest_date)
        start_year = next_month_date.year
        end_year = next_month_date.year

        # Fetch the data for that year
        new_data_json = fetch_bls_data(list(series_ids.values()), start_year, end_year, BLS_API_KEY)
        new_df = bls_response_to_df(new_data_json, series_ids)

        # Filter to the target month only
        new_df = new_df[new_df['date'] == next_month_date]

        if not new_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=['date', 'series_id'], inplace=True)
            combined_df.sort_values(by='date', inplace=True)
            combined_df.to_csv(CSV_FILENAME, index=False)
            print(f"Data updated with new month: {next_month_date.strftime('%B %Y')}")
        else:
            print("No new data found for the next month. Data file is up-to-date.")
