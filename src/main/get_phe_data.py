# Imports
import pandas as pd
import fingertips_py as ftp
from pathlib import Path

from src.flask.settings import RUNNING_LOCALLY

# Indicator ID 848 refers to Depression: Recorded prevalence (aged 18+)
# Indicator ID 273 refers to Chronic Heart Disease prevalence

# area_type_id = 15 in England
# area_type_id = 113 is parliamentary constituencies


def data_paths(indicator):

    if RUNNING_LOCALLY:
        # Make sure the required path exists. Create it if not.
        Path("../../data/json/phe").mkdir(parents=True, exist_ok=True)

        phe_data_path = Path("../../data/json/phe/{}_DATA".format(indicator))
        phe_meta_path = Path("../../data/json/phe/{}_META".format(indicator))
        all_data_path = Path("../../data/json/phe/{}_ALL_DATA".format(indicator))
    else:
        # Make sure the required path exists. Create it if not.
        Path("coronavirus-webapp/data/json/phe").mkdir(parents=True, exist_ok=True)

        phe_data_path = Path("coronavirus-webapp/data/json/phe/{}_DATA".format(indicator))
        phe_meta_path = Path("coronavirus-webapp/data/json/phe/{}_META".format(indicator))
        all_data_path = Path("coronavirus-webapp/data/json/phe/{}_ALL_DATA".format(indicator))

    return phe_data_path, phe_meta_path, all_data_path


def check_data_exists(indicator):
    """
    Check is local JSON files exist for the indicator.
    :param indicator:
    :return:
    """

    phe_data_path, phe_meta_path, all_data_path = data_paths(indicator)

    # Re-download the data if both data and meta data files do not exist.
    if phe_data_path.is_file() and phe_meta_path.is_file():
        get_data = True
        meta = True

    else:
        get_data = False
        meta = False

    # All data is not strictly needed, so if this doesn't exist we're not too bothered.
    if all_data_path.is_file():
        all_data = True

    else:
        all_data = False

    return get_data, meta, all_data


def get_data_from_json(path):
    """
    As named...
    :param pathlib.Path path:
    :return:
    """
    return pd.read_json(path)


def get_data(indicator, england_only=True, keep_cols=None, dev=False, use_json=True):

    """
    Get data from the fingertips api. If write_json is false, then try to not query the API and read locally.
    :param indicator:
    :param england_only:
    :param keep_cols:
    :param dev:
    :param use_json:
    :return:
    """

    if use_json is True:
        phe_data_path, phe_meta_path, all_data_path = data_paths(indicator)
        check_data, check_meta, check_all = check_data_exists(indicator)

        # Make sure both data and metadata exists. Otherwise, re-download them.
        if check_data is True and check_meta is True:
            get_data = get_data_from_json(phe_data_path)
            meta = get_data_from_json(phe_meta_path)

            # All data is not strictly needed, so if that doesn't exist, just continue.
            if check_all is True:
                all_data = get_data_from_json(all_data_path)
            else:
                all_data = None
            print("using json...")

            return get_data, meta, all_data

        else:
            print("Required JSON files do not exist. Downloading data from PHE.")

    # There is an 'England' area code in the data, so just use that flag
    print("use JSON didn't work")
    if england_only is True:
        get_data = ftp.retrieve_data.get_all_data_for_indicators(indicators=indicator, area_type_id=15)

    #     There seems to be some cases where a valid indicator and area id can return an empty df...
        if get_data.empty:
            get_data = ftp.retrieve_data.get_data_for_indicator_at_all_available_geographies(indicator)
            get_data = get_data.loc[get_data['Area Type'].str.upper() == 'ENGLAND']

            if get_data.empty:
                raise ValueError("No data returned from fingertips."
                                 " You have probably specified an invalid indicator ID.")

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

    # For Development, keep all of the columns available too.
    if dev is True:
        print("Running function get_data in dev mode")
        all_data = get_data.copy().reset_index(drop=True)
    else:
        all_data = pd.DataFrame()

    get_data = get_data.loc[:, keep_cols].reset_index(drop=True)

    write_data_to_json(get_data, "{}_DATA".format(indicator))
    write_data_to_json(meta, "{}_META".format(indicator))
    write_data_to_json(all_data, "{}_ALL_DATA".format(indicator))

    return get_data, meta, all_data


def extract_summary_figure(data, json = False):
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

    if json is True:
        return max_counts.to_json()
    else:
        return max_counts


def explore_profile_data(profile_id):

    """
    This is an easier way to find some interesting indicators to explore.
    :param profile_id: PHE Fingertips profile ID
    :return: Unique indicators IDs and Names for a given profile
    """

    # Some useful profile IDs
    # 40 - Common mental health disorders
    # 135 - Cardiovascular disease

    profile_data = ftp.retrieve_data.get_all_data_for_profile(profile_id)

    if profile_data.empty:
        raise ValueError("Data returned by Fingertips is empty. Possible profile_id is invalid.")

    unique = profile_data.drop_duplicates('Indicator ID').sort_values(by='Indicator ID')

    return unique


def get_figure_for_flask(data):
    """
    Get the single figure we want to display on the webpage.
    Pass the result of extract_summary_figure() into this function.
    :param data: return from extract_summary_figure()
    :return: Most recent figure for data
    """

    def sort_fn(elem):
        """
        Function to use as key in sorting data to ensure we can get the latest data
        :param elem:
        :return:
        """
        return elem.split('/')[1]

    # Make sure the data is sorted by year, so we can then assume the last element is the most recent
    time_periods = sorted(data['Time period'].tolist(), key=sort_fn)
    most_recent_year = time_periods[-1]

    most_recent_data = data.loc[data['Time period'] == most_recent_year, :]

    # return f"{int(most_recent_data.iloc[0].loc['Count']):,}"
    return int(most_recent_data.iloc[0].loc['Count'])


def write_data_to_json(data, name):
    """
    Take the PHE DataFrame and save to JSON so we don't have to query the (slow) PHE API every time.
    :param data: data to write
    :param name: file name, including extension
    :return: None
    """

    if data.empty:
        return "Empty df passed. Nothing will be written."

    # TODO: Regex check for invalid file name.
    if RUNNING_LOCALLY:
        OUT_PATH = "../../data/json/phe/{}"
    else:
        OUT_PATH = "coronavirus-webapp/data/json/phe/{}"

    data.to_json(OUT_PATH.format(name))


def get_heart_data():
    heart_data, heart_meta, all_data = get_data(273, dev=True, england_only=True, use_json=True)
    summary_heart = extract_summary_figure(heart_data, json=False)
    return get_figure_for_flask(summary_heart)


def get_depression_data():
    depression_data, depression_meta, all_depression = get_data(848, dev=True, england_only=True, use_json=True)
    summary_depression = extract_summary_figure(depression_data, json=False)
    return get_figure_for_flask(summary_depression)


def get_domestic_abuse_data():
    domestic_abuse, dom_meta, dom_all = get_data(92863, dev=True, england_only=True, use_json=True)
    summary_domestic = extract_summary_figure(domestic_abuse, json=False)
    return get_figure_for_flask(summary_domestic)


def get_phe_data_for_flask(indicator, dev=True):
    if type(indicator) is not int:
        raise TypeError("Indicator ID must be an integer, not {}".format(type(indicator)))

    data, meta, all_data = get_data(indicator, dev=dev, england_only=True, use_json=True)
    summary_data = extract_summary_figure(data, json=False)
    return get_figure_for_flask(summary_data)
