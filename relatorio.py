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

# Lista com todos os colaboradores das fotos enviadas
COLAB_PADRAO = [
    "", "ADILSON DE JESUS SANTOS", "HANDREY FRITZ SERAFIM", "JONATAS FAGUNDES DA COSTA", 
    "PAULO SILAS PONATH", "JOAO VICTOR OLIVEIRA CORATO GABRIEL", "JAMES RIBEIRO CARNEIRO", 
    "FELIPE DE SOUZA BISPO", "JOSE CICERO CORREIA DA SILVA", "HIGOR PEREIRA SILVA DE JESUS", 
    "JOAO MARCOS BARONE DE SOUSA", "FELIPE ROCHA PEREIRA", "PAULO HENRIQUE OLIVEIRA DOS SANTOS", 
    "RENATO MARQUES CAMPOREZ", "IGOR SÁ", "JUCELI DA SOLEDADE OLIVEIRA", "VINICIUS DE SOUZA SPADETO",
    "ADEILTON ARAUJO SANTOS", "ELTON CANALLI DE OLIVEIRA", "GILMAR DIAS OLIVEIRA", 
    "MATEUS SILVA BONIM", "JEFFERSON ALVES DE OLIVEIRA", "NILDERLEI HENRIQUE ALVARENGA", 
    "ALEXANDRO BATISTA COSTA", "RAFAEL BARCELLOS", "LUCAS PORTO", "KHAYO", "VANDERLEI"
]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): return padrao
    try:
        with open(arquivo, 'r', encoding='utf-8') as f: return json.load(f)
    except: return padrao

def formatar_prefixo(nome):
    return nome.split(" ")[0].replace("-", " ")

def limpar_nome_colab(nome_completo):
    if not nome_completo: return ""
    partes = nome_completo.split()
    return " ".join(partes[:2]) if len(partes) >= 2 else nome_completo

def data_em_portugues():
    meses = {"January": "janeiro", "February": "fevereiro", "March": "março", "April": "abril", "May": "maio", "June": "junho", "July": "julho", "August": "agosto", "September": "setembro", "October": "outubro", "November": "novembro", "December": "dezembro"}
    dias_semana = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
    agora = datetime.now()
    return f"{dias_semana[agora.strftime('%A')]}, dia {agora.strftime('%d')} de {meses[agora.strftime('%B')]} de {agora.strftime('%Y')}"

frota = carregar_dados(ARQUIVO_FROTA, FROTA_PADRAO)
colaboradores = sorted(carregar_dados(ARQUIVO_COLAB, COLAB_PADRAO))
lista_total = sorted([item for sublist in frota.values() for item in sublist])

# --- INTERFACE ---
st.sidebar.title("🏗️ Menu")
aba = st.sidebar.radio("Escolha:", ["Equipamentos Utilizados", "Disponibilidade", "Gestão"])

if aba == "Equipamentos Utilizados":
    st.title("📋 Relação de Equipamentos")
    
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    st.subheader("👥 Equipe")
    exp1 = st.expander("Definir Responsáveis", expanded=True)
    with exp1:
        c1, c2 = st.columns(2)
        with c1:
            sup_casp = st.selectbox("CASP - Supervisor", colaboradores)
            ctrl_casp = st.selectbox("CASP - Controlador", colaboradores)
            enc_c8 = st.selectbox("CANTEIRO 8 - Encarregado", colaboradores)
        with c2:
            ctrl_c8 = st.selectbox("CANTEIRO 8 - Controlador", colaboradores)
            enc_pas = st.selectbox("PAS - Encarregado", colaboradores)
            ctrl_bacia = st.selectbox("Controlador da Bacia", colaboradores)
            
    st.subheader("🛠️ Executadores - ADM")
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        exec1_nome = st.selectbox("Executador 1", colaboradores)
        exec1_task = st.text_input("Tarefa 1", value="Confecção do caminhão seguro em frente ao pátio 6.")
    with col_adm2:
        exec2_nome = st.selectbox("Executador 2", colaboradores)
        exec2_task = st.text_input("Tarefa 2", value="Limpeza pelo pátio 6, dando prioridade às canaletas.")

    st.markdown("---")
    st.subheader("🚜 Equipamentos")
    disp = lista_total.copy()
    u24 = st.multiselect("(24 horas)", disp); disp = [e for e in disp if e not in u24]
    u12 = st.multiselect("(12 horas)", disp); disp = [e for e in disp if e not in u12]
    uadm = st.multiselect("(ADM)", disp)

    if st.button("GERAR RELATÓRIO COMPLETO"):
        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        # Bloco Equipe
        if sup_casp or ctrl_casp:
            txt += "CASP\n"
            if sup_casp: txt += f"Supervisor: {limpar_nome_colab(sup_casp)}\n"
            if ctrl_casp: txt += f"Controlador: {limpar_nome_colab(ctrl_casp)}\n"
            txt += "\n"
            
        if enc_c8 or ctrl_c8:
            txt += "CANTEIRO 8\n"
            if enc_c8: txt += f"Encarregado: {limpar_nome_colab(enc_c8)}\n"
            if ctrl_c8: txt += f"Controlador: {limpar_nome_colab(ctrl_c8)}\n"
            txt += "\n"
            
        if enc_pas:
            txt += f"PAS\nEncarregado: {limpar_nome_colab(enc_pas)}\n\n"
            
        if exec1_nome or exec2_nome:
            txt += "EXECUTADORES - ADM\n"
            if exec1_nome: txt += f"{limpar_nome_colab(exec1_nome).split()[0]}: {exec1_task}\n"
            if exec2_nome: txt += f"{limpar_nome_colab(exec2_nome).split()[0]}: {exec2_task}\n"
            txt += "\n"
            
        if ctrl_bacia:
            txt += f"CONTROLADOR DA BACIA: {limpar_nome_colab(ctrl_bacia)}\n\n"
            
        # Bloco Equipamentos
        for tit, lista in [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", uadm)]:
            if lista:
                txt += f"{tit}\n\n"
                for e in lista: txt += f"✅ {e.replace('-', ' ')} CASP\n"
                txt += "\n"
                
        st.code(txt, language="text")

# --- MANTENDO AS OUTRAS ABAS SIMPLES ---
elif aba == "Disponibilidade":
    st.title("🚜 Disponibilidade")
    st.info("Selecione os equipamentos que estão com defeito.")
    # Lógica de disponibilidade aqui...
elif aba == "Gestão":
    st.title("⚙️ Gestão de Dados")
    st.write("Use para adicionar novos nomes ou máquinas.")
