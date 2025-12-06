import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

#st.write("# Accessing a REST API from Within Streamlit")
#"""
#Simply retrieving data from a REST api running in a separate Docker Container.

##If the container isn't running, this will be very unhappy.  But the Streamlit app 
#should not totally die. 
#"""

st.write("accessing a REST API from within streamlit")


response = requests.get("http://web-api:4000/analytics/analytics/engagement").json()
try:
    st.dataframe(response)
except Exception as e:
    st.error(f"Could not load data from API: {e}")

