import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra", layout="wide")

# --- 1. BANCO DE DADOS ---
ARQUIVO_DADOS = 'frota.json'

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

def carregar_frota():
    if not os.path.exists(ARQUIVO_DADOS): return FROTA_PADRAO
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f: return json.load(f)

def salvar_frota(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f: json.dump(dados, f, indent=4, ensure_ascii=False)

def formatar_prefixo(nome):
    # Pega apenas o que vem antes do primeiro espaço ou hífen e troca hífen por espaço
    prefixo = nome.split(" ")[0].replace("-", " ")
    return prefixo

frota = carregar_frota()
lista_completa_equip = sorted([item for sublist in frota.values() for item in sublist])

# --- 2. NAVEGAÇÃO LATERAL ---
st.sidebar.title("🏗️ Menu Principal")
aba = st.sidebar.radio("Escolha o Relatório:", ["Disponibilidade", "Equipamentos Utilizados", "Gestão de Frota"])

# --- ABA 1: DISPONIBILIDADE ---
if aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
    relatorio_dict = {}
    
    for categoria, lista in frota.items():
        with st.expander(f"📂 {categoria}", expanded=False):
            itens = []
            for equip in lista:
                nome_limpo = formatar_prefixo(equip)
                if st.checkbox(f"{nome_limpo}", key=f"disp_{equip}"):
                    obs = st.text_input(f"Defeito para {nome_limpo}", key=f"obs_{equip}")
                    itens.append(f"❌ {nome_limpo} - {obs}" if obs else f"✅ {nome_limpo}")
            if itens: relatorio_dict[categoria] = itens

    if st.button("GERAR RELATÓRIO DISPONIBILIDADE"):
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto = f"DISPONIBILIDADE DE EQUIPAMENTOS - {agora}\n\n"
        for cat, linhas in relatorio_dict.items():
            texto += f"{cat}\n" + "\n".join(linhas) + "\n\n"
        st.code(texto, language="text")

# --- ABA 2: UTILIZADOS (MODELO WHATSAPP) ---
elif aba == "Equipamentos Utilizados":
    st.title("📋 Relação de Equipamentos Utilizados")
    
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Cumprimento", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    st.markdown("---")
    
    # Blocos de Seleção
    util_24h = st.multiselect("Selecione Equipamentos (24 horas)", lista_completa_equip)
    util_12h = st.multiselect("Selecione Equipamentos (12 horas)", lista_completa_equip)
    util_adm = st.multiselect("Selecione Equipamentos (ADM)", lista_completa_equip)

    if st.button("GERAR RELAÇÃO DE UTILIZADOS"):
        dia_semana = datetime.now().strftime("%A").capitalize() # Ex: Segunda-feira
        data_extenso = datetime.now().strftime("%d de %B de %Y")
        
        texto_util = f"{saudacao}\nCom segurança.\n\n"
        texto_util += f"Hoje, {data_extenso}\n"
        texto_util += "Segue a relação de equipamentos utilizados:\n\n"
        texto_util += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        if util_24h:
            texto_util += "(24 horas)\n"
            for e in util_24h: texto_util += f"✅ {formatar_prefixo(e)} CASP\n"
            texto_util += "\n"
            
        if util_12h:
            texto_util += "(12 horas)\n"
            for e in util_12h: texto_util += f"✅ {formatar_prefixo(e)} CASP\n"
            texto_util += "\n"

        if util_adm:
            texto_util += "(ADM)\n"
            for e in util_adm: texto_util += f"✅ {formatar_prefixo(e)} CASP\n"
            texto_util += "\n"

        st.code(texto_util, language="text")

# --- ABA 3: GESTÃO ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gestão de Equipamentos")
    
    with st.expander("➕ Adicionar"):
        c_add = st.selectbox("Categoria", list(frota.keys()))
        n_add = st.text_input("Novo Prefixo (Ex: ESE-099)")
        if st.button("Salvar Novo"):
            frota[c_add].append(n_add)
            salvar_frota(frota)
            st.rerun()

    with st.expander("✏️ Editar"):
        c_ed = st.selectbox("Categoria ", list(frota.keys()))
        item_ed = st.selectbox("Selecionar", frota[c_ed])
        n_ed = st.text_input("Corrigir Nome", value=item_ed)
        if st.button("Salvar Edição"):
            idx = frota[c_ed].index(item_ed)
            frota[c_ed][idx] = n_ed
            salvar_frota(frota)
            st.rerun()

    with st.expander("❌ Excluir"):
        c_rm = st.selectbox("Categoria  ", list(frota.keys()))
        item_rm = st.selectbox("Apagar", frota[c_rm])
        if st.button("Confirmar Exclusão"):
            frota[c_rm].remove(item_rm)
            salvar_frota(frota)
            st.rerun()