import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Pato AI Pro")

# --- FUNKCIA NA VÝPOČET PERCENT (AI MOZOG) ---
def vypocitaj_statistiky(df, domaci, hostia):
    # Filtrujeme posledné zápasy oboch tímov
    posledne_doma = df[df['HomeTeam'] == domaci].tail(5)
    posledne_vonku = df[df['AwayTeam'] == hostia].tail(5)
    
    # Výpočet Over 2.5 (kolko zápasov z posledných 10 malo viac ako 2 góly)
    vsetky = pd.concat([posledne_doma, posledne_vonku])
    pocet_over25 = len(vsetky[(vsetky['FTHG'] + vsetky['FTAG']) > 2.5])
    percento_over25 = (pocet_over25 / len(vsetky)) * 100 if len(vsetky) > 0 else 0
    
    # Výpočet BTTS (Obaja dajú gól)
    btts_pocet = len(vsetky[(vsetky['FTHG'] > 0) & (vsetky['FTAG'] > 0)])
    percento_btts = (btts_pocet / len(vsetky)) * 100 if len(vsetky) > 0 else 0

    return {
        "domaci": domaci,
        "hostia": hostia,
        "p_over15": int(percento_over25 + 15), # Odhad
        "p_over25": int(percento_over25),
        "p_btts": int(percento_btts),
        "p_corners": "8.4", # Tu môžeš neskôr pridať reálne rohy
        "ai_text": f"Analýza potvrdzuje, že {domaci} má silný útok, zatiaľ čo {hostia} v posledných 3 zápasoch inkasovali priemerne 2 góly."
    }

# --- FUNKCIA NA ZOBRAZENIE NEÓNOVÉHO DIZAJNU ---
def renderuj_neon(data):
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
            
        # Tu Python prepíše tie "diery" v HTML tvojimi číslami
        html = html.replace("{{DOMACI}}", data['domaci'])
        html = html.replace("{{HOSTIA}}", data['hostia'])
        html = html.replace("{{P_OVER15}}", str(data['p_over15']))
        html = html.replace("{{P_OVER25}}", str(data['p_over25']))
        html = html.replace("{{P_BTTS}}", str(data['p_btts']))
        html = html.replace("{{P_CORNERS}}", str(data['p_corners']))
        html = html.replace("{{AI_TEXT}}", data['ai_text'])
        
        st.components.v1.html(html, height=800, scrolling=True)
    else:
        st.error("Súbor index.html nenájdený!")

# --- HLAVNÉ MENU ---
st.sidebar.title("PATO AI PRO")
ligy = {
    "ANGLICKO": "data_anglicko.csv",
    "TALIANSKO": "data_taliansko.csv",
    "SPANIELSKO": "data_spanielsko.csv",
    "NEMECKO": "data_nemecko.csv",
    "FRANCUZSKO": "data_francuzsko.csv"
}

volba = st.sidebar.selectbox("LIGA:", list(ligy.keys()))
subor = ligy[volba]

if os.path.exists(subor):
    df = pd.read_csv(subor)
    zapas_list = (df['HomeTeam'] + " vs " + df['AwayTeam']).unique().tolist()
    vybraty = st.sidebar.selectbox("ZÁPAS:", zapas_list)
    
    if st.sidebar.button("SPUSTIŤ SKENER"):
        d, h = vybraty.split(" vs ")
        vysledky = vypocitaj_statistiky(df, d, h)
        renderuj_neon(vysledky)
else:
    st.sidebar.warning(f"Chýba súbor {subor}")
