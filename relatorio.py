import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Turno", layout="wide")

# --- 1. BANCO DE DADOS ---
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
        "TSE-019 - CAT D6D", "TSE-036 - CAT D6M", "TSE-037 - CAT D6M",
        "TSE-046 - CAT D5", "TSE-052 - CAT D4"
    ],
    "MINI CARREGADEIRA / ESCAVADEIRA": ["MCP-007 - CAT 226B3", "MEE-007 - CAT 305.5"],
    "PLANTAS": [
        "ALV-001 - BRITADOR SXBM 6240", "CMB-002 - BRITADOR CÔNICO SYMONS",
        "CMP-001 - PENEIRA AZUL", "USC-001 - USINA DE REVSOL CINZA"
    ]
}

def carregar_frota():
    if not os.path.exists(ARQUIVO_DADOS):
        return FROTA_PADRAO
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_frota(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

frota = carregar_frota()

# --- 2. GESTÃO NA BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações")
with st.sidebar.expander("➕ Adicionar Máquina"):
    cat_add = st.selectbox("Categoria", list(frota.keys()))
    novo_nome = st.text_input("Nome/Tag")
    if st.button("Salvar"):
        if novo_nome:
            frota[cat_add].append(novo_nome)
            salvar_frota(frota)
            st.rerun()

# --- 3. INTERFACE PRINCIPAL ---
st.title("🚜 Controle de Disponibilidade")

relatorio_final_dict = {}

for categoria, lista in frota.items():
    with st.expander(f"📂 {categoria}", expanded=True):
        itens_selecionados = []
        for equip in lista:
            # Mostra no site com espaço em vez de hífen (ex: ESE 019)
            exibicao_site = equip.replace("-", " ", 1)
            check = st.checkbox(f"{exibicao_site}", key=equip)
            
            if check:
                obs = st.text_input(f"Defeito para {exibicao_site}", key=f"obs_{equip}")
                # Formata o nome para o relatório (ex: ESE 019)
                equip_formatado = equip.replace("-", " ", 1)
                
                if obs:
                    itens_selecionados.append(f"❌ {equip_formatado} - {obs}")
                else:
                    itens_selecionados.append(f"✅ {equip_formatado}")
        
        if itens_selecionados:
            relatorio_final_dict[categoria] = itens_selecionados

# --- 4. GERADOR DE RELATÓRIO ---
if st.button("GERAR RELATÓRIO FINAL"):
    if not relatorio_final_dict:
        st.error("Selecione pelo menos um equipamento!")
    else:
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        # Cabeçalho limpo: apenas o título e a data
        texto = f"DISPONIBILIDADE DE EQUIPAMENTOS - {agora}\n\n"
        
        for cat, linhas in relatorio_final_dict.items():
            texto += f"{cat}\n"  # Categoria sem emoji
            texto += "\n".join(linhas) + "\n\n"
        
        st.success("Relatório pronto! Clique em 'Copy' no canto da caixa abaixo.")
        st.code(texto, language="text")