import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra", layout="wide")

# --- TRADUÇÃO DE DATA ---
def data_em_portugues():
    meses_trad = {
        "January": "Janeiro", "February": "Fevereiro", "March": "Março",
        "April": "Abril", "May": "Maio", "June": "Junho",
        "July": "Julho", "August": "Agosto", "September": "Setembro",
        "October": "Outubro", "November": "Novembro", "December": "Dezembro"
    }
    agora = datetime.now()
    return f"{agora.strftime('%d')} de {meses_trad.get(agora.strftime('%B'))} de {agora.strftime('%Y')}"

# --- BANCO DE DADOS ---
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

COLAB_LISTA_NOVA = [
    "ADILSON JESUS", "HANDREY FRITZ", "JONATAS FAGUNDES", "PAULO SILAS", "ALISSON NASCIMENTO",
    "ANDRE LUIZ", "JULIO MESSIAS", "JOAO VICTOR", "JAMES RIBEIRO", "FELIPE SOUZA",
    "JOSE CICERO", "HENRIQUE JESUS", "HIGOR PEREIRA", "JOAO MARCOS", "FELIPE ROCHA",
    "PAULO HENRIQUE", "RENATO MARQUES", "FILIPE NASCIMENTO", "IGOR SÁ", "RIAN SANTOS",
    "JUCELI SOLEDADE", "ALEXANDRO BATISTA", "RAFAEL BARCELLOS", "VINICIUS SOUZA",
    "LUCAS NASCIMENTO", "RAFAEL TREVIZANELI", "FHELIPE SILVA", "LEONILSON SILVA"
]

def carregar_dados(arquivo, padrao):
    if not os.path.exists(arquivo): return padrao
    with open(arquivo, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def limpar_nome(n):
    partes = n.split()
    return " ".join(partes[:2]) if len(partes) >= 2 else n

# Iniciar Dados
frota = carregar_dados(ARQUIVO_FROTA, FROTA_PADRAO)
colaboradores = carregar_dados(ARQUIVO_COLAB, sorted(COLAB_LISTA_NOVA))
lista_completa_equip = sorted([item for sublist in frota.values() for item in sublist])

# --- NAVEGAÇÃO ---
st.sidebar.title("🏗️ Menu Principal")
aba = st.sidebar.radio("Ir para:", ["Disponibilidade", "Equipamentos Utilizados", "Gestão de Frota", "Gestão de Pessoal"])

# --- 1. DISPONIBILIDADE ---
if aba == "Disponibilidade":
    st.title("🚜 Disponibilidade")
    rel_d = {}
    for cat, lista in frota.items():
        with st.expander(f"📂 {cat}"):
            itens = []
            for e in lista:
                tag = e.replace("-", " ", 1)
                if st.checkbox(f"{tag}", key=f"d_{e}"):
                    obs = st.text_input(f"Defeito p/ {tag}", key=f"o_{e}")
                    itens.append(f"❌ {tag} - {obs}" if obs else f"✅ {tag}")
            if itens: rel_d[cat] = itens
    if st.button("GERAR RELATÓRIO"):
        res = f"DISPONIBILIDADE DE EQUIPAMENTOS - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        for c, l in rel_d.items(): res += f"{c}\n" + "\n".join(l) + "\n\n"
        st.code(res, language="text")

# --- 2. UTILIZADOS ---
elif aba == "Equipamentos Utilizados":
    st.title("📋 Equipamentos Utilizados")
    c1, c2, c3 = st.columns(3)
    with c1: saud = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with c2: let = st.selectbox("Letra", ["A", "B", "C", "D"])
    with c3: tur = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])
    
    cp1, cp2 = st.columns(2)
    with cp1: superv = st.selectbox("Supervisor", colaboradores)
    with cp2: encar = st.selectbox("Encarregado", colaboradores)

    st.markdown("---")
    disp = lista_completa_equip.copy()
    u24 = st.multiselect("24h", disp); disp = [e for e in disp if e not in u24]
    u12 = st.multiselect("12h", disp); disp = [e for e in disp if e not in u12]
    uadm = st.multiselect("ADM", disp); disp = [e for e in disp if e not in uadm]
    uev = st.multiselect("EVENTUAL", disp)

    if st.button("GERAR"):
        txt = f"{saud}\nCom segurança.\n\nHoje, {data_em_portugues()}\nSegue relação:\n\n"
        txt += f"Supervisor: {limpar_nome(superv)}\nEncarregado: {limpar_nome(encar)}\nLetra: {let}\nTurno: {tur}\n\n"
        for t, l in [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", uadm), ("(EVENTUAL)", uev)]:
            if l:
                txt += f"{t}\n"
                for e in l: txt += f"✅ {e.replace('-', ' ', 1)} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

# --- 3. GESTÃO FROTA ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gerir Equipamentos")
    with st.expander("➕ Adicionar"):
        ca = st.selectbox("Categoria", list(frota.keys()))
        na = st.text_input("Prefixo (Ex: ESE-048)")
        if st.button("Salvar"):
            frota[ca].append(na); salvar_dados(ARQUIVO_FROTA, frota); st.rerun()
    with st.expander("✏️ Editar/Excluir"):
        ce = st.selectbox("Categoria ", list(frota.keys()))
        ie = st.selectbox("Equipamento", frota[ce])
        ne = st.text_input("Novo Nome", value=ie)
        c_ed1, c_ed2 = st.columns(2)
        with c_ed1:
            if st.button("Atualizar"):
                idx = frota[ce].index(ie); frota[ce][idx] = ne; salvar_dados(ARQUIVO_FROTA, frota); st.rerun()
        with c_ed2:
            if st.button("Excluir"):
                frota[ce].remove(ie); salvar_dados(ARQUIVO_FROTA, frota); st.rerun()

# --- 4. GESTÃO PESSOAL ---
elif aba == "Gestão de Pessoal":
    st.title("👤 Gerir Colaboradores")
    nc = st.text_input("Nome Completo")
    if st.button("Adicionar"):
        if nc: colaboradores.append(nc); salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()
    st.markdown("---")
    cr = st.selectbox("Editar/Remover Colaborador", colaboradores)
    n_edit_c = st.text_input("Editar Nome Selecionado", value=cr)
    ce1, ce2 = st.columns(2)
    with ce1:
        if st.button("Salvar Alteração"):
            idx_c = colaboradores.index(cr); colaboradores[idx_c] = n_edit_c; salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()
    with ce2:
        if st.button("Remover Permanentemente"):
            colaboradores.remove(cr); salvar_dados(ARQUIVO_COLAB, colaboradores); st.rerun()