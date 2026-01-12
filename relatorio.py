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

COLAB_PADRAO = ["Adilson Santos", "Paulo Ponath", "Filipe Spadetto"]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): 
        return padrao
    try:
        with open(arquivo, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except:
        return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f: 
        json.dump(dados, f, indent=4, ensure_ascii=False)

def formatar_prefixo(nome):
    return nome.split(" ")[0].replace("-", " ")

def limpar_nome_colab(nome_completo):
    partes = nome_completo.split()
    return " ".join(partes[:2]) if len(partes) >= 2 else nome_completo

# Carregar dados
frota = carregar_dados(ARQUIVO_FROTA, FROTA_PADRAO)
colaboradores = sorted(carregar_dados(ARQUIVO_COLAB, COLAB_PADRAO))
lista_completa_equip = sorted([item for sublist in frota.values() for item in sublist])

# --- 2. NAVEGAÇÃO LATERAL ---
st.sidebar.title("🏗️ Menu Principal")
aba = st.sidebar.radio("Escolha o Relatório:", ["Disponibilidade", "Equipamentos Utilizados", "Gestão de Frota", "Gestão de Pessoal"])

# --- ABA: DISPONIBILIDADE ---
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

# --- ABA: UTILIZADOS ---
elif aba == "Equipamentos Utilizados":
    st.title("📋 Relação de Equipamentos Utilizados")
    
    col1, col2, col3 = st.columns(3)
    with col1: 
        saudacao = st.selectbox("Cumprimento", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: 
        letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: 
        turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    col_p1, col_p2 = st.columns(2)
    with col_p1: 
        supervisor = st.selectbox("Supervisor", colaboradores)
    with col_p2: 
        encarregado = st.selectbox("Encarregado", colaboradores)

    st.markdown("---")
    
    disponiveis = lista_completa_equip.copy()
    u24 = st.multiselect("24 horas", disponiveis)
    disponiveis = [e for e in disponiveis if e not in u24]
    
    u12 = st.multiselect("12 horas", disponiveis)
    disponiveis = [e for e in disponiveis if e not in u12]
    
    u_adm = st.multiselect("ADM", disponiveis)
    disponiveis = [e for e in disponiveis if e not in u_adm]
    
    u_ev = st.multiselect("EVENTUAL", disponiveis)

    if st.button("GERAR RELAÇÃO DE UTILIZADOS"):
        data_extenso = datetime.now().strftime("%d de %B de %Y")
        s_nome = limpar_nome_colab(supervisor)
        e_nome = limpar_nome_colab(encarregado)
        
        texto_util = f"{saudacao}\nCom segurança.\n\nHoje, {data_extenso}\nSegue a relação de equipamentos utilizados:\n\n"
        texto_util += f"Supervisor: {s_nome}\nEncarregado: {e_nome}\nLetra: {letra}\nTurno: {turno}\n\n"
        
        secoes = [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", u_adm), ("(EVENTUAL)", u_ev)]
        for titulo, lista in secoes:
            if lista:
                texto_util += f"{titulo}\n"
                for e in lista: 
                    texto_util += f"✅ {formatar_prefixo(e)} CASP\n"
                texto_util += "\n"
        st.code(texto_util, language="text")

# --- GESTÃO FROTA ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gestão de Equipamentos")
    with st.expander("➕ Adicionar"):
        c_add = st.selectbox("Categoria", list(frota.keys()))
        n_add = st.text_input("Novo Prefixo")
        if st.button("Salvar Novo"):
            frota[c_add].append(n_add)
            salvar_dados(ARQUIVO_FROTA, frota)
            st.rerun()
    with st.expander("✏️ Editar"):
        c_ed = st.selectbox("Categoria ", list(frota.keys()))
        item_ed = st.selectbox("Selecionar", frota[c_ed])
        n_ed = st.text_input("Corrigir", value=item_ed)
        if st.button("Salvar Edição"):
            idx = frota[c_ed].index(item_ed)
            frota[c_ed][idx] = n_ed
            salvar_dados(ARQUIVO_FROTA, frota)
            st.rerun()
    with st.expander("❌ Excluir"):
        c_rm = st.selectbox("Categoria  ", list(frota.keys()))
        item_rm = st.selectbox("Apagar", frota[c_rm])
        if st.button("Confirmar Exclusão"):
            frota[c_rm].remove(item_rm)
            salvar_dados(ARQUIVO_FROTA, frota)
            st.rerun()

# --- GESTÃO PESSOAL ---
elif aba == "Gestão de Pessoal":
    st.title("👤 Gestão de Colaboradores")
    novo_colab = st.text_input("Nome do Colaborador")
    if st.button("Adicionar Colaborador"):
        if novo_colab:
            colaboradores.append(novo_colab)
            salvar_dados(ARQUIVO_COLAB, colaboradores)
            st.rerun()
    st.markdown("---")
    colab_remover = st.selectbox("Remover Colaborador", colaboradores)
    if st.button("Remover"):
        colaboradores.remove(colab_remover)
        salvar_dados(ARQUIVO_COLAB, colaboradores)
        st.rerun()