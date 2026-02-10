import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra Pro", layout="wide")

# CSS para melhorar a estética dos cards e seletores
st.markdown("""
    <style>
    .stCheckbox { background-color: #262730; padding: 5px; border-radius: 5px; margin-bottom: 2px; }
    .status-box { border: 1px solid #4B4B4B; padding: 10px; border-radius: 10px; background-color: #1E1E1E; margin-bottom: 10px; }
    .category-header { color: #FF4B4B; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #333; }
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

# --- 1. EQUIPAMENTOS UTILIZADOS ---
if aba == "Equipamentos Utilizados":
    st.title("📋 Painel de Utilização de Máquinas")
    
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    st.subheader("👥 Equipe Responsável")
    with st.expander("Definir Colaboradores", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            sup_casp = st.selectbox("CASP - Supervisor", colaboradores)
            ctrl_casp = st.selectbox("CASP - Controlador", colaboradores)
            enc_c8 = st.selectbox("CANTEIRO 8 - Encarregado", colaboradores)
        with c2:
            ctrl_c8 = st.selectbox("CANTEIRO 8 - Controlador", colaboradores)
            enc_pas = st.selectbox("PAS - Encarregado", colaboradores)
            ctrl_bacia = st.selectbox("Controlador da Bacia", colaboradores)

    st.markdown("---")
    st.subheader("🚜 Distribuição de Máquinas")
    
    # Lógica de seleção por chips/grid
    selecoes = {"24h": [], "12h": [], "ADM": [], "EV": []}
    
    for cat, maquinas in frota.items():
        st.markdown(f"<div class='category-header'>{cat}</div>", unsafe_allow_html=True)
        # Criar colunas para os cards (4 por linha)
        cols_grid = st.columns(4)
        for idx, m in enumerate(maquinas):
            with cols_grid[idx % 4]:
                tag = formatar_prefixo(m)
                # Radio horizontal para escolha rápida do turno
                regime = st.radio(f"**{tag}**", ["-", "24h", "12h", "ADM", "EV"], key=f"ut_{m}", horizontal=True, label_visibility="visible")
                if regime != "-":
                    selecoes[regime].append(m)

    if st.button("GERAR RELATÓRIO WHATSAPP", use_container_width=True):
        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        # Pessoal
        if sup_casp or ctrl_casp:
            txt += "CASP\n"
            if sup_casp: txt += f"Supervisor: {limpar_nome_colab(sup_casp)}\n"
            if ctrl_casp: txt += f"Controlador: {limpar_nome_colab(ctrl_casp)}\n"
            txt += "\n"
        
        # Máquinas por regime
        regimes_map = {"24h": "(24 horas)", "12h": "(12 horas)", "ADM": "(ADM)", "EV": "(EVENTUAL)"}
        for sigla, titulo in regimes_map.items():
            if selecoes[sigla]:
                txt += f"{titulo}\n"
                for e in selecoes[sigla]:
                    txt += f"✅ {formatar_prefixo(e)} CASP\n"
                txt += "\n"
        
        st.code(txt, language="text")

# --- 2. DISPONIBILIDADE ---
elif aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
    defeitos = {}
    for cat, lista in frota.items():
        st.markdown(f"#### {cat}")
        cols = st.columns(4)
        for idx, e in enumerate(lista):
            tag = formatar_prefixo(e)
            with cols[idx % 4]:
                if st.checkbox(tag, key=f"disp_{e}"):
                    obs = st.text_input("Defeito", key=f"obs_{e}", placeholder="Causa...")
                    defeitos[e] = obs if obs else "Manutenção"
        st.markdown("---")
                
    if st.button("GERAR DISPONIBILIDADE", use_container_width=True):
        texto = f"DISPONIBILIDADE DE EQUIPAMENTOS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        for cat, lista in frota.items():
            texto += f"*{cat}*\n"
            for e in lista:
                tag = formatar_prefixo(e)
                if e in defeitos: texto += f"❌ {tag} - {defeitos[e]}\n"
                else: texto += f"✅ {tag}\n"
            texto += "\n"
        st.code(texto, language="text")

# --- 3. ATIVIDADES CASP ---
elif aba == "Atividades CASP":
    st.title("📝 Relatório de Atividades CASP")
    c1, c2, c3 = st.columns(3)
    with c1: d_c = st.date_input("Data", datetime.now())
    with c2: l_c = st.selectbox("Letra", ["A", "B", "C", "D"], key="l_c")
    with c3: t_c = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"], key="t_c")

    rec_lista = sorted(["Lama de Aciaria - 2B", "Lama de Alto Forno - P11", "Lama de ETF - P10", "Resíduo de Varrição - P10", "Lama do Tratamento de Gás - P06", "Lama TK4 - P06", "Lama ETB - P6", "RESC - P06/P10", "Drypit - P01/P13", "FMM Calcita", "RPOF Venda"])
    sai_lista = sorted(["Siderita", "Drypit", "Ecocarbo I", "Ecocarbo II", "R-POF p/ PM", "R-Mix p/ PM", "R-Bit p/ PM", "Lama AF (Cooproves)", "0a19 Tc5", "0a19 RCC"])
    atv_lista = ["Rotina de organização", "Carregamento e rechego", "Subida de Lama AF P11", "Corte de lama AC 2B", "Tombamento Siderita P13", "Blend Pó/RIND P06", "Limpeza canaletas/Wind Fence", "Segregação eletroímã", "Abastecimento Peneira", "Nivelamento de pátio"]

    st.markdown("### 📥 Recebimento")
    sel_rec = [i for i in rec_lista if st.checkbox(i, key=f"r_{i}")]
    st.markdown("### 📤 Saída")
    sel_sai = [i for i in sai_lista if st.checkbox(i, key=f"s_{i}")]
    st.markdown("### 🚜 Atividades")
    sel_atv = [i for i in atv_lista if st.checkbox(i, key=f"a_{i}")]
    
    if st.button("GERAR ATIVIDADES"):
        txt = f"Boa tarde a todos, com segurança!\n\n*Atividades CASP*\n\n📅 Data: {d_c.strftime('%d/%m/%Y')}\n🔠 Letra: {l_c}\n⏰ Turno: {t_c}\n\n📥 Recebimento:\n"
        for i in sel_rec: txt += f"- {i} ✅\n"
        txt += "\n📤 Saída:\n"
        for i in sel_sai: txt += f"- {i} ✅\n"
        txt += "\n🚜 Atividades:\n"
        for i in sel_atv: txt += f"- {i}\n"
        st.code(txt, language="text")

# --- 4. GESTÃO DE FROTA ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gestão de Equipamentos")
    with st.expander("➕ Adicionar Novo Equipamento"):
        c_add = st.selectbox("Categoria", sorted(list(frota.keys())))
        n_add = st.text_input("Novo Prefixo")
        if st.button("Salvar Novo"):
            if n_add:
                frota[c_add].append(n_add.upper()); salvar_dados(ARQUIVO_FROTA, frota); st.rerun()

# --- 5. GESTÃO DE PESSOAL ---
elif aba == "Gestão de Pessoal":
    st.title("👤 Gestão de Colaboradores")
    novo_colab = st.text_input("Nome do Colaborador")
    if st.button("Adicionar Colaborador"):
        if novo_colab:
            colaboradores.append(novo_colab.upper()); salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()
