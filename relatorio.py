import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra Pro", layout="wide")

# --- 1. BANCO DE DADOS ---
ARQUIVO_FROTA = 'frota.json'
ARQUIVO_COLAB = 'colaboradores.json'

FROTA_PADRAO = {
    "CARREGADEIRA": ["CSP-078", "CSP-090", "CSP-091", "CSP-093", "CSP-094", "CSP-096", "CSP-097", "CSP-098", "CSP-100", "CSP-104", "CSP-106", "CSP-107"],
    "ESCAVADEIRA": ["ESE-019", "ESE-023", "ESE-031", "ESE-036", "ESE-039", "ESE-047", "ESE-048", "ESE-049", "ESE-050", "ESE-053", "ESE-055", "LOC-3456", "LOC-7726"],
    "CAMINHÃO": ["CAM-185", "CAM-250", "CAM-267", "CAM-279", "CAM-306"],
    "MOTONIVELADORA": ["MON-021", "MON-022"],
    "RETRO ESCAVADEIRA": ["RTE-029", "RTE-030", "RTE-034", "RTE-035"],
    "TRATOR DE ESTEIRA": ["TSE-019", "TSE-036", "TSE-037", "TSE-046", "TSE-052"],
    "MINI CARREGADEIRA / ESCAVADEIRA": ["MCP-007", "MEE-007"],
    "PLANTAS": ["ALV-001", "CMB-002", "CMP-001", "USC-001"]
}

# Lista inicial com os nomes que forneceu (Primeiro e Segundo nome)
COLAB_PADRAO = ["Adilson Santos", "Paulo Ponath", "Filipe Spadetto"]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): return padrao
    with open(