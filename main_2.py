import streamlit as st
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import requests
import json
import os

header = st.container()
description = st.container()

with header:
    st.title('Pointer - Precificador Inteligente')


@st.cache(allow_output_mutation=True)

@st.experimental_singleton
def charge_model_H():
    # Load large model
    model = CatBoostRegressor()
    return model

catboost_model_H = charge_model_H()
#catboost_model_H = catboost_model_H.load_model('catboost_model_H.pkl')


@st.experimental_singleton
def charge_model_M():
    # Load large model
    model = CatBoostRegressor()
    return model

catboost_model_M = charge_model_M()
#catboost_model_M = catboost_model_M.load_model('catboost_model_M.pkl')


@st.experimental_singleton
def charge_model_L():
    # Load large model
    model = CatBoostRegressor()
    return model

catboost_model_L = charge_model_L()
#catboost_model_L = catboost_model_L.load_model('catboost_model_L.pkl')

#Loading database

def get_data():
    path = r'base_consulta_api.csv'
    return pd.read_csv(path, index_col=[0])


df = get_data()

Marca = df['marca'].drop_duplicates().sort_values()
marca_selecionada = st.selectbox('Selecione a marca desejada:', Marca)


Modelo = df[df['marca'] ==
            marca_selecionada]['modelo'].drop_duplicates().sort_values()
modelo_selecionado = st.selectbox('Selecione o modelo desejado:', Modelo)

Ano_do_Modelo = df[df['modelo'] ==
            modelo_selecionado]['ano_modelo'].sort_values().unique()
ano_modelo_selecionado = st.selectbox('Selecione o ano do modelo:', Ano_do_Modelo.astype(int))



#Chamando na API


token = st.secrets["token"]
model_hash = st.secrets["model_hash"]

url = "https://neomaril.datarisk.net/api/model/sync/run/comven/" + model_hash
headers = {"Authorization": "Bearer " + token}
payload = {
    "Input": {"marca" : marca_selecionada,
    "ano_modelo" : ano_modelo_selecionado.astype(float),
    "modelo" : modelo_selecionado}
}

response = requests.request("POST", url, json=payload, headers=headers)

#Formando predicoes do modelo para interface

predictions = response.json()

try:
    y_pred_H = predictions['percentil_90']
    y_pred_M = predictions['mediana']
    y_pred_L = predictions['percentil_10']

    st.markdown("<h1 style='text-align: center; color: red;'>Preços estimados</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Inferior")
        st.subheader(f'R$ {"{:,.0f}".format(y_pred_L).replace(",",".")}')

    with col2:
        st.header("Média")
        st.subheader(f'R$ {"{:,.0f}".format(y_pred_M).replace(",",".")}')

    with col3:
        st.header("Superior")
        st.subheader(f'R$ {"{:,.0f}".format(y_pred_H).replace(",",".")}')
except KeyError:
    st.markdown("<h1 style='text-align: center; color: red;'>Veículo não encontrado</h1>", unsafe_allow_html=True)



