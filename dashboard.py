import streamlit as st

main = st.Page("pages/homepage.py", title="Home",
               icon=":material/dashboard:")

search_transactions = st.Page("pages/search_transactions.py", title="Search Transactions",
                              icon=":material/search:")

page = st.navigation(
    {
        "Dashboard": [main]
    }
)
st.set_page_config(page_title="Skinport Dashboard",
                   page_icon=":material/account_balance:")
page.run()
