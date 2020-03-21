# Imports
import pandas as pd
import fingertips_py as ftp
from pprint import pprint

# Indicator ID 848 refers to Depression: Recorded prevalence (aged 18+)
# Indicator ID 273 refers to Chronic Heart Disease prevalence

# area_type_id = 15 in England
# area_type_id = 113 is parliamentary constituencies

def get_data(indicator, england_only = True, keep_cols = None, dev = False):
    # There is an 'England' area code in the data, so just use that flag
    if england_only is True:
        get_data = ftp.retrieve_data.get_all_data_for_indicators(indicators=indicator, area_type_id=15)

    #     There seems to be some cases where a valid indicator and area id can return an empty df...
        if get_data.empty:
            get_data = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies(indicator)
            get_data = get_data.loc[get_data['Area Type'].str.upper() == 'ENGLAND']

    else:
        get_data = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies(indicator)

    meta = ftp.get_metadata_for_indicator_as_dataframe(indicator)

    # Remove any rows that don't have a value
    get_data = get_data.loc[~get_data['Value'].isna(), :]


    if keep_cols is None:
        keep_cols = ['Indicator ID', 'Indicator Name', 'Sex', 'Age', 'Time period', 'Value', 'Value note', 'Count', 'Denominator']
    else:
        if not isinstance(keep_cols, list):
            raise TypeError("Columns to keep must be passed as a list.")

    # TODO: For Development, keep all of the columns available too.
    if dev is True:
        print("Running function get_data in dev mode")
        all_data =  get_data.copy()
    else:
        all_data = None

    get_data = get_data.loc[:, keep_cols].reset_index(drop=True)

    return get_data, meta, all_data


def extract_summary_figure(data):
    time_periods = data['Time period'].unique()

    # There seems to be a summary figure for the metrics with no category for each time period, so extract this and ignore
    # other data for now
    max_counts = pd.DataFrame()

    for period in time_periods:
        period_data = data.loc[data['Time period'] == period, :].drop_duplicates().reset_index(drop=True)

        # The row with the greatest denominator should be the one that has considered all the data...this is an (unverified)
        # assumption
        if len(period_data) > 1:
            max_idx = period_data['Denominator'].idxmax()
            period_data = period_data.iloc[max_idx, :]

        max_counts = max_counts.append(period_data)

    max_counts = max_counts.reset_index(drop=True)

    return max_counts


heart_data, heart_meta, all_data = get_data(273, dev=True, england_only=True)
summary_heart = extract_summary_figure(heart_data)

depression_data, depression_meta, all_depression = get_data(848, dev=True, england_only=True)
summary_depression = extract_summary_figure(depression_data)

