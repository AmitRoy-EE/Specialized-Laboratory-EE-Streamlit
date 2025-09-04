import pandas as pd
import json


def load_default_pv_cf():
    """Load default PV capacity factor data"""
    return pd.read_csv(
        "input_data/hourly_pv_cf.csv",
        dtype={"pv_cf": float},
        parse_dates=["date_time"],
    )


def load_default_electricity_demand():
    """Load default electricity demand profiles"""
    return pd.read_csv(
        "input_data/hourly_electricity_demands_kWh (family, 2-working-persons, 1 pensioneer).csv",
        dtype={"profile_1": float, "profile_2": float, "profile_3": float},
        parse_dates=["date_time"],
    )


def load_default_electricity_price():
    """Load default electricity price data"""
    return pd.read_csv(
        "input_data/hourly_electricity_price.csv",
        dtype={"electricity_price": float},
        parse_dates=["date_time"],
    )


def load_default_co2_emissions():
    """Load default CO2 emissions data"""
    return pd.read_csv(
        "input_data/hourly_co2-emissions.csv",
        dtype={"CO2_emissions": float},
        parse_dates=["date_time"],
    )


def load_json(file_path):
    """Load JSON file"""
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def load_operating_strategy(strategy_name):
    """Load operating strategy based on selection"""
    if strategy_name == "Reference":
        os = load_json("operating_strategies/reference.json")
        return json.dumps(os, indent=4)

    elif strategy_name == "No battery":
        os = load_json("operating_strategies/no_battery.json")
        return json.dumps(os, indent=4)

    elif strategy_name == "Custom":
        os = load_json("operating_strategies/reference.json")
        # Added newline to ensure reload happens if custom_os and reference_os are identical
        return json.dumps(os, indent=4) + "\n"


def load_custom_pv_cf(uploaded_file, separator):
    """Process uploaded PV capacity factor data"""
    try:
        uploaded_pv_cf = pd.read_csv(uploaded_file, sep=separator, engine="python")
        if len(uploaded_pv_cf) != 168:
            return (
                None,
                f"Failed to apply times series: Please provide exactly 168 value rows. Found {len(uploaded_pv_cf)} rows with values.",
            )
        elif not all(col in ["date_time", "pv_cf"] for col in uploaded_pv_cf.columns):
            return (
                None,
                f"Failed to apply times series: Please rename the columns to match ['date_time'{separator}  'pv_cf']! Found {uploaded_pv_cf.columns.to_list()}.",
            )
        else:
            return uploaded_pv_cf, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def load_custom_load_profile(uploaded_file, separator):
    """Process uploaded load profile data"""
    try:
        uploaded_load_profile = pd.read_csv(uploaded_file, sep=separator, engine="python")
        if len(uploaded_load_profile) != 168:
            return None, f"Please provide exactly 168 value rows. Found {len(uploaded_load_profile)} rows with values."
        elif not all(col in ["date_time", "profile_1"] for col in uploaded_load_profile.columns):
            return (
                None,
                f"Please rename the columns to match ['date_time'{separator}  'profile_1']! Found {uploaded_load_profile.columns.to_list()}.",
            )
        else:
            return uploaded_load_profile, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def load_custom_elec_price(uploaded_file, separator):
    """Process uploaded electricity price data"""
    try:
        uploaded_elec_price = pd.read_csv(uploaded_file, sep=separator, engine="python")
        if len(uploaded_elec_price) != 168:
            return None, f"Please provide exactly 168 value rows. Found {len(uploaded_elec_price)} rows with values."
        elif not all(col in ["date_time", "electricity_price"] for col in uploaded_elec_price.columns):
            return (
                None,
                f"Please rename the columns to match ['date_time'{separator}  'electricity_price']! Found {uploaded_elec_price.columns.to_list()}.",
            )
        else:
            return uploaded_elec_price, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"


def load_custom_co2_emissions(uploaded_file, separator):
    """Process uploaded CO2 emissions data"""
    try:
        uploaded_co2_emissions = pd.read_csv(uploaded_file, sep=separator, engine="python")
        if len(uploaded_co2_emissions) != 168:
            return None, f"Please provide exactly 168 value rows. Found {len(uploaded_co2_emissions)} rows with values."
        elif not all(col in ["date_time", "CO2_emissions"] for col in uploaded_co2_emissions.columns):
            return (
                None,
                f"Please rename the columns to match ['date_time'{separator}  'CO2_emissions']! Found {uploaded_co2_emissions.columns.to_list()}.",
            )
        else:
            return uploaded_co2_emissions, None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"
