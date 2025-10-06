import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
from dotenv import load_dotenv
import os
from collections import defaultdict
from utils import transactions

# Load environment variables from .env file
load_dotenv()


def save_keys(secret_id, client_secret):
    """Save API keys to the .env file."""
    with open(".env", "w") as f:
        f.write(f"API_CLIENT_ID={secret_id}\n")
        f.write(f"API_CLIENT_SECRET={client_secret}\n")


# Streamlit container to input and save API keys
with st.container(border=True):
    st.subheader("API keys")
    clientId = st.text_input("Client ID", key="client_id",
                             type="password", value=os.getenv("API_CLIENT_ID"), help="Found in https://skinport.com/account")
    clientSecret = st.text_input(
        "Client Secret", key="client_secret", type="password", value=os.getenv("API_CLIENT_SECRET"), help="Found in https://skinport.com/account")
    if st.button("Save 💾"):
        save_keys(clientId, clientSecret)


@st.cache_resource
def _get_transaction_manager():
    """Initialize and load transaction manager (cached for performance)."""
    man = transactions.TransactionManager(clientId, clientSecret)
    man.load_transactions()
    return man


def get_transaction_manager():
    """Retrieve the transaction manager from session state, initializing if needed."""
    if "transactionManager" not in st.session_state:
        st.session_state.transactionManager = _get_transaction_manager()
    return st.session_state.transactionManager


def transaction_graph_data(start_date_filter, end_date_filter):
    """Process transaction data and return rolling averages for graphing."""
    daily_totals = {}

    averages_dict = {
        'Nothing': 1,
        'Weekly': 7,
        'Monthly': 30
    }

    # Streamlit selectbox for rolling average smoothing
    average_length_key = st.selectbox(
        "Rolling Average Smoothing",
        averages_dict.keys(),  help="Does a rolling average on the graph data, if Nothing is selected the data is not changed"
    )
    average_length = averages_dict[average_length_key]

    with st.spinner("Getting all the transaction data...", show_time=True):
        data = get_transaction_manager().transactions

    # Process transactions within date range
    for item in data:
        updated_at = datetime.strptime(
            item["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        date = updated_at.date()
        if date < start_date_filter or date > end_date_filter:
            continue  # skip outside filter

        type_ = item["type"]

        if date not in daily_totals:
            daily_totals[date] = {"credit": 0, "purchase": 0}

        if type_ == "credit":
            amount = exclude_fees(item.get("amount", 0), item.get(
                "fee"), st.session_state.fees_bool)
            daily_totals[date]["credit"] += amount
        elif type_ == "purchase":
            amount = item.get("amount", 0)
            daily_totals[date]["purchase"] += amount

    # Fill missing dates with zeros
    current_date = start_date_filter
    while current_date <= end_date_filter:
        if current_date not in daily_totals:
            daily_totals[current_date] = {"credit": 0, "purchase": 0}
        current_date += timedelta(days=1)

    # Compute rolling averages
    dates = sorted(daily_totals.keys())[average_length:]
    credit_rolling, purchase_rolling = [], []

    for i in range(len(dates)):
        if i >= average_length - 1:
            credit_avg = sum(daily_totals[dates[j]]["credit"] for j in range(
                i - average_length + 1, i + 1)) / average_length
            purchase_avg = sum(daily_totals[dates[j]]["purchase"] for j in range(
                i - average_length + 1, i + 1)) / average_length
        else:
            credit_avg = None
            purchase_avg = None

        credit_rolling.append(credit_avg)
        purchase_rolling.append(purchase_avg)

    return dates, credit_rolling, purchase_rolling


def exclude_fees(amount, fee, sum_it: bool):
    """Return amount excluding fees if sum_it is True, otherwise return original amount."""
    if sum_it:
        return amount - (fee or 0)
    else:
        return amount


def get_country_distribution(start_date: date, end_date: date):
    """Return total sold amounts per buyer country within the specified date range."""
    data = get_transaction_manager().get_sold()
    buyer_totals = defaultdict(float)

    for entry in data:
        if entry.get("status") != "complete" or "items" not in entry:
            continue

        entry_date_str = entry.get("updated_at")
        if not entry_date_str:
            continue

        # Try parsing with or without milliseconds
        try:
            entry_date = datetime.strptime(
                entry_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        except ValueError:
            try:
                entry_date = datetime.strptime(
                    entry_date_str, "%Y-%m-%dT%H:%M:%SZ").date()
            except ValueError:
                continue  # skip invalid date

        # Skip if outside the date range
        if entry_date < start_date or entry_date > end_date:
            continue

        for item in entry["items"]:
            buyer_country = item.get("buyer_country")
            if buyer_country:
                buyer_totals[buyer_country] += exclude_fees(
                    item.get("amount", 0), item.get("fee"), st.session_state.fees_bool)

    return buyer_totals


def load_date_boxes():
    """Display date input boxes and quick filter buttons in Streamlit."""

    today = datetime.now().date()
    if "start_date" not in st.session_state:
        st.session_state.start_date = today - timedelta(days=365)
    if "end_date" not in st.session_state:
        st.session_state.end_date = today - timedelta(days=1)

    with st.container(border=True):
        column_dates = st.columns(2, gap="Small")

        with column_dates[0]:
            start_date_filter = st.date_input(
                "Start Date", value=st.session_state.start_date, key="start_date_input")
            st.session_state.start_date = start_date_filter

        with column_dates[1]:
            end_date_filter = st.date_input(
                "End Date", value=st.session_state.end_date, key="end_date_input")
            st.session_state.end_date = end_date_filter

        column_days = st.columns(5, gap=None)

        def set_days(value):
            st.session_state.start_date = today - timedelta(days=value)
            st.session_state.end_date = today

        # Checkbox to exclude fees from totals
        with column_days[0]:
            st.session_state.fees_bool = st.checkbox(
                "Exclude fees", help="The amounts shown include Skinport fees. If the checkbox is enabled, you will see only the amount you received.")

        # Quick filters for last 7, 30, or 365 days
        with column_days[len(column_days)-3]:
            st.button("last 7 days", on_click=lambda: set_days(7))
        with column_days[len(column_days)-2]:
            st.button("last 30 days", on_click=lambda: set_days(30))
        with column_days[len(column_days)-1]:
            st.button("last 365 days", on_click=lambda: set_days(365))


def load_transaction_graph():
    """Display line chart of sold vs purchased transactions."""
    dates, credit_rolling, purchase_rolling = transaction_graph_data(
        st.session_state.start_date, st.session_state.end_date)

    df = pd.DataFrame({
        'Sold': credit_rolling,
        'Purchased': purchase_rolling
    }, index=pd.to_datetime(dates))

    st.subheader("Skinport Transactions")
    st.line_chart(df, color=["#B51F1F", "#58B857"])


def load_countryDistribution_graph():
    """Display total sales per buyer country as a dataframe."""
    buyer_totals = get_country_distribution(
        st.session_state.start_date, st.session_state.end_date)
    df = pd.DataFrame({
        "Country": list(buyer_totals.keys()),
        "Total (EUR)": list(buyer_totals.values())
    })

    # Sort by total descending for better visualization
    df = df.sort_values("Total (EUR)", ascending=False)

    st.subheader("Total Sales per Buyer Country")
    st.dataframe(df.reset_index(drop=True))


# Initialize session state
if "transactions_clicked" not in st.session_state:
    st.session_state.transactions_clicked = False

# Button to load transactions and graphs
if st.button(":green[Load all transactions ]📥"):
    st.session_state.transactions_clicked = True

# Display transactions and graphs if clicked
if st.session_state.transactions_clicked:
    if clientId == "" or clientSecret == "":
        st.error("Please insert the API Keys")
    else:
        load_date_boxes()
        load_transaction_graph()
        load_countryDistribution_graph()
