# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 09:10:49 2025

@author: neto.pedro
"""
#pip install streamlit

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import locale
import glob
import os
import numpy as np
import locale
from datetime import datetime, timedelta


try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Linux e Streamlit Cloud
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')  # Windows
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')  # No Windows pode precisar ser 'Portuguese_Brazil.1252'

dia_hoje = datetime.date.today() - datetime.timedelta(days=10)# Número do mês (com dois dígitos)

mes_numero = dia_hoje.strftime("%m")
mes_nome = dia_hoje.strftime("%B").upper()
ano = dia_hoje.strftime("%Y")

# Caminho da pasta onde estão os arquivos CSV
caminho_pasta = f"https://github.com/Ronches/QuartilHCosta/blob/main/"  # altere para o caminho desejado

# Lista todos os arquivos .csv da pasta
arquivos_csv = glob.glob(os.path.join(caminho_pasta, "*.csv"))

# Lê e empilha todos os arquivos em um único DataFrame
calculadoras = pd.concat([pd.read_csv(arquivo, sep=";", encoding="utf-8") for arquivo in arquivos_csv], ignore_index=True)
calculadoras['DATA'] = pd.to_datetime(calculadoras['MES_REF'], format='%m/%Y')
calculadoras['ano'] = calculadoras['DATA'].dt.year.astype(str)
calculadoras['mes'] = calculadoras['DATA'].dt.strftime('%B').str.upper()
calculadoras['[%] ICM FINAL'] = (
    calculadoras['[%] ICM FINAL']
    .str.replace(',', '.', regex=False)
    .astype(float)
)
st.set_page_config(
    page_title="Quartil Supervisão HCosta",
    page_icon="≫",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Filtro de supervisor
supervisores = calculadoras["SUPERVISOR"].unique()
selecionado = st.multiselect("Selecione o(s) Supervisor(es):", options=supervisores, default=supervisores)
calculadora_filtro = calculadoras[calculadoras["SUPERVISOR"].isin(selecionado)]

# Soma do ICM por quartil
tabela = calculadora_filtro.groupby(["SUPERVISOR", "QUARTIL"]).agg(
    ICM_Somado=("[%] ICM FINAL", "sum")
).reset_index()

total_icm = calculadora_filtro.groupby("SUPERVISOR")["[%] ICM FINAL"].sum().reset_index().rename(columns={"ICM": "ICM_Total"})
tabela = tabela.merge(total_icm, on="SUPERVISOR")
tabela["% Representatividade"] = (tabela["ICM_Somado"] / tabela["[%] ICM FINAL"])

# Pivotando estilo tabela dinâmica
pivot = tabela.pivot(index="QUARTIL", columns="SUPERVISOR", values=["ICM_Somado", "% Representatividade"])

# Exibindo no Streamlit
st.dataframe(pivot.style.format({"% Representatividade": "{:.1f}%", "ICM_Somado": "{:.0f}"}))