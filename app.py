import streamlit as st
import pandas as pd
import json
from io import StringIO
from visualisation import (
    plot_demand_and_pv_generation,
    plot_elec_price_and_CO2_emissions,
    compute_and_plot_costs,
    compute_and_plot_emissions,
    show_latex_table,
    plot_energy_flow_diagram,
    plot_energy_balance,
)
from data_processing import (
    load_default_pv_cf,
    load_default_electricity_demand,
    load_default_electricity_price,
    load_default_co2_emissions,
    load_operating_strategy,
    load_custom_pv_cf,
    load_custom_load_profile,
    load_custom_elec_price,
    load_custom_co2_emissions,
)
from utils import safe_execute, parse_json_strategy, check_energy_balance, calculate_electricity_price

# write simulation results to results folder True/False
# can be used to check integrity of simulation for the default parameter set (currently 6 kW, 12 kWh, additional costs applied)
write_results_to_file = False

st.set_page_config(
    page_title="Lab A",
    layout="wide",
)

# Load default data
default_pv_cf = load_default_pv_cf()
default_electricity_demand = load_default_electricity_demand()
default_electricity_price = load_default_electricity_price()
default_co2_emissions = load_default_co2_emissions()

# Start of streamlit functions
image_container = st.container()
image_container_col1, image_container_col2, image_container_col3 = image_container.columns([1, 2, 1])

with image_container_col1:
    st.markdown("# Fachlabor EE")
    st.markdown(
        """
        This app simulates the operation of a household energy system with a battery storage system.
        It is developed and used as part of the teaching lab "Optimal operation and sizing of a residential PV storage system" at Ruhr University Bochum.
        For further information download the script below.
        """
    )

    with open("Teaching_lab___Storage_operation.pdf", "rb") as pdf_script:
        PDFScriptbyte = pdf_script.read()

    st.download_button(
        label="Download Script",
        data=PDFScriptbyte,
        file_name="Teaching_lab___Storage_operation.pdf",
        mime='application/octet-stream'
    )

    example_csv_files = {
        "hourly_electricity_price.csv": "input_data/hourly_electricity_price.csv",
        "hourly_co2-emissions.csv": "input_data/hourly_co2-emissions.csv",
        "hourly_electricity_demands_kWh.csv": "input_data/hourly_electricity_demands_kWh_upload_example.csv",
        "hourly_pv_cf.csv": "input_data/hourly_pv_cf.csv",
    }

    with st.expander("Download custom input examples"):
        for file_name, file_path in example_csv_files.items():
            try:
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    st.download_button(
                        label=f"Download {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime="text/csv",
                    )
            except FileNotFoundError:
                st.warning(f"File not found: {file_path}")

    separator_radio = st.radio(
        "Select preferred separator for .csv input files:",
        [",", ";"],
        captions=[
            "comma",
            "semicolon",
        ],
    )

with image_container_col2:
    st.image(
        "images/second_draft_household.png",
        caption="Figure 0: Scheme of the energy system household. The demand node is depicted as a circle, the units and the grid as icons and connecting lines are shown as arrows.",
        use_column_width=True,
    )


container1 = st.container()

c1col1, c1col2 = container1.columns(2)

with c1col1:
    st.markdown("# 1. Time series data for generation and demand")
    pv_cf_radio = st.radio(
        "Select time series for PV capacity factor:",
        ["Use default", "Use own"],
        captions=[
            "Use preloaded data [1].",
            "Upload your own data.",
        ],
    )
    if pv_cf_radio == "Use default":
        pv_cf_series = default_pv_cf["pv_cf"]
        date_time = default_pv_cf["date_time"]
    elif pv_cf_radio == "Use own":
        uploaded_file1 = st.file_uploader(
            f"Upload a CSV-file: The input file must contain 1 row with the column names ['date_time'{separator_radio} 'pv_cf'] and 168 rows of data (1 row per hour). This resembles a one-week's data series.",
            type=["csv"],
            key="pv_cf_uploader",
        )

        if uploaded_file1 is not None:
            uploaded_pv_cf, error_msg = load_custom_pv_cf(uploaded_file1, separator_radio)
            if error_msg:
                st.error(error_msg)
                uploaded_pv_cf = None

            if uploaded_pv_cf is None:
                pv_cf_series = default_pv_cf["pv_cf"]
                date_time = default_pv_cf["date_time"]
            else:
                pv_cf_series = uploaded_pv_cf["pv_cf"]
                date_time = default_pv_cf["date_time"]
        else:
            pv_cf_series = default_pv_cf["pv_cf"]
            date_time = default_pv_cf["date_time"]

    pv_cf = pv_cf_series

    # Initialize session state for own capacity of the PV installation
    if "own_pv_capacity" not in st.session_state:
        st.session_state.own_pv_capacity = None

    # Define a callback function to reset the own capacity of the PV installation
    def reset_own_pv_capacity():
        st.session_state.own_pv_capacity = None

    radio_pv_capacity = st.radio(
        "Select the capacity of the PV installation [kW]:", [3, 6, 9], index=1, on_change=reset_own_pv_capacity
    )

    own_pv_capacity_value = st.number_input(
        "Define your own capacity of the PV installation [kW]:",
        value=st.session_state.own_pv_capacity,
        key="own_pv_capacity",
    )

    if st.session_state.own_pv_capacity is None:
        pv_generation = radio_pv_capacity * pv_cf  # type: ignore
        str_pv_cap = radio_pv_capacity
    else:
        pv_generation = own_pv_capacity_value * pv_cf  # type: ignore
        str_pv_cap = own_pv_capacity_value

    pv_generation = pv_generation.rename("P_pv")

    default_load_profile_radio = st.radio(
        "Select your preferred default load profile [2]:",
        ["Profile 1", "Profile 2", "Profile 3"],
        captions=[
            "One full-time and one part-time working person with three children.",
            "One full-time and one part-time working person.",
            "One pensioner.",
        ],
    )

    if default_load_profile_radio == "Profile 1":
        electricity_demand = default_electricity_demand["profile_1"]
        str_profile = "P1"
    elif default_load_profile_radio == "Profile 2":
        electricity_demand = default_electricity_demand["profile_2"]
        str_profile = "P2"
    elif default_load_profile_radio == "Profile 3":
        electricity_demand = default_electricity_demand["profile_3"]
        str_profile = "P3"

    use_own_load_profiles_check = st.checkbox("Use own load profiles (e.g. Shelly Plug time series)")

    if use_own_load_profiles_check:
        st.write(
            "Please provide the data in Watt [W] (this is the default for Shelly Plug data). Conversion to [kW] is done automatically after uploading."
        )
        st.write(
            "After the upload you can select if you want to use the provided data as standalone or to add it to the selected default load profile."
        )

        uploaded_file2 = st.file_uploader(
            f"Upload a CSV-file: The input file must contain 1 row with the column names [date_time{separator_radio} load] and 168 rows of data (1 row per hour). This resembles a one-week's data series.",
            type=["csv"],
            key="own_load_profiles_uploader",
        )

        if uploaded_file2 is not None:
            uploaded_load_profile, error_msg = load_custom_load_profile(uploaded_file2, separator_radio)
            if error_msg:
                st.error(error_msg)
                uploaded_load_profile = None

            if uploaded_load_profile is not None:
                uploaded_demand = uploaded_load_profile["load"]
                uploaded_demand_selectbox = st.selectbox(
                    "How would you like to use the uploaded profile?",
                    ("Standalone", "Combine with default load profile"),
                )
                units_own_load_profile_radio = st.radio(
                    "Select the units of the uploaded profile:",
                    ["**[W] (Recommended for Shelly Plug data)**", "**[kW]**"],
                )
                if uploaded_demand_selectbox == "Standalone":
                    str_own_load = "S"
                    if units_own_load_profile_radio == "**[W] (Recommended for Shelly Plug data)**":
                        electricity_demand = uploaded_demand / 1000
                    else:
                        electricity_demand = uploaded_demand

                elif uploaded_demand_selectbox == "Combine with default load profile":
                    str_own_load = "C"
                    if units_own_load_profile_radio == "**[W] (Recommended for Shelly Plug data)**":
                        electricity_demand = electricity_demand + uploaded_demand / 1000
                    else:
                        electricity_demand = electricity_demand + uploaded_demand

    electricity_demand = electricity_demand.rename("P_load")


with c1col2:
    st.markdown(
        """
        <style>
        [data-testid="column"]:nth-of-type(2) > div {
            position: sticky;
            top: 50px;
            height: 100vh;
            overflow-y: auto;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ##### Please note: The y-axis range in the figure gets rescaled as the values are changed.
        """
    )

    plot_demand_and_pv_generation(date_time, electricity_demand, pv_generation)

st.markdown("___")

container2 = st.container()

c2col1, c2col2 = container2.columns(2)

with c2col1:
    st.markdown("# 2. Time series data for electricity price and CO₂ emissions")

    st.markdown("Input electricity price parameters:")

    taxes_and_fees = st.number_input(
        "Taxes and fees [ct/kWh]:",
        value=5,
    )

    grid_fees = st.number_input(
        "Grid fees [ct/kWh]:",
        value=12,
    )

    st.markdown("VAT (**V**alue-**A**dded **T**ax) of 19% will be applied")

    apply_additional_costs = st.checkbox("Apply additional costs.")

    elec_price_radio = st.radio(
        "Select time series for electricity price:",
        ["Use default", "Use own"],
        captions=[
            "Use preloaded data [3].",
            "Upload your own data.",
        ],
    )
    if elec_price_radio == "Use default":
        electricity_wholesale_price = default_electricity_price["electricity_price"]
    elif elec_price_radio == "Use own":
        uploaded_file3 = st.file_uploader(
            f"Upload a CSV-file: The input file must contain 1 row with the column names ['date_time'{separator_radio} 'electricity_price'] and 168 rows of data (1 row per hour). This resembles a one-week's data series.",
            type=["csv"],
            key="elec_price_uploader",
        )

        if uploaded_file3 is not None:
            uploaded_elec_price, error_msg = load_custom_elec_price(uploaded_file3, separator_radio)
            if error_msg:
                st.error(error_msg)
                uploaded_elec_price = None

            if uploaded_elec_price is None:
                electricity_wholesale_price = default_electricity_price["electricity_price"]
            else:
                electricity_wholesale_price = uploaded_elec_price["electricity_price"]
        else:
            electricity_wholesale_price = default_electricity_price["electricity_price"]

    electricity_price_customer = calculate_electricity_price(
        electricity_wholesale_price, apply_additional_costs, taxes_and_fees, grid_fees
    )

    st.markdown("___")
    CO2_emissions_radio = st.radio(
        "Select time series for CO₂ emissions:",
        ["Use default", "Use own"],
        captions=[
            "Use preloaded data [3].",
            "Upload your own data.",
        ],
    )
    if CO2_emissions_radio == "Use default":
        CO2_emissions_specific = default_co2_emissions["CO2_emissions"]
    elif CO2_emissions_radio == "Use own":
        uploaded_file4 = st.file_uploader(
            f"Upload a CSV-file: The input file must contain 1 row with the column names ['date_time'{separator_radio} 'CO2_emissions'] and 168 rows of data (1 row per hour). This resembles a one-week's data series.",
            type=["csv"],
            key="CO2_emissions_uploader",
        )

        if uploaded_file4 is not None:
            uploaded_co2_emissions, error_msg = load_custom_co2_emissions(uploaded_file4, separator_radio)
            if error_msg:
                st.error(error_msg)
                uploaded_co2_emissions = None

            if uploaded_co2_emissions is None:
                CO2_emissions_specific = default_co2_emissions["CO2_emissions"]
            else:
                CO2_emissions_specific = uploaded_co2_emissions["CO2_emissions"]
        else:
            CO2_emissions_specific = default_co2_emissions["CO2_emissions"]

with c2col2:
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")
    st.markdown(
        """
            ##### Please note: The y-axis range in the figure gets rescaled as the values are changed.
            """
    )
    plot_elec_price_and_CO2_emissions(date_time, electricity_price_customer, CO2_emissions_specific)

st.markdown("___")

st.markdown("# 3. Further input data settings")
st.markdown(
    """
    Here, the **feed-in tariff** can be set, as well as the **operating strategy**. 
    
    With the button **"Start model calculation!"** the model will be automatically solved. 
    Above all, the model ensures that the **electricity demand is always met**.
    """
)

feed_in_default = 0.08
feed_in_tariff = st.slider("Feed-in tariff [€/kWh]", min_value=0.0, max_value=0.5, value=feed_in_default)


# Initialize session state for own capacity of the battery
if "own_battery_capacity" not in st.session_state:
    st.session_state.own_battery_capacity = None


# Define a callback function to reset the own capacity of the battery
def reset_own_battery_capacity():
    st.session_state.own_battery_capacity = None


radio_battery_capacity = st.radio(
    "Select the capacity of the battery [kWh]:", [3, 6, 9], index=1, on_change=reset_own_battery_capacity
)

own_battery_capacity_value = st.number_input(
    "Define your own battery capacity [kWh]:", value=st.session_state.own_battery_capacity, key="own_battery_capacity"
)

if st.session_state.own_battery_capacity is None:
    storage_capacity = radio_battery_capacity
    str_bat_cap = radio_battery_capacity
else:
    storage_capacity = own_battery_capacity_value
    str_bat_cap = own_battery_capacity_value

# st.write(f"Storage capacity is: {storage_capacity}")


def simulate_and_show_results(feed_in_tariff, electricity_price_customer, CO2_emissions_specific):

    download_placeholder_1 = st.empty()
    download_placeholder_2 = st.empty()

    # get latex tables
    latex_table_reference, latex_table_no_battery = show_latex_table()

    status_placeholder_simulationState = st.empty()
    status_placeholder_error_msg = st.empty()
    status_placeholder_energyBalanceCheck = st.empty()
    status_placeholder_batteryChargeCheck = st.empty()
    status_placeholder_batteryDischargeCheck = st.empty()
    status_placeholder_noArbitrageCheck1 = st.empty()
    status_placeholder_noArbitrageCheck2 = st.empty()
    status_placeholder_energyBalance = st.empty()

    st.header("**Showing results:**")
    st.markdown("___")
    st.markdown("# 5. Outputs")

    # Declaration of required series (for Reference, No battery and Custom)
    P_pv = pv_generation
    P_load = electricity_demand
    P_feed_in = pd.Series(0.0, index=date_time.index, name="P_feed-in")
    P_purchase = pd.Series(0.0, index=date_time.index, name="P_purchase")

    # Header
    if operating_strategy_selected == "Reference":
        st.header("Reference: Paper operating strategy [1]", divider="orange")
        st.caption("Table 4b: Conditions and consequences of the reference operating strategy [1].")
        st.latex(latex_table_reference)

    if operating_strategy_selected == "No battery":
        st.header("No battery storage", divider="orange")
        st.caption("Table 4b: Conditions and consequences of the no-battery operating strategy.")
        st.latex(latex_table_no_battery)

    if operating_strategy_selected == "Custom":
        st.header("Custom operating strategy", divider="orange")

    with st.expander("**Table 2**: Aggregated simulation results and performance indicators"):
        placeholder_outputsTable = st.empty()

    # Perform calculations for the simulation

    # Whitelist allowed words
    whitelist_allowed_words = {
        "P_pv",
        "P_load",
        "P_purchase",
        "P_feed_in",
        "t",
        "SoC",
        "W_batt_max",
        "min",
        "W_batt",
        "max",
        "P_charge",
        "P_discharge",
        "feed_in_tariff",
        "electricity_price_customer",
        "CO2_emissions",
    }

    P_charge = pd.Series(0.0, index=date_time.index, name="P_charge")
    P_discharge = pd.Series(0.0, index=date_time.index, name="P_discharge")
    W_batt = pd.Series(0.0, index=date_time.index, name="W_batt")
    SoC = pd.Series(0.0, index=date_time.index, name="SoC")
    W_batt_max = storage_capacity

    try:
        try:
            # Use StringIO to create a temporary file-like object
            oper_stra = StringIO(st.session_state.text_area_operating_strategy)
            # Load JSON from the StringIO object
            os_from_text_area = json.load(oper_stra)

        except json.JSONDecodeError:
            st.error("The content is not valid JSON. Please correct any formatting errors.")

        # Apply operating strategy to all variables
        for t in range(date_time.size):
            for action in os_from_text_area:
                if safe_execute(
                    action["condition"], allowed_words=whitelist_allowed_words, mode="eval", extra_variables=locals()
                ):
                    safe_execute(
                        action["action"], allowed_words=whitelist_allowed_words, mode="exec", extra_variables=locals()
                    )

            if P_charge[t] > 0 and SoC[t] == 1 and t == 0 or P_charge[t] > 0 and SoC[t - 1] == 1 and t > 0:
                status_placeholder_batteryChargeCheck.error(
                    "batteryChargeCheck Error: Charging of full battery is not possible, results are invalid!"
                )

            if P_discharge[t] > 0 and SoC[t] == 0 and t == 0 or P_discharge[t] > 0 and SoC[t - 1] == 0 and t > 0:
                status_placeholder_batteryDischargeCheck.error(
                    "batteryDischargeCheck Error: Discharging of empty battery is not possible, results are invalid!"
                )

            if P_feed_in[t] > P_pv[t]:
                status_placeholder_noArbitrageCheck1.error(
                    "noArbitrageCheck Error: Discharging the battery to sell to the grid is not allowed."
                )

            if P_charge[t] > P_pv[t]:
                status_placeholder_noArbitrageCheck2.error(
                    "noArbitrageCheck Error: Charging the battery from the grid is not allowed."
                )

            W_batt[t] = min(max((0 if t == 0 else W_batt[t - 1]) + P_charge[t] - P_discharge[t], 0), W_batt_max)
            SoC[t] = W_batt[t] / W_batt_max

        st.session_state.simulation_error = False

    except Exception as e:
        status_placeholder_error_msg.error(
            f"Error in json strategy. Exception (-1) indicates that an [t-1] for t=0 was requested, but this is not defined. Exception: {e}"
        )

    # Use the plot_energy_flow_diagram function from visualisation.py
    fig02 = plot_energy_flow_diagram(
        date_time,
        P_load,
        P_pv,
        P_feed_in,
        P_purchase,
        SoC,
        P_charge,
        P_discharge,
        electricity_price_customer,
        CO2_emissions_specific,
    )
    st.plotly_chart(fig02)

    # Energy balance

    net_energy_balance = P_load - P_pv + P_charge - P_discharge + P_feed_in - P_purchase

    # Use the plot_energy_balance function from visualisation.py
    fig03 = plot_energy_balance(date_time, net_energy_balance)

    # Computation of the costs
    E_purchase, E_feed_in = compute_and_plot_costs(
        P_purchase, P_feed_in, electricity_price_customer, feed_in_tariff, date_time
    )

    # Computation of the emissions
    CO2_generated = compute_and_plot_emissions(CO2_emissions_specific, E_purchase, date_time)

    # Create a dictionary with the output values description
    table_outputs = {
        "Parameter": [
            "C_purchase_total",
            "C_feed_in_total",
            "C_total",
            "CO2_emissions",
            "Self-consumption",
            "Self-sufficiency",
        ],
        "Description": [
            "Total cost of purchased electricity",
            "Total cost of fed-in electricity",
            "Total cost of electricity",
            "Total CO₂ emissions",
            "(PV Energy Used On-Site / Total PV Energy Generated)*100",
            "(PV Energy Used On-Site / Total Energy Consumption)*100",
        ],
        "Value": [
            f"{(E_purchase * electricity_price_customer).sum():.2f}",
            f"{(E_feed_in * electricity_price_customer).sum():.2f}",
            f"{((E_purchase + E_feed_in) * electricity_price_customer).sum():.2f}",
            f"{CO2_generated.sum():.2f}",
            f"{(((P_pv.sum() - P_feed_in.sum())/P_pv.sum())*100):.2f}",
            f"{(((P_pv.sum() - P_feed_in.sum())/P_load.sum())*100):.2f}",
        ],
        "Units": ["€", "€", "€", "gCO₂", "%", "%"],
    }

    df_outputs = pd.DataFrame(table_outputs)
    with placeholder_outputsTable:
        st.table(df_outputs)

    # Concatenate all data for download
    all_result_data = pd.concat(
        [
            date_time,
            electricity_demand,
            pv_generation,
            electricity_price_customer,
            CO2_emissions_specific,
            P_charge,
            P_discharge,
            P_feed_in,
            P_purchase,
            W_batt,
            SoC,
            E_purchase,
            E_feed_in,
            CO2_generated,
        ],
        axis=1,
    )

    new_header_names = [
        "date_time",
        "P_load_kW",
        "P_pv_kW",
        "electricity_price_customer_EUR_kWh",
        "CO2_emissions_g_kWh",
        "P_charge_kW",
        "P_discharge_kW",
        "P_feed_in_kW",
        "P_purchase_kW",
        "W_batt_kWh",
        "SoC_%",
        "E_purchase_kWh",
        "E_feed_in_kWh",
        "CO2_generated_g",
    ]

    all_result_data.columns = new_header_names

    csv_value = all_result_data.to_csv(float_format="%.2f", index=False)
    os_from_text_area_json_dump = json.dumps(os_from_text_area, indent=4)

    if write_results_to_file:
        all_result_data.to_csv(
            f"results/{operating_strategy_selected.strip().replace(' ', '_')}_results.csv",
            float_format="%.2f",
            index=False,
        )

    if st.session_state.simulation_error:
        status_placeholder_simulationState.error("Simulation failed, error message below.")
    else:
        # Use the check_energy_balance function from visualisation.py
        status_type, balance_check = check_energy_balance(net_energy_balance)
        if status_type == "success":
            status_placeholder_energyBalanceCheck.success(balance_check)
        else:
            status_placeholder_energyBalanceCheck.error(balance_check)

        status_placeholder_simulationState.info(
            "Simulation done. Check the Energy Flow Balance (Should be 0 for all t)."
        )

        status_placeholder_energyBalance.plotly_chart(fig03, key="energyBalance_placeholder")
        download_placeholder_1.download_button(
            label="Download the applied operating strategy",
            data=os_from_text_area_json_dump,
            file_name="applied_os.json",
            mime="application/json",
        )
        if use_own_load_profiles_check:
            download_placeholder_2.download_button(
                label="Download result time series",
                data=csv_value,
                file_name=f"{operating_strategy_selected}_results_{str_pv_cap}kW_{str_bat_cap}kWh_{str_profile}_OL_{str_own_load}.csv",
                mime="text/csv",
            )
        else:
            download_placeholder_2.download_button(
                label="Download result time series",
                data=csv_value,
                file_name=f"{operating_strategy_selected}_results_{str_pv_cap}kW_{str_bat_cap}kWh_{str_profile}.csv",
                mime="text/csv",
            )


st.markdown("# 4. Operating strategy")

# Create a dictionary with the data description
table_parameters = {
    "Category": [
        "Photovoltaics",
        "Household",
        "Grid",
        "Grid",
        "Grid",
        "Grid",
        "Grid",
        "Battery",
        "Battery",
        "Battery",
        "Battery",
        "Battery",
    ],
    "Parameter": [
        "P_pv[t]",
        "P_load[t]",
        "P_purchase[t]*",
        "P_feed_in[t]*",
        "feed_in_tariff",
        "electricity_price_customer[t]",
        "CO2_emissions_specific[t]",
        "P_charge[t]*",
        "P_discharge[t]*",
        "W_Batt[t]",
        "W_Batt_max",
        "SoC[t]",
    ],
    "Description": [
        "PV power in t (PV generation)",
        "Power consumption in t (electricity demand)",
        "Power purchase from grid in t",
        "Feed-in power in t",
        "PV feed-in tariff",
        "Electricity price",
        "Specific CO2 emissions",
        "Charging power in t",
        "Discharging power in t",
        "Storage level in t",
        "Usable storage capacity",
        "State of charge",
    ],
    "Units": [
        "kW",  # PV Generation
        "kW",  # Power consumption
        "kW",  # Grid purchase
        "kW",  # Grid feed-in
        "€/kWh",  # Feed-in tariff
        "€/kWh",  # Electricity price
        "g_CO2/kWh",  # specific CO2 emissions
        "kW",  # Battery charging power
        "kW",  # Battery discharging power
        "kWh",  # Storage level
        "kWh",  # Usable storage capacity
        "%",  # State of charge
    ],
}


df = pd.DataFrame(table_parameters)

st.markdown(
    """
### Available Parameter Overview
The table below provides an overview of key parameters in the simulation, 
categorized by different categories such as Photovoltaics, Household, Grid, and Battery.           
"""
)

st.markdown(
    """
### Notes for parameter table
- Parameters with `[t]` are time-dependent parameters
- All parameters can be used in the conditions
- Only Parameters marked with * can be used in the actions and are initialised with value 0 for all `[t]` if not specified otherwise
"""
)

with st.expander("**Table 1**: Parameters table"):
    st.table(df)

st.markdown(
    """
### Notes for operating strategy
- The json syntax needs to be preserved. Use the button below to check if syntax is maintained.
- Updating the battery variables (`SoC[t]` and `W_batt[t]`) happens in the background.
"""
)


# Define a callback function to reset the button state
def reset_clicked_parse_json():
    st.session_state.clicked_parse_json_button = False
    st.session_state.prepared_for_simulation = False


operating_strategy_selected = st.selectbox(
    label="**Select operating strategy:**",
    options=["Reference", "No battery", "Custom"],
    index=0,
    key="operating_strategy_selected",
    on_change=reset_clicked_parse_json,
)

if st.session_state.operating_strategy_selected == "Reference":
    text_os = load_operating_strategy("Reference")
elif st.session_state.operating_strategy_selected == "No battery":
    text_os = load_operating_strategy("No battery")
elif st.session_state.operating_strategy_selected == "Custom":
    text_os = load_operating_strategy("Custom")

st.session_state.text_area_operating_strategy = st.text_area(
    label="Text area for the operation strategy", value=text_os, height=500
)

if "simulation_error" not in st.session_state:
    st.session_state.simulation_error = None

if "clicked_parse_json_button" not in st.session_state:
    st.session_state.clicked_parse_json_button = False

if "prepared_for_simulation" not in st.session_state:
    st.session_state.prepared_for_simulation = False

if st.button("Check JSON"):
    st.session_state.clicked_parse_json_button = True

if st.session_state.clicked_parse_json_button:
    # get manual changes to text_area and apply them to session state

    parsed_strategy, is_valid, error = parse_json_strategy(st.session_state.text_area_operating_strategy)

    if is_valid:
        st.success("The content is valid JSON. Please continue with 'Start model calculation'")
        with st.expander("View the parsed JSON content"):
            st.write("Parsed JSON:", parsed_strategy)

        st.session_state.prepared_for_simulation = True
    else:
        st.session_state.prepared_for_simulation = False
        # Show a basic error message
        st.error("The content is not valid JSON. Please correct any formatting errors.")

        # Expand to view details of the error
        with st.expander("View details of the JSON parsing error"):
            # Show the error message and location
            st.write(f"Error Message: {error.msg}")
            st.write(f"Error at Line {error.lineno}, Column {error.colno}")

            # Display the problematic line with a marker at the error position
            error_line = st.session_state.text_area_operating_strategy.splitlines()[error.lineno - 1]
            st.text_area("Problematic JSON Line", f"{error_line}\n{' ' * (error.colno - 1)}^", height=100)

if st.session_state.prepared_for_simulation:
    if use_own_load_profiles_check and (uploaded_file2 is not None) and (uploaded_demand_selectbox == "Standalone"):
        st.warning(
            "**Warning:** You uploaded a load profile that is currently used without combining it with the selected load profile (it is used as a 'Standalone' profile). Consider combining it with the selected default profile via the dropdown menu in section 1.",
            icon="⚠️",
        )

    if not (apply_additional_costs):
        st.warning(
            "**Warning:** Additional costs for electricity price are not applied. Please select 'Apply additional costs' in section 2.",
            icon="⚠️",
        )

    if st.button("Start model calculation!"):
        # Current Workaround to make variable available:Arguments for simulate_and_show_results are given to make globals available as locals to hand them over as the argument extra_variables for the save eval function
        simulate_and_show_results(feed_in_tariff, electricity_price_customer, CO2_emissions_specific)


st.write("")
st.markdown("___")

with st.expander("Data Sources for Default Data"):
    st.write("[1] [Visit Renewable Ninja](https://www.renewables.ninja/)")
    st.write("[2] [Visit FfE](https://www.ffe.de/)")
    st.write(
        "[3] [Visit Agora Data Tool](https://www.agora-energiewende.org/data-tools/agorameter/chart/today/power_price_emission/01.01.2024/31.12.2024/hourly)"
    )

with st.expander("Show session_state (only for debug)"):
    st.session_state

st.markdown("[Gitlab Repository](https://gitlab.ruhr-uni-bochum.de/ee/NeuesFachlabor)")
with open(".version") as version_file:
    version = version_file.read()
st.write(f"App version: {version}")
st.write(f"Streamlit version: {st.__version__}")
