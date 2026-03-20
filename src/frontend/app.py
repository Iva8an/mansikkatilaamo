from http.client import HTTPException
from time import strptime

import streamlit as st
import requests
from datetime import date, datetime
import random
import funktiot as f

if "tila" not in st.session_state:
    st.session_state.tila = "kalenteri"

f.pohjustus()
if st.session_state.tila != "valmis":
    f.tietoja()

if st.session_state.tila=="kalenteri":
    f.kalenteri()

if st.session_state.tila=="varaus":
    f.varaus()

if st.session_state.tila=="valmis":
    f.valmis()

if st.session_state.tila=="virhe":
    st.write("tilauksessa tapahtui virhe yritä uudelleen myöhemmin")




