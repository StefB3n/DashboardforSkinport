import streamlit as st
from datetime import datetime, timedelta, date
from utils import transactions
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import base64
import requests
from dotenv import load_dotenv
import os
from collections import defaultdict


def get_transaction_manager():
    """Retrieve the transaction manager from Streamlit session state."""
    if "transactionManager" not in st.session_state:
        st.error("you must load the data on the dashboard, before using this page")
    return st.session_state.transactionManager


def load_transactions_by_item_name(item_name: str, type_filter):
    """Load and display transactions containing a specific item name and type."""
    data = get_transaction_manager().transactions
    if not data:
        st.error("No transaction data returned from API.")
        return pd.DataFrame()

    matches = []

    for entry in data:
        # Ensure items is a list
        items = entry.get("items")
        if entry.get("status") != "complete":
            continue

        if entry["type"] == type_filter and entry["type"] == "withdraw":
            # Parse date for withdrawal entries
            updated_at = entry.get("updated_at")
            date = None
            if updated_at:
                try:
                    date = datetime.strptime(
                        updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        date = datetime.strptime(
                            updated_at, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        pass
            matches.append({
                "Date": date,
                "Amount (EUR)": entry.get("amount", 0.0),
                "Type": entry.get('type', "Unknown")
            })

        elif entry["type"] == type_filter or type_filter is None:
            if not isinstance(items, list):
                continue

            for item in items:
                name = item.get("market_hash_name") or item.get("name", "")
                if not name:
                    continue

                if item_name.lower() in name.lower():
                    # Parse date for item entries
                    updated_at = entry.get("updated_at")
                    date = None
                    if updated_at:
                        try:
                            date = datetime.strptime(
                                updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            try:
                                date = datetime.strptime(
                                    updated_at, "%Y-%m-%dT%H:%M:%SZ")
                            except ValueError:
                                pass

                    matches.append({
                        "Date": date,
                        "Item": name,
                        "Amount (EUR)": item.get("amount", 0.0),
                        "Type": entry.get('type', "Unknown"),
                        "Sale ID": item.get("sale_id", "N/A")
                    })

    if not matches:
        st.warning(f"No transactions found containing '{item_name}'.")
        return pd.DataFrame()

    df = pd.DataFrame(matches)
    df = df.sort_values("Date", ascending=False)
    st.dataframe(df.reset_index(drop=True), height=600)
    return df


st.subheader("Search through the transaction history")

# Mapping for transaction type selection
selection_dict = {
    'All': None,
    'Purchase': "purchase",
    'Sold': "credit",
    'Payouts': "withdraw"
}

# Streamlit selectbox for transaction type
selection_key = st.selectbox(
    "Transaction Type",
    selection_dict.keys()
)
type_filter = selection_dict[selection_key]

# Initialize search click state if not present
if "transactionManager" not in st.session_state:
    st.session_state.search_clicked = False

# Layout for search input and button
search_area = st.columns((4, 1), vertical_alignment="bottom")
with search_area[0]:
    market_hash_name = st.text_input(
        "Items Name (MarketHashName)", placeholder="Skins name or markethashname")
with search_area[1]:
    if st.button("Search 🔎"):
        st.session_state.search_clicked = True

# Execute search if button was clicked
if st.session_state.search_clicked:
    load_transactions_by_item_name(market_hash_name, type_filter)
    st.session_state.search_clicked = False
