import streamlit as st
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Turno", layout="wide")

# --- 1. SISTEMA DE BANCO DE DADOS ---
ARQUIVO_DADOS = 'frota.json'

FROTA_PADRAO = {
    "CARREGADEIRA": [
        "CSP-078 - CAT 938G II", "CSP-090 - CAT 938K", "CSP-091 - CAT 938K",
        "CSP-093 - CAT 924K", "CSP-094 - CAT 938K", "CSP-096 - CAT 938K",
        "CSP-097 - CAT 938K", "CSP-098 - CAT 924K", "CSP-100 - CAT 950L",
        "CSP-104 - CAT 938K", "CSP-106 - CAT 924K", "CSP-107 - CAT 924K"
    ],
    "ESCAVADEIRA": [
        "ESE-019 - CAT 320 C", "ESE-023 - CAT 320 C", "ESE-031 - CAT 312 C",
        "ESE-036 - HYUNDAI R260LC", "ESE-039 - HYUNDAI R220LC-9S", "ESE-047 - CAT 320LBR",
        "ESE-048 - CAT 320GX", "ESE-049 - CAT 320LBR", "ESE-050 - CAT 320LBR",
        "ESE-053 - CAT 320GC", "ESE-055 - CAT 320GC", "LOC-3456 - HYUNDAI R220LC-9S",
        "LOC-7726 - HYUNDAI R220LC-9S"
    ],
    "CAMINHÃO": [
        "CAM-185 - FORD 2626", "CAM-250 - MB L-1620/51", "CAM-267 - MB 1718/48",
        "CAM-279 - VW 24.260", "CAM-306 - VW 26.260"
    ],
    "MOTONIVELADORA": ["MON-021 - CAT 12H II", "MON-022 - CAT 12H II"],
    "RETRO ESCAVADEIRA": [
        "RTE-029 - CAT 416E", "RTE-030 - CAT 416E", "RTE-034 - CAT 416F", "RTE-035 - CAT 416F"
    ],
    "TRATOR DE ESTEIRA": [
        "TSE-