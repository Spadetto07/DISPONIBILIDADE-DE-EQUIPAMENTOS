import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão CASP Pro", layout="centered") # 'centered' fica melhor para listas verticais

# CSS para deixar os itens da lista mais espaçados e fáceis de clicar no celular
st.markdown("""
    <style>
    .stCheckbox {
        padding: 10px;
        border-bottom: 1px solid #333;
    }
    .stCheckbox:hover {
        background-color: #262730;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. BANCO DE DADOS ---
ARQUIVO_FROTA = 'frota.json'
ARQUIVO_COLAB = 'colaboradores.json'

FROTA_PADRAO = {
    "CAMINHÃO": ["CAM-185", "CAM-250", "CAM-267", "CAM-279", "CAM-306"],
    "CARREGADEIRA": ["CSP-078", "CSP-090", "CSP-091", "CSP-093", "CSP-094", "CSP-096", "CSP-097", "CSP-098", "CSP-100", "CSP-104", "CSP-106", "CSP-107"],
    "ESCAVADEIRA": ["ESE-019", "ESE-023", "ESE-031", "ESE-036", "ESE-039", "ESE-047", "ESE-048", "ESE-049", "ESE-050", "ESE-053", "ESE-055", "LOC-3456", "LOC-7726"],
    "MINI CARREGADEIRA / ESCAVADEIRA": ["MCP-007", "MEE-007"],
    "MOTONIVELADORA": ["MON-021", "MON-022"],
    "PLANTAS": ["ALV-001", "CMB-002", "CMP-001", "USC-001"],
    "RETRO ESCAVADEIRA": ["RTE-029", "RTE-030", "RTE-034", "RTE-035"],
    "TRATOR DE ESTEIRA": ["TSE-019", "TSE-036", "TSE-037", "TSE-046", "TSE-052"]
}

COLAB_PADRAO = ["", "ADILSON DE JESUS SANTOS", "HANDREY FRITZ SERAFIM", "JONATAS FAGUNDES DA COSTA", "PAULO SILAS PONATH", "JOAO VICTOR OLIVEIRA CORATO GABRIEL", "JAMES RIBEIRO CARNEIRO", "FELIPE DE SOUZA BISPO", "JOSE CICERO CORREIA DA SILVA", "HIGOR PEREIRA SILVA DE JESUS", "JOAO MARCOS BARONE DE SOUSA", "FELIPE ROCHA PEREIRA", "PAULO HENRIQUE OLIVEIRA DOS SANTOS", "RENATO MARQUES CAMPOREZ", "IGOR SÁ", "JUCELI DA SOLEDADE OLIVEIRA", "VINICIUS DE SOUZA SPADETO", "ALEXANDRO BATISTA COSTA", "RAFAEL BARCELLOS", "LUCAS NASCIMENTO", "FHELIPE SILVA", "LEONILSON SILVA"]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): return padrao
    try:
        with open(arquivo, 'r', encoding='utf-8') as f: return json.load(f)
    except: return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f: json.dump(dados, f, indent=4, ensure_ascii=False)

def formatar_prefixo(nome): return nome.split(" ")[0].replace("-", " ")

def limpar_nome_colab(nome_completo):
    if not nome_completo: return ""
    partes = nome_completo.split()
    return " ".join(partes[:2]) if len(partes) >= 2 else nome_completo

def data_em_portugues():
    meses = {"January": "janeiro", "February": "fevereiro", "March": "março", "April": "abril", "May": "maio", "June": "junho", "July": "julho", "August": "agosto", "September": "setembro", "October": "outubro", "November": "novembro", "December": "dezembro"}
    dias_semana = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
    agora = datetime.now()
    return f"{dias_semana[agora.strftime('%A')]}, dia {agora.strftime('%d')} de {meses[agora.strftime('%B')]} de {agora.strftime('%Y')}"

# --- CARREGAMENTO ---
frota_raw = carregar_dados(ARQUIVO_FROTA, FROTA_PADRAO)
frota = {k: sorted(v) for k, v in sorted(frota_raw.items())}
colaboradores = sorted(carregar_dados(ARQUIVO_COLAB, COLAB_PADRAO))

# --- NAVEGAÇÃO ---
st.sidebar.title("🏗️ Menu Principal")
aba = st.sidebar.radio("Escolha:", ["Equipamentos Utilizados", "Disponibilidade", "Atividades CASP", "Gestão de Frota", "Gestão de Pessoal"])

# --- 1. EQUIPAMENTOS UTILIZADOS (LISTA VERTICAL ALFABÉTICA) ---
if aba == "Equipamentos Utilizados":
    st.title("📋 Utilização de Máquinas")
    
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    st.markdown("---")
    regime_pincel = st.segmented_control("Selecionar Regime:", options=["24h", "12h", "ADM", "EV"], default="24h")

    if "maquinas_regime" not in st.session_state:
        st.session_state.maquinas_regime = {m: None for cat in frota.values() for m in cat}

    # Lista vertical única em ordem alfabética de todos os equipamentos
    lista_alfabetica = sorted([m for cat in frota.values() for m in cat])

    st.subheader(f"Marque os equipamentos [{regime_pincel}]")
    for m in lista_alfabetica:
        tag = formatar_prefixo(m)
        ja_selecionada = st.session_state.maquinas_regime[m] == regime_pincel
        
        # Checkbox em lista vertical
        if st.checkbox(f"{tag}", value=ja_selecionada, key=f"ut_{m}_{regime_pincel}"):
            st.session_state.maquinas_regime[m] = regime_pincel
        elif ja_selecionada:
            st.session_state.maquinas_regime[m] = None

    if st.button("GERAR RELATÓRIO WHATSAPP", use_container_width=True):
        escolhas_finais = {"24h": [], "12h": [], "ADM": [], "EV": []}
        for m, reg in st.session_state.maquinas_regime.items():
            if reg: escolhas_finais[reg].append(m)

        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        for chave, titulo in [("24h", "(24 horas)"), ("12h", "(12 horas)"), ("ADM", "(ADM)"), ("EV", "(EVENTUAL)")]:
            if escolhas_finais[chave]:
                txt += f"{titulo}\n"
                # Garante ordem alfabética na saída do texto também
                for e in sorted(escolhas_finais[chave]):
                    txt += f"✅ {formatar_prefixo(e)} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

# --- 3. ATIVIDADES CASP (LISTA VERTICAL ALFABÉTICA) ---
elif aba == "Atividades CASP":
    st.title("📝 Relatório de Atividades CASP")
    c1, c2, c3 = st.columns(3)
    with c1: d_c = st.date_input("Data", datetime.now(), key="d_c")
    with c2: l_c = st.selectbox("Letra", ["A", "B", "C", "D"], key="l_c")
    with c3: t_c = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"], key="t_c")

    # Bancos de dados em ordem alfabética
    rec_lista = sorted(["Lama de Aciaria - 2B", "Lama de Alto Forno - P11", "Lama de ETF - P10", "Lama de Varrição - P10", "Resíduo de Varrição - P10", "Lama do Tratamento de Gás - P06", "Lama TK4 - P06", "Lama TK2 (Bacia 03) - P10", "Lama ETB - P6", "Lama do Lava Rodas", "Pó do Despoeiramento (Kopron) - P06", "Pó do Balão", "Pó do 'EP' (P10)", "RESC - P06/P10", "Resíduo de Escavação - P10", "Resíduo de Raspagem de Solo", "Drypit - P01/P13", "Blende Siderúrgico", "Geobag - P1", "Escória Granulada - P13", "RPOF de Venda - P2A", "FMM Calcita", "Sidercal - PAS", "RH1/RH2 - UBC", "Refratário RIP - Rotatória", "Hotcar - Galpão Kopron", "Lama de Escória - P10", "Lixo de Briquetagem", "Rejeito Geral (Vale)", "Rejeito de Briquetagem (Vale)", "Resíduo impureza 3a4 (Vale)", "Água contaminada óleo (P10)"])
    
    sai_lista = sorted(["Siderita (75 a 200mm) - P03/P13", "Drypit (Médio não magnético)", "Ecocarbo I", "Ecocarbo II", "R-POF (p/ Pátio de Minério)", "R-POF (Venda)", "R-Mix (p/ Pátio de Minério)", "R-Bit (p/ Pátio de Minério)", "Lama de Alto Forno (Cooproves)", "Lama de Aciaria (Cooproves)", "Resíduos Sólidos (Cooproves)", "Pó do Balão (p/ PM)", "0a19 Tc5 Britado (p/ PAS)", "0a19 RCC (Pilha 1E/1F)", "Refratário da Coqueria", "Sucata TA de LD", "Sucata F1", "Sucata 3A8", "Sucata de RBIT", "Carvão Vegetal (SunCoke)", "Lastro de Coque", "Pilha 1E/1C/1F", "Válvulas R3", "Degradado de Carbono", "Minério Usina 08", "Siderita Zerada (P03)"])
    
    atv_lista = sorted(["Rotina de organização dos pátios, pilhas e baias", "Carregamento e rechego de materiais", "Subida de Lama de Alto Forno P11", "Corte de lama de aciaria (2B) para Cooproves", "Tombamento de Siderita (P13)", "Blend Pó de Despoeiramento x RIND Bruto", "Mistura e Blend do Pré-Mix P06", "Abastecimento de Peneira Magnética ou Verde", "Limpeza de canaletas e Wind Fence", "Segregação de metálicos com eletroímã", "Retirada de panos da grelha", "Nivelamento de pátio (Patrol)", "Confecção de taludes de contenção", "Retirada de 'negativo' das pilhas", "Empilhamento de 0A19 / RCC", "Aterramento da baia da balança", "Identificação de caminho seguro", "Transporte material limpeza bacia p/ P11", "Raspagem de caçambas com escavadeira", "Corte de RBIT Peneirado (P03)"])

    st.subheader("📥 Recebimento (Ordem A-Z)")
    sel_rec = [i for i in rec_lista if st.checkbox(i, key=f"r_{i}")]

    st.subheader("📤 Saída (Ordem A-Z)")
    sel_sai = [i for i in sai_lista if st.checkbox(i, key=f"s_{i}")]

    st.subheader("🚜 Atividades (Ordem A-Z)")
    sel_atv = [i for i in atv_lista if st.checkbox(i, key=f"a_{i}")]
    
    obs_c = st.text_area("Notas extras:")

    if st.button("🚀 GERAR RELATÓRIO ATIVIDADES", use_container_width=True):
        txt = f"Boa tarde a todos, com segurança!\n\n*Atividades CASP*\n\n📅 Data: {d_c.strftime('%d/%m/%Y')}\n🔠 Letra: {l_c}\n⏰ Turno: {t_c}\n\n📥 Recebimento de Materiais:\n"
        for i in sorted(sel_rec): txt += f"- {i} ✅\n"
        txt += "\n📤 Saída de Materiais:\n"
        for i in sorted(sel_sai): txt += f"- {i} ✅\n"
        txt += "\n🚜 Atividades Executadas:\n"
        for i in sorted(sel_atv): txt += f"- {i}\n"
        if obs_c:
            for line in obs_c.split('\n'):
                if line.strip(): txt += f"- {line.strip()}\n"
        st.code(txt, language="text")

# --- 4. GESTÃO DE FROTA / 5. GESTÃO DE PESSOAL (Mantidos do seu código) ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gestão de Equipamentos")
    with st.expander("➕ Adicionar Novo Equipamento"):
        c_add = st.selectbox("Categoria", sorted(list(frota.keys())))
        n_add = st.text_input("Novo Prefixo")
        if st.button("Salvar Novo"):
            if n_add:
                frota[c_add].append(n_add.upper()); salvar_dados(ARQUIVO_FROTA, frota); st.rerun()

elif aba == "Gestão de Pessoal":
    st.title("👤 Gestão de Colaboradores")
    novo_colab = st.text_input("Nome do Colaborador")
    if st.button("Adicionar Colaborador"):
        if novo_colab:
            colaboradores.append(novo_colab.upper()); salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()
