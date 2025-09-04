import streamlit as st
import plotly.graph_objs as go


def plot_demand_and_pv_generation(time_series, demand, pv_generation):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_series,
            y=demand,
            mode="lines",
            name="Demand",
            hovertemplate="%{y:.2g}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=time_series,
            y=pv_generation,
            mode="lines",
            name="PV Generation",
            hovertemplate="%{y:.2g}",
        )
    )
    fig.update_layout(
        title="Figure 1: Electricity Demand and PV Generation",
        xaxis_title="Time",
        yaxis_title="Electric Power [kW]",
        yaxis=dict(tickformat=".1f"),  # Show numbers with one decimal place
        hovermode="x",
    )
    st.plotly_chart(fig)


def plot_elec_price_and_CO2_emissions(time_series, electricity_price, CO2_emissions):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_series,
            y=electricity_price,
            mode="lines",
            name="Electricity price",
            hovertemplate="%{y:.2f}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=time_series,
            y=CO2_emissions,
            mode="lines",
            name="CO₂ Emissions",
            yaxis="y2",
            hovertemplate="%{y:.2f}",
        )
    )
    fig.update_layout(
        title="Figure 2: Electricity Price and CO₂ Emissions",
        xaxis_title="Time",
        yaxis=dict(
            title="Electricity Price [€/kWh]",
            side="left",
        ),
        yaxis2=dict(
            title="CO₂ Emissions [gCO₂/kWh]",
            side="right",
            overlaying="y",
            anchor="x",
            showgrid=False,
        ),
        legend=dict(orientation="h", x=0.0, y=-0.3),
        hovermode="x",
    )
    st.plotly_chart(fig)


def plot_energy_flow_diagram(
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
):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_time, y=(-1) * P_load, mode="lines", name="Demand"))
    fig.add_trace(go.Scatter(x=date_time, y=P_pv, mode="lines", name="PV Generation"))
    fig.add_trace(go.Scatter(x=date_time, y=P_load - P_pv, mode="lines", name="Residual load", visible="legendonly"))
    fig.add_trace(go.Scatter(x=date_time, y=(-1) * P_feed_in, mode="lines", name="Feed-in", visible="legendonly"))
    fig.add_trace(go.Scatter(x=date_time, y=P_purchase, mode="lines", name="Purchase", visible="legendonly"))

    fig.add_trace(go.Scatter(x=date_time, y=SoC, mode="lines", name="SoC", yaxis="y2"))
    fig.add_trace(go.Scatter(x=date_time, y=(-1) * P_charge, mode="lines", name="Charge", visible="legendonly"))
    fig.add_trace(go.Scatter(x=date_time, y=P_discharge, mode="lines", name="Discharge", visible="legendonly"))
    fig.add_trace(
        go.Scatter(
            x=date_time,
            y=electricity_price_customer,
            mode="lines",
            name="Electricity price",
            yaxis="y3",
            visible="legendonly",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=date_time, y=CO2_emissions_specific, mode="lines", name="CO₂ Emissions", yaxis="y4", visible="legendonly"
        )
    )

    fig.update_layout(
        title="Figure 4c: Energy Flow Diagram",
        xaxis_title="Time",
        yaxis_title="Power [kW]",
        legend=dict(orientation="h", x=0.0, y=-0.3),
        hovermode="x",
    )

    fig.update_layout(
        xaxis=dict(domain=[0.0, 0.8]),  # set the horizontal relative width of the x axis
        yaxis2=dict(
            title="State of Charge (SoC)",
            overlaying="y",
            side="right",
            anchor="free",
            position=0.8,
            range=[-1.0, 1.0],
        ),
        yaxis3=dict(
            title="Electricity price [€/kWh]",
            overlaying="y",
            side="right",
            anchor="free",
            position=0.9,
        ),
        yaxis4=dict(
            title="CO₂ Emissions [gCO₂/kWh]",
            overlaying="y",
            side="right",
            anchor="free",
            position=1.0,
        ),
    )

    return fig


def plot_energy_balance(date_time, net_energy_balance):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_time, y=net_energy_balance, mode="lines", name="Energy Balance"))
    fig.update_layout(title="Figure 4a: Energy Flow Balance", xaxis_title="Date", yaxis_title="Balance [kW]")
    return fig


def compute_and_plot_costs(P_purchase, P_feed_in, electricity_price, feed_in_tariff, time_series):
    time_step = 1  # [h]
    E_purchase = P_purchase * time_step  # [kWh]
    C_purchase = E_purchase * electricity_price  # [€]
    C_purchase_total = C_purchase.sum()
    E_feed_in = P_feed_in * time_step  # [kWh]
    C_feed_in = -E_feed_in * feed_in_tariff  # [€]
    C_feed_in_total = C_feed_in.sum()
    C_balance = C_purchase + C_feed_in
    C_total = C_balance.sum()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_series, y=C_purchase, mode="lines", name="Purchase costs"))
    fig.add_trace(go.Scatter(x=time_series, y=C_feed_in, mode="lines", name="Feed-in compensation"))
    fig.update_layout(
        title="Figure 4d: Electricity costs and feed-in compensation",
        xaxis_title="Date",
        yaxis_title="Cost [€]",
        hovermode="x",
    )
    st.plotly_chart(fig)
    st.subheader(f"The cost for purchased electricity is {C_purchase_total:.2f} €")
    st.subheader(f"The cost for fed-in electricity is {C_feed_in_total:.2f} €")
    st.markdown(f"### The total cost is {C_total:.2f} €")
    E_purchase.name = "E_purchase"
    E_feed_in.name = "E_feed_in"
    return E_purchase, E_feed_in


def compute_and_plot_emissions(CO2_emissions, E_purchase, time_series):
    CO2_generated = CO2_emissions * E_purchase  # [gCO2]
    CO2_generated.name = "CO2_generated"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_series, y=CO2_generated, mode="lines", name="CO2 emissions"))
    fig.update_layout(
        title="Figure 4e: CO₂ emissions due to purchased electricity",
        xaxis_title="Date",
        yaxis_title="CO₂ emissions [gCO₂]",
        hovermode="x",
    )
    st.plotly_chart(fig)
    CO2_total = round(CO2_generated.sum(), 2)
    st.markdown(
        f"### The weekly CO₂ emissions due to purchased electricity using this operating strategy corresponds to {CO2_total:.2f} gCO₂"
    )
    return CO2_generated


def show_latex_table():

    latex_table_reference = r"""

    \begin{array}{c c c c l c l}

    \hline
    \text{Conditions} & \text{} & \text{} & \text{} & \text{Consequence} & \text{} & \text{} \\

    \hline

    P_{\text{PV},t} > P_{\text{Load},t} & \text{} & \text{SoC}_t < 1 & \text{} & P_{\text{Charge},t} = P_{\text{PV},t} - P_{\text{Load},t} & \text{} & P_{\text{Feed-in},t} = 0 \\
    \text{} & \text{} & \text{} & \text{} & P_{\text{Discharge},t} = 0 & \text{} & P_{\text{Purchase},t} = 0\\

    \text{} & \text{} & \text{SoC}_t = 1 &  \text{} & P_{\text{Charge},t} = 0 & \text{} & P_{\text{Feed-in},t} = P_{\text{PV},t} - P_{\text{Load},t} \\
    \text{} & \text{} & \text{} & \text{} & P_{\text{Discharge},t} = 0 & \text{} & P_{\text{Purchase},t} = 0 \\

    \text{} & \text{and} & \text{} & \text{then} & \text{} & \text{and} & \text{} \\

    P_{\text{PV},t} \le P_{\text{Load},t} & \text{} & \text{SoC}_t > 0 &  \text{} & P_{\text{Charge},t} = 0 & \text{} & P_{\text{Feed-in},t} = 0 \\
    \text{} & \text{} & \text{} & \text{} & P_{\text{Discharge},t} = P_{\text{PV},t} - P_{\text{Load},t} & \text{} & P_{\text{Purchase},t} = 0 \\

    \text{} & \text{} & \text{SoC}_t = 0 &  \text{} & P_{\text{Charge},t} = 0 & \text{} & P_{\text{Feed-in},t} = 0  \\
    \text{} & \text{} & \text{} & \text{} & P_{\text{Discharge},t} = 0 & \text{} & P_{\text{Purchase},t} = P_{\text{PV},t} - P_{\text{Load},t}\\

    \hline

    \end{array}

    """

    latex_table_no_battery = r"""

    \begin{array}{c c c}

    \hline
    \text{Conditions} & & \text{Consequence} \\

    \hline

    P_{\text{PV}} > P_{\text{Load}} & & P_{\text{Feed-in},t} = P_{\text{PV},t} - P_{\text{Load},t} \\

    \hline

    P_{\text{PV}} \le P_{\text{Load}} & & P_{\text{Purchase},t} = P_{\text{PV},t} - P_{\text{Load},t} \\

    \hline

    \end{array}

    """

    return latex_table_reference, latex_table_no_battery
