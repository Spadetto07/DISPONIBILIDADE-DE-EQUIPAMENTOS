import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra Pro", layout="wide")
st.markdown(
    """
    <head>
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="icon" sizes="192x192" href="https://cdn-icons-png.flaticon.com/512/4342/4342728.png">
        <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/4342/4342728.png">
    </head>
    """,
    unsafe_allow_html=True
)

# --- 1. BANCO DE DADOS ---
ARQUIVO_FROTA = 'frota.json'
ARQUIVO_COLAB = 'colaboradores.json'

FROTA_PADRAO = {
    "CAMINHÃO": ["CAM-185", "CAM-250", "CAM-267", "CAM-279", "CAM-306"],
    "CARREGADEIRA": ["CSP-078", "CSP-090", "CSP-091", "CSP-093", "CSP-094", "CSP-096", "CSP-097", "CSP-098", "CSP-100", "CSP-104", "CSP-106", "CSP-107"],
    "ESCAVADEIRA": ["ESE-019", "ESE-023", "ESE-031", "ESE-034", "ESE-036", "ESE-039", "ESE-047", "ESE-048", "ESE-049", "ESE-050", "ESE-053", "ESE-055", "LOC-3456", "LOC-7726"],
    "MINI CARREGADEIRA / ESCAVADEIRA": ["MCP-007", "MEE-007"],
    "MOTONIVELADORA": ["MON-021", "MON-022"],
    "PLANTAS": ["ALV-001", "CMB-002", "CMP-001", "USC-001"],
    "RETRO ESCAVADEIRA": ["RTE-029", "RTE-030", "RTE-034", "RTE-035"],
    "TRATOR DE ESTEIRA": ["TSE-019", "TSE-036", "TSE-037", "TSE-046", "TSE-052"]
}

COLAB_PADRAO = [
    "", "ADILSON DE JESUS SANTOS", "HANDREY FRITZ SERAFIM", "JONATAS FAGUNDES DA COSTA", 
    "PAULO SILAS PONATH", "JOAO VICTOR OLIVEIRA CORATO GABRIEL", "JAMES RIBEIRO CARNEIRO", 
    "FELIPE DE SOUZA BISPO", "JOSE CICERO CORREIA DA SILVA", "HIGOR PEREIRA SILVA DE JESUS", 
    "JOAO MARCOS BARONE DE SOUSA", "FELIPE ROCHA PEREIRA", "PAULO HENRIQUE OLIVEIRA DOS SANTOS", 
    "RENATO MARQUES CAMPOREZ", "IGOR SÁ", "JUCELI DA SOLEDADE OLIVEIRA", "VINICIUS DE SOUZA SPADETO",
    "ALEXANDRO BATISTA COSTA", "RAFAEL BARCELLOS", "LUCAS NASCIMENTO", "FHELIPE SILVA", "LEONILSON SILVA"
]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): return padrao
    try:
        with open(arquivo, 'r', encoding='utf-8') as f: return json.load(f)
    except: return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def formatar_prefixo(nome):
    return nome.split(" ")[0].replace("-", "")

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
    st.title("📋 Relação de Equipamentos Utilizados")
    col1, col2, col3 = st.columns(3)
    with col1: saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with col2: letra = st.selectbox("Letra", ["A", "B", "C", "D"])
    with col3: turno = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    st.subheader("👥 Equipe e Setores")
    with st.expander("Definir Colaboradores por Função", expanded=True):
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
    st.subheader("🚜 Seleção de Máquinas")
    regime_pincel = st.segmented_control("Selecionar Regime:", options=["24h", "12h", "ADM", "EV"], default="24h")

    if "maquinas_regime" not in st.session_state:
        st.session_state.maquinas_regime = {}

    # VISUALIZAÇÃO COM LEGENDAS POR CATEGORIA (A-Z)
    for categoria, lista_m in frota.items():
        st.markdown(f"**{categoria}S**") # Legenda na tela de escolha
        for m in lista_m:
            tag = formatar_prefixo(m)
            ja_selecionada = st.session_state.maquinas_regime.get(m) == regime_pincel
            if st.checkbox(f"{tag}", value=ja_selecionada, key=f"ut_{m}_{regime_pincel}"):
                st.session_state.maquinas_regime[m] = regime_pincel
            elif ja_selecionada:
                st.session_state.maquinas_regime[m] = None
        st.write("")

    if st.button("GERAR RELATÓRIO WHATSAPP"):
        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
        if sup_casp or ctrl_casp:
            txt += "CASP\n"
            if sup_casp: txt += f"Supervisor: {limpar_nome_colab(sup_casp)}\n"
            if ctrl_casp: txt += f"Controlador: {limpar_nome_colab(ctrl_casp)}\n\n"
        
        # GERAÇÃO DO RELATÓRIO IGUAL À FOTO (SEM LEGENDAS DE CATEGORIA NO MEIO)
        for titulo_regime, chave in [("(24 horas)", "24h"), ("(12 horas)", "12h"), ("(ADM)", "ADM"), ("(EVENTUAL)", "EV")]:
            maquinas_ativas = [m for m, r in st.session_state.maquinas_regime.items() if r == chave]
            if maquinas_ativas:
                txt += f"{titulo_regime}\n"
                for e in sorted(maquinas_ativas):
                    txt += f"✅ {formatar_prefixo(e)} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

# --- 2. DISPONIBILIDADE ---
elif aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
    rel_d = {}
    for cat, lista in frota.items():
        with st.expander(f"📂 {cat}", expanded=True):
            itens = []
            for e in lista:
                tag = formatar_prefixo(e)
                if st.checkbox(f"{tag}", key=f"disp_{e}"):
                    obs = st.text_input(f"Defeito para {tag}", key=f"obs_{e}", placeholder="Causa...")
                    itens.append(f"❌ {tag} - {obs}" if obs else f"✅ {tag}")
                else:
                    itens.append(f"✅ {tag}")
            rel_d[cat] = itens
                
    if st.button("GERAR DISPONIBILIDADE"):
        texto = f"DISPONIBILIDADE DE EQUIPAMENTOS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        for c, l in rel_d.items(): 
            texto += f"*{c}*\n" + "\n".join(l) + "\n\n"
        st.code(texto, language="text")

# --- 3. ATIVIDADES CASP ---
elif aba == "Atividades CASP":
    st.title("📝 Relatório de Atividades CASP")
    c1, c2, c3 = st.columns(3)
    with c1: d_c = st.date_input("Data", datetime.now(), key="d_c")
    with c2: l_c = st.selectbox("Letra", ["A", "B", "C", "D"], key="l_c")
    with c3: t_c = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"], key="t_c")

    rec_lista = sorted(["Lama de Aciaria - 2B", "Lama de Alto Forno - P11", "Lama de ETF - P10", "Lama de Varrição - P10", "Resíduo de Varrição - P10", "Lama do Tratamento de Gás - P06", "Lama TK4 - P06", "Lama TK2 (Bacia 03) - P10", "Lama ETB - P6", "Lama do Lava Rodas", "Pó do Despoeiramento - P06", "Pó do Balão", "Pó do 'EP' (P10)", "RESC - P06/P10", "Resíduo de Escavação - P10", "Resíduo de Raspagem de Solo", "Dry Pit - P1", "Blende Siderúrgico", "Geobag - P1", "Escória Granulada - P13", "R-POF Venda", "FMM Calcita", "Sidercal - PAS", "RH1/RH2 - UBC", "Refratário RIP - Rotatória", "Hotcar - Galpão Kopron", "Lama de Escória - P10", "Lixo de Briquetagem", "Rejeito Geral (Vale)", "Rejeito de Briquetagem (Vale)", "Resíduo impureza 3a4 (Vale)", "Água contaminada óleo (P10)"])
    sai_lista = sorted(["Siderita", "Dry Pit - P1", "Ecocarbo I", "Ecocarbo II", "R-POF p/ PM", "R-POF Venda", "R-Mix", "R-Bit p/ PM", "Lama de Alto Forno (Cooproves)", "Lama de Aciaria (Cooproves)", "Resíduos Sólidos (Cooproves)", "Pó do Balão (p/ PM)", "0a19 Tc5 Britado (p/ PAS)", "0a19 RCC (Pilha 1E/1F)", "Refratário da Coqueria", "Sucata TA de LD", "Sucata F1", "Sucata 3A8", "Sucata de RBIT", "Carvão Vegetal (SunCoke)", "Lastro de Coque", "Pilha 1E/1C/1F", "Válvulas R3", "Degradado de Carbono", "Minério Usina 08", "Siderita Zerada (P03)"])
    atv_lista = sorted(["Rotina de organização dos pátios, pilhas e baias", "Carregamento e rechego de materiais (otimização de espaço)", "Carregamento e transporte de Lama de alto forno bruta para peneira verde", "Corte de lama de aciaria (2B) para Cooproves", "rechego e mistura siderita P13", "Blend Pó de Despoeiramento x RIND Bruto", "Carregamento de R-pof P/ PM", "Abastecimento de Peneira Magnética ou Verde", "Limpeza de canaletas e Wind Fence", "Segregação de metálicos com eletroímã", "Retirada de panos da grelha", "Nivelamento de pátio (Patrol)", "Confecção de taludes de contenção", "Retirada de 'negativo' das pilhas", "Empilhamento de 0A19 / RCC", "Aterramento da baia da balança", "Identificação de caminho seguro", "Transporte material limpeza bacia p/ P11", "Rechego de R-pof pátio 2A", "Carregamento e transporte de R-Mix p/ PM"])

    st.subheader("📥 Recebimento")
    sel_rec = [i for i in rec_lista if st.checkbox(i, key=f"r_{i}")]
    st.subheader("📤 Saída")
    sel_sai = [i for i in sai_lista if st.checkbox(i, key=f"s_{i}")]
    st.subheader("🚜 Atividades")
    sel_atv = [i for i in atv_lista if st.checkbox(i, key=f"a_{i}")]
    
    if st.button("🚀 GERAR RELATÓRIO ATIVIDADES"):
        txt = f"Boa tarde a todos, com segurança!\n\n*Atividades CASP*\n\n📅 *Data:* {d_c.strftime('%d/%m/%Y')}\n🔠 *Letra:* {l_c}\n⏰ *Turno:* {t_c}\n\n📥 *Recebimento de Materiais:*\n"
        for i in sorted(sel_rec): txt += f"- {i} ✅\n"
        txt += "\n📤 *Saída de Materiais:*\n"
        for i in sorted(sel_sai): txt += f"- {i} ✅\n"
        txt += "\n🚜 *Atividades Executadas:*\n"
        for i in sorted(sel_atv): txt += f"- {i}\n"
        st.code(txt, language="text")

# --- 4. GESTÃO DE FROTA ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gestão de Equipamentos")
    
    with st.expander("➕ Adicionar Novo Equipamento"):
        c_add = st.selectbox("Categoria para adicionar", sorted(list(frota.keys())))
        n_add = st.text_input("Novo Prefixo (Ex: ESE-048)")
        if st.button("Salvar Novo"):
            if n_add:
                frota[c_add].append(n_add.upper())
                salvar_dados(ARQUIVO_FROTA, frota)
                st.rerun()

    with st.expander("✏️ Editar Equipamento"):
        c_ed = st.selectbox("Categoria ", sorted(list(frota.keys())), key="cat_ed")
        item_ed = st.selectbox("Equipamento para editar", sorted(frota[c_ed]), key="item_ed")
        n_ed = st.text_input("Novo Nome", value=item_ed)
        if st.button("Salvar Alteração"):
            frota[c_ed].remove(item_ed)
            frota[c_ed].append(n_ed.upper())
            salvar_dados(ARQUIVO_FROTA, frota)
            st.rerun()

    with st.expander("❌ Excluir Equipamento"):
        c_rm = st.selectbox("Categoria  ", sorted(list(frota.keys())), key="cat_rm")
        item_rm = st.selectbox("Equipamento para apagar", sorted(frota[c_rm]), key="item_rm")
        if st.button("Confirmar Exclusão"):
            frota[c_rm].remove(item_rm)
            salvar_dados(ARQUIVO_FROTA, frota)
            st.rerun()

# --- 5. GESTÃO DE PESSOAL ---
elif aba == "Gestão de Pessoal":
    st.title("👤 Gestão de Colaboradores")
    
    with st.expander("➕ Adicionar Colaborador"):
        novo_colab = st.text_input("Nome do Colaborador")
        if st.button("Adicionar"):
            if novo_colab:
                colaboradores.append(novo_colab.upper())
                salvar_dados(ARQUIVO_COLAB, colaboradores)
                st.rerun()
    
    with st.expander("✏️ Editar Colaborador"):
        colab_editar = st.selectbox("Selecionar Colaborador", colaboradores, key="edit_col")
        novo_nome_colab = st.text_input("Novo Nome", value=colab_editar)
        if st.button("Salvar Mudança"):
            colaboradores.remove(colab_editar)
            colaboradores.append(novo_nome_colab.upper())
            salvar_dados(ARQUIVO_COLAB, colaboradores)
            st.rerun()

    with st.expander("❌ Remover Colaborador"):
        colab_remover = st.selectbox("Remover Colaborador", colaboradores, key="rem_col")
        if st.button("Remover Permanentemente"):
            if colab_remover:
                colaboradores.remove(colab_remover)
                salvar_dados(ARQUIVO_COLAB, colaboradores)
                st.rerun()
