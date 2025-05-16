import streamlit as st
import pandas as pd
import geopandas as gpd
from PIL import Image
import numpy as np

inicial = st.Page("inicial.py", title="Página Inicial", icon=":material/add_circle:")
mapa = st.Page("mapa.py", title="Gerador de Mapas", icon=":material/add_circle:")
gerador = st.Page("gerador.py", title="Gerador de Mapas", icon=":material/add_circle:")
visualizador = st.Page("visualizador.py", title="Visualizador", icon=":material/add_circle:")
sobre = st.Page("sobre.py", title="Sobre", icon=":material/add_circle:")


pg = st.navigation([inicial, mapa, visualizador, sobre])

st.set_page_config(page_title="Mapas de Fluxo", layout="centered", page_icon=":material/edit:")

if "escuro" not in st.session_state:
    st.session_state["escuro"] = True

if "gdf" not in st.session_state:
    st.session_state['gdf'] = (gpd.read_file('arquivos/BR_UF_2023.shp').loc[:,["SIGLA_UF", "geometry"]].copy()
                               .set_index('SIGLA_UF'))

if "cores" not in st.session_state:
    st.session_state["cores"] = {"pbg": {True: "#1a120d", False: "#ffede6"},
                                 "sbg": {True: "#33231a", False: "#ffcda5"},
                                 "tex": {True: "#ffede6", False: "#1a0a00"},
                                 "lat": {True: "#ff9640", False: "#804e26"}}

if "centroide" not in st.session_state:
    st.session_state['centroide'] = st.session_state['gdf'].copy().to_crs(epsg=5880).centroid.to_crs(epsg=4674)

if "df_1":
    np.random.seed(123)
    matriz = np.random.randint(0, 101, size=(27, 27))
    st.session_state["df_1"] = pd.DataFrame(matriz, columns=sorted(st.session_state['gdf'].index.values),
                                            index=sorted(st.session_state['gdf'].index.values))

st.logo(Image.open("imagens/icone.png"))

modo_escuro = st.toggle(":orange-badge[🌙 Modo Escuro]", st.session_state["escuro"])

st.session_state["escuro"] = modo_escuro

custom_css = f"""
    <style>
        .stApp {{
            background-color: {st.session_state["cores"]["pbg"][modo_escuro]};
            color: {st.session_state["cores"]["tex"][modo_escuro]};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {st.session_state["cores"]["sbg"][modo_escuro]};
        }}

        section[data-testid="stSidebar"] * {{
            color: {st.session_state["cores"]["lat"][modo_escuro]} !important;
        }}
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

pg.run()