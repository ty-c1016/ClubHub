import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks
from datetime import datetime, timedelta
import pandas as pd

SideBarLinks()

st.set_page_config(
    page_title="Search Insights",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Search Insights Dashboard")
st.markdown("Analyze user search behavior and popular keywords")

st.divider()

#API endpoint
API_URL = "http://web-api:4000/analytics/analytics/search"

try:
    response = requests.get(f"{API_URL}/summary")
    if response.status_code == 200:
        search_summary = response.json()
    else:
        st.error(f"Failed to fetch summary data. Status: {response.status_code}")
        search_summary = {}
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching summary data: {e}")
    search_summary = {}