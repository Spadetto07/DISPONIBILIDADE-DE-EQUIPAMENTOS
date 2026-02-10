import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão CASP Pro", layout="wide")

# CSS para esconder os checkboxes originais e criar um visual de "Botão/Card"
st.markdown("""
    <style>
    .stCheckbox {
        background-color: #262730;
        padding: 8px 15px;
        border-radius: 10px;
        border: 1px solid #4B4B4B;
        margin-bottom: 5px;
    }
    .stCheckbox:hover {
        border-color: #FF4B4B;
    }
    div[data-dt-idx] {  display: none; }
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

# --- 1. EQUIPAMENTOS UTILIZADOS (VERSÃO LIMPA) ---
if aba == "Equipamentos Utilizados":
    st.title("📋 Utilização de Máquinas")
    
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    # Seleção de Pessoal resumida em um expander
    with st.expander("👤 Definir Responsáveis", expanded=False):
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            sup_casp = st.selectbox("CASP - Supervisor", colaboradores)
            ctrl_casp = st.selectbox("CASP - Controlador", colaboradores)
        with c_p2:
            enc_pas = st.selectbox("PAS - Encarregado", colaboradores)
            ctrl_bacia = st.selectbox("Controlador da Bacia", colaboradores)

    st.markdown("---")
    st.subheader("🚜 Selecione o Regime e marque as máquinas")
    
    # 1. Escolha o regime primeiro (Pincel)
    regime_pincel = st.segmented_control(
        "Selecionar Regime:", 
        options=["24h", "12h", "ADM", "EV"], 
        default="24h"
    )

    # 2. Grid de máquinas
    escolhas_finais = {"24h": [], "12h": [], "ADM": [], "EV": []}
    
    # Usamos o session_state para persistir as escolhas entre os regimes
    if "maquinas_regime" not in st.session_state:
        st.session_state.maquinas_regime = {m: None for cat in frota.values() for m in cat}

    for cat, maquinas in frota.items():
        with st.expander(f"📂 {cat}", expanded=True):
            cols = st.columns(4)
            for idx, m in enumerate(maquinas):
                tag = formatar_prefixo(m)
                # Verifica se a máquina já pertence a algum regime
                ja_selecionada = st.session_state.maquinas_regime[m] == regime_pincel
                
                if cols[idx % 4].checkbox(tag, value=ja_selecionada, key=f"ut_{m}_{regime_pincel}"):
                    st.session_state.maquinas_regime[m] = regime_pincel
                elif ja_selecionada:
                    # Se desmarcar, remove o regime
                    st.session_state.maquinas_regime[m] = None

    if st.button("GERAR RELATÓRIO WHATSAPP", use_container_width=True):
        # Organiza os dados para o texto
        for m, reg in st.session_state.maquinas_regime.items():
            if reg: escolhas_finais[reg].append(m)

        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        if sup_casp or ctrl_casp:
            txt += "CASP\n"
            if sup_casp: txt += f"Supervisor: {limpar_nome_colab(sup_casp)}\n"
            if ctrl_casp: txt += f"Controlador: {limpar_nome_colab(ctrl_casp)}\n\n"
        
        regimes_config = [("24h", "(24 horas)"), ("12h", "(12 horas)"), ("ADM", "(ADM)"), ("EV", "(EVENTUAL)")]
        for chave, titulo in regimes_config:
            if escolhas_finais[chave]:
                txt += f"{titulo}\n"
                for e in escolhas_finais[chave]:
                    txt += f"✅ {formatar_prefixo(e)} CASP\n"
                txt += "\n"
        
        st.code(txt, language="text")

# --- 2. DISPONIBILIDADE (LAYOUT LIMPO) ---
elif aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
    defeitos = {}
    for cat, lista in frota.items():
        with st.expander(f"📂 {cat}", expanded=True):
            cols = st.columns(4)
            for idx, e in enumerate(lista):
                tag = formatar_prefixo(e)
                with cols[idx % 4]:
                    if st.checkbox(tag, key=f"disp_ch_{e}"):
                        obs = st.text_input("Defeito", key=f"obs_ch_{e}", label_visibility="collapsed", placeholder="Causa...")
                        defeitos[e] = obs if obs else "Manutenção"
                
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

# --- 3. ATIVIDADES CASP (LIMPO) ---
elif aba == "Atividades CASP":
    st.title("📝 Atividades CASP")
    c_c1, c_c2, c_c3 = st.columns(3)
    with c_c1: d_c = st.date_input("Data", datetime.now(), key="d_c")
    with c_c2: l_c = st.selectbox("Letra", ["A", "B", "C", "D"], key="l_c")
    with c_c3: t_c = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"], key="t_c")

    # Listas em colunas para ocupar menos espaço
    rec_lista = sorted(["Lama Aciaria - 2B", "Lama Alto Forno - P11", "Lama ETF - P10", "Resíduo Varrição - P10", "Lama Gás - P06", "Lama TK4", "Lama ETB - P6", "RESC - P06/P10", "Drypit - P01/P13", "FMM Calcita", "RPOF Venda"])
    sai_lista = sorted(["Siderita", "Drypit", "Ecocarbo I", "Ecocarbo II", "R-POF p/ PM", "R-Mix p/ PM", "R-Bit p/ PM", "Lama AF (Cooproves)", "0a19 Tc5", "0a19 RCC"])
    atv_lista = ["Rotina organização", "Carregamento/rechego", "Subida Lama AF P11", "Corte lama AC 2B", "Tombamento Siderita P13", "Blend Pó/RIND P06", "Limpeza canaletas", "Segregação eletroímã", "Nivelamento pátio"]

    st.subheader("📥 Recebimento")
    sel_rec = [i for i in rec_lista if st.checkbox(i, key=f"r_{i}")]
    
    st.subheader("📤 Saída")
    sel_sai = [i for i in sai_lista if st.checkbox(i, key=f"s_{i}")]
    
    st.subheader("🚜 Atividades")
    sel_atv = [i for i in atv_lista if st.checkbox(i, key=f"a_{i}")]
    
    if st.button("GERAR ATIVIDADES", use_container_width=True):
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
    st.markdown("---")
    colab_remover = st.selectbox("Remover Colaborador", colaboradores)
    if st.button("Remover Permanentemente"):
        if colab_remover:
            colaboradores.remove(colab_remover); salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()
