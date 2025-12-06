import json
import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("## API Test: Analytics Engagement Data")
response = requests.get("http://web-api:4000/analytics/analytics/engagement").json()
try:
    st.dataframe(response)
except Exception as e:
    st.error(f"Could not load data from API: {e}")



