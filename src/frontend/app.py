from http.client import HTTPException
from time import strptime

import streamlit as st
import requests
from datetime import date, datetime
import random
if "tila" not in st.session_state:
    st.session_state.tila = "kalenteri"
if "paiva" not in st.session_state:
    st.session_state.paiva = date.today()
if "max" not in st.session_state:
    st.session_state.max = 10
if "mansikkahinta" not in st.session_state:
    st.session_state.mansikkahinta = 50
if st.session_state.tila != "valmis":
    st.title("Mansikka tilaus")
    st.write("Maksimissaan 10 laatikkoa per varaus saatavuus saattaa vaihdella päivittäin")
    st.header("Hinnasto:")
    st.write("Mansikat 5kg ~10 ltr laatikko = 50 €")
if st.session_state.tila != "kalenteri":
    if st.button("Palaa päivämäärän valintaan"):
        st.session_state.tila = "kalenteri"
        st.rerun()

if st.session_state.tila=="kalenteri":
    st.session_state.paiva = st.date_input("Päivän valinta")
    if date.today() >= st.session_state.paiva:
        st.write("Varauksia ei vapaana tälle päivälle. Valitse toinen päivä")
    else:
        st.write("mansikoita varattavissa.", st.session_state.max, "laatikkoa varattavissa")
        if st.button("Siirry varaamaan"):
            st.session_state.tila = "varaus"
            st.rerun()

if st.session_state.tila=="varaus":
    st.write("Valittu päivämäärä: ", st.session_state.paiva)
    st.session_state.mansikoita =st.number_input("Mansikka laatikoita. 1 laatikko= 5kg ~10 ltr",0,st.session_state.max,1)
    st.write("hinta yhteensä", st.session_state.mansikoita * st.session_state.mansikkahinta, "€")
    st.session_state.nimi = st.text_input("Nimi")
    st.session_state.email = st.text_input("Email")
    st.session_state.puhelinnumero = st.text_input("Puhelinnumero")
    st.session_state.muu =st.text_area("Muuta infoa")
    st.session_state.varaustunnus = int(datetime.today().timestamp() * 100000) - 177250000000000
    if st.button("VARAA MANSIKAT!!"):
        tiedot = {
            "id": st.session_state.varaustunnus,
            "email": st.session_state.email,
            "maara": st.session_state.mansikoita,
            "puh": st.session_state.puhelinnumero,
            "muuta": st.session_state.muu,
            "pvm": datetime.strftime(st.session_state.paiva, "%Y-%m-%d")
        }
        testi = {
            "name": "st.session_state.puhelinnumero",
            "description": "st.session_state.muu",
        }
        #vastaus = requests.post("http://localhost:8000/tilaus", json=testi)"""
        onnistuu_laatikoiden_maara = requests.get(f"http://localhost:8000/saatavuus/{tiedot["pvm"]}")
        if onnistuu_laatikoiden_maara:
            requests.post(f"http://localhost:8000/tilaus/", json=tiedot)
            st.session_state.tila = "valmis"
            st.rerun()
        else:
            st.write(f"Ei onnistu varaamaan {tiedot["maara"]} laatikkoa päivälle {tiedot["pvm"]}, {onnistuu_laatikoiden_maara.status_code} ")

       # if vastaus.status_code == 200:
        #    st.session_state.tila = "valmis"
        #    st.rerun()
       # else:
        #    st.session_state.tila = "virhe"
         #   st.rerun()

if st.session_state.tila=="valmis":
    st.write("Mansikat varattu. Varaus tunnus:", st.session_state.varaustunnus)
    st.write("Nimi: ", st.session_state.nimi)
    st.write("Puhelinnumero: ", st.session_state.puhelinnumero)
    st.write("Muuta infoa: ", st.session_state.muu)
    st.write("varattu määrä: ", st.session_state.mansikoita)
    st.write("hinta yhteensä: ", st.session_state.mansikoita * st.session_state.mansikkahinta, "€")
    st.write("Tarkista vielä tiedot ja ole hyvä ja ole yhteydessä jos on muutettavaa! :)")

if st.session_state.tila=="virhe":
    st.write("tilauksessa tapahtui virhe yritä uudelleen myöhemmin")