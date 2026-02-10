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
    "ESCAVADEIRA": ["ESE-019", "ESE-023", "ESE-031", "ESE-036", "ESE-039", "ESE-047", "ESE-048", "ESE-049", "ESE-050", "ESE-053", "ESE-055", "LOC-3456", "LOC-7726"],
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

# --- CARREGAMENTO ---
frota_raw = carregar_dados(ARQUIVO_FROTA, FROTA_PADRAO)
frota = {k: sorted(v) for k, v in sorted(frota_raw.items())}
colaboradores = sorted(carregar_dados(ARQUIVO_COLAB, COLAB_PADRAO))
lista_total = sorted([item for sublist in frota.values() for item in sublist])

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
            
    st.subheader("🛠️ Executadores - ADM")
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        exec1_nome = st.selectbox("Executador 1", colaboradores)
        exec1_task = st.text_input("Tarefa 1", value="Confecção do caminhão seguro em frente ao pátio 6.")
    with col_adm2:
        exec2_nome = st.selectbox("Executador 2", colaboradores)
        exec2_task = st.text_input("Tarefa 2", value="Limpeza pelo pátio 6, dando prioridade às canaletas.")

    st.markdown("---")
    st.subheader("🚜 Seleção de Máquinas")
    disp = lista_total.copy()
    u24 = st.multiselect("(24 horas)", disp); disp = [e for e in disp if e not in u24]
    u12 = st.multiselect("(12 horas)", disp); disp = [e for e in disp if e not in u12]
    uadm = st.multiselect("(ADM)", disp); disp = [e for e in disp if e not in uadm]
    uev = st.multiselect("(EVENTUAL)", disp)

    if st.button("GERAR RELATÓRIO WHATSAPP"):
        txt = f"{saudacao}\nCom segurança.\n\n{data_em_portugues()}\n\nSegue a relação de equipamentos utilizados:\n\n"
        txt += f"Letra: {letra}\nTurno: {turno}\n\n"
        
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
        if enc_pas: txt += f"PAS\nEncarregado: {limpar_nome_colab(enc_pas)}\n\n"
        if exec1_nome or exec2_nome:
            txt += "EXECUTADORES - ADM\n"
            if exec1_nome: txt += f"{limpar_nome_colab(exec1_nome).split()[0]}: {exec1_task}\n"
            if exec2_nome: txt += f"{limpar_nome_colab(exec2_nome).split()[0]}: {exec2_task}\n"
            txt += "\n"
        if ctrl_bacia: txt += f"CONTROLADOR DA BACIA: {limpar_nome_colab(ctrl_bacia)}\n\n"
            
        for tit, lista in [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", uadm), ("(EVENTUAL)", uev)]:
            if lista:
                txt += f"{tit}\n"
                for e in lista: txt += f"✅ {formatar_prefixo(e)} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

# --- 2. DISPONIBILIDADE ---
elif aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
    rel_d = {}
    for cat, lista in frota.items():
        with st.expander(f"📂 {cat}", expanded=False):
            itens = []
            for e in lista:
                tag = formatar_prefixo(e)
                if st.checkbox(f"{tag}", key=f"disp_{cat}_{e}"):
                    obs = st.text_input(f"Defeito para {tag}", key=f"obs_{cat}_{e}")
                    itens.append(f"❌ {tag} - {obs}" if obs else f"✅ {tag}")
            if itens: rel_d[cat] = itens
                
    if st.button("GERAR DISPONIBILIDADE"):
        texto = f"DISPONIBILIDADE DE EQUIPAMENTOS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        for c, l in rel_d.items(): 
            texto += f"{c}\n" + "\n".join(l) + "\n\n"
        st.code(texto, language="text")

# --- 3. ATIVIDADES CASP (BANCO COMPLETO) ---
elif aba == "Atividades CASP":
    st.title("📝 Relatório de Atividades CASP")
    c1, c2, c3 = st.columns(3)
    with c1: d_casp = st.date_input("Data", datetime.now())
    with c2: l_casp = st.selectbox("Letra", ["A", "B", "C", "D"])
    with c3: t_casp = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])

    # BANCO DE DADOS COMPLETO EXTRAÍDO DOS RELATÓRIOS
    rec_lista = sorted([
        "Lama de Aciaria - 2B", "Lama de Alto Forno - P11", "Lama de ETF - P10", "Lama de Varrição - P10",
        "Resíduo de Varrição - P10", "Lama do Tratamento de Gás - P06", "Lama TK4 - P06", "Lama TK2 (Bacia 03) - P10",
        "Lama ETB - P6", "Lama do Lava Rodas", "Pó do Despoeiramento (Kopron) - P06", "Pó do Balão",
        "Pó do 'EP' (P10 vindo do P1/P2)", "Resíduo de Construção Civil (RESC) - P06/P10", "Resíduo de Escavação - P10",
        "Resíduo de Raspagem de Solo", "Drypit - P01 / P13", "Blende Siderúrgico", "Geobag - P1", "Escória Granulada - P13",
        "RPOF de Venda - P2A", "FMM Cascalho Calcítico (Calcita) - P1", "Sidercal - PAS", "RH1 / RH2 - UBC",
        "Refratário da Coqueria / LTQ / RIP - Rotatória", "Hotcar - Galpão Kopron", "Lama de Escória - P10",
        "Lixo de Briquetagem", "Rejeito Geral (Vale)", "Rejeito de Briquetagem (Vale)", "Resíduo com impureza 3a4 (Vale)",
        "Água contaminada com óleo/graxa (Bacia P10)"
    ])
    
    sai_lista = sorted([
        "Siderita (75 a 200mm) - P03 / P13", "Drypit (Médio não magnético)", "Ecocarbo I", "Ecocarbo II",
        "R-POF (p/ Pátio de Minério)", "R-POF (Venda)", "R-Mix (p/ Pátio de Minério)", 
        "R-Bit (p/ Pátio de Minério ou Peneira Magnética)", "Lama de Alto Forno (Cooproves / PAS / Kopron)",
        "Lama de Aciaria (Carregamento Cooproves)", "Resíduos Sólidos (Carregamento Cooproves)",
        "Pó do Balão (p/ Pátio de Minério)", "0a19 Tc5 Britado (p/ PAS)", "0a19 RCC (Pilha 1E / 1F)",
        "Refratário da Coqueria / Convertedor", "Sucata TA de LD", "Sucata F1", "Sucata 3A8 (p/ Pátio de Sucatas)",
        "Sucata de RBIT", "Carvão Vegetal (SunCoke)", "Lastro de Coque", "Pilha 1E / 1C / 1F", "Válvulas R3",
        "Degradado de Carbono (Cossipress)", "Minério Usina 08", "Siderita Zerada (P03)"
    ])
    
    atv_lista = [
        "Rotina de organização dos pátios, pilhas e baias", "Carregamento e rechego de materiais (otimização de espaço)",
        "Subida de Lama de Alto Forno (Base para Topo) - P11", "Corte de lama de aciaria (2B) para carregamento Cooproves",
        "Tombamento de Siderita (P13) para abertura de espaço para grelha", "Blend Pó de Despoeiramento x RIND Bruto (Kopron P06)",
        "Mistura e Blend do Pré-Mix (Escavadeira/Carregadeira) - P06", "Abastecimento de Peneira Magnética ou Peneira Verde",
        "Limpeza de canaletas laterais, Wind Fence e bacia da balança (P11/P13/P2B)", "Segregação de metálicos/sucata com eletroímã (Nordberg/P1)",
        "Retirada de panos da grelha da peneira verde", "Nivelamento e regularização de pátio (Motoniveladora/Patrol/Trator)",
        "Confecção de taludes de contenção e separação (ETF/P11/Kopron)", "Retirada de 'negativo' das pilhas (Siderita/Drypit/0a19)",
        "Empilhamento de 0A19 / RCC (Antiga Bacia)", "Aterramento da baia da balança (Lama AC - 2B)",
        "Identificação de caminho seguro (pedestais e cordas)", "Transporte de material de limpeza de bacia para pátio 11",
        "Raspagem de caçambas com escavadeira (Vix)", "Corte de RBIT Peneirado (P03) para carregamento"
    ]

    st.subheader("📥 Recebimento de Materiais")
    sel_rec = st.multiselect("Recebidos:", rec_lista)
    st.subheader("📤 Saída de Materiais")
    sel_sai = st.multiselect("Saídas:", sai_lista)
    st.subheader("🚜 Atividades Executadas")
    sel_atv = st.multiselect("Tarefas:", atv_lista)
    obs_casp = st.text_area("Notas extras (uma por linha):")

    if st.button("GERAR ATIVIDADES WHATSAPP"):
        txt = f"Boa tarde a todos, com segurança!\n\n*Atividades CASP*\n\n📅 Data: {d_casp.strftime('%d/%m/%Y')}\n🔠 Letra: {l_casp}\n⏰ Turno: {t_casp}\n\n📥 Recebimento de Materiais:\n"
        for i in sel_rec: txt += f"- {i} ✅\n"
        txt += "\n📤 Saída de Materiais:\n"
        for i in sel_sai: txt += f"- {i} ✅\n"
        txt += "\n🚜 Atividades Executadas:\n"
        for i in sel_atv: txt += f"- {i}\n"
        if obs_casp:
            for line in obs_casp.split('\n'):
                if line.strip(): txt += f"- {line.strip()}\n"
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
