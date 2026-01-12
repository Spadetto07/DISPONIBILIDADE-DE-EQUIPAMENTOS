import streamlit as st
import json
import base64
from github import Github
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Obra", layout="wide")

# --- CONEXÃO COM GITHUB ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["GITHUB_REPO"]
    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Erro de conexão. Verifique os Secrets.")
    st.stop()

def carregar_do_github(caminho, padrao):
    try:
        contents = repo.get_contents(caminho)
        return json.loads(base64.b64decode(contents.content).decode('utf-8'))
    except: return padrao

def salvar_no_github(caminho, dados):
    conteudo_json = json.dumps(dados, indent=4, ensure_ascii=False)
    try:
        contents = repo.get_contents(caminho)
        repo.update_file(contents.path, f"Update {caminho}", conteudo_json, contents.sha)
    except:
        repo.create_file(caminho, "Create file", conteudo_json)

# --- DADOS PADRÃO (AQUI ESTÁ TUDO QUE VOCÊ QUER) ---
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

COLAB_PADRAO = [
    "ADILSON JESUS", "HANDREY FRITZ", "JONATAS FAGUNDES", "PAULO SILAS", "ALISSON NASCIMENTO",
    "ANDRE LUIZ", "JULIO MESSIAS", "JOAO VICTOR", "JAMES RIBEIRO", "FELIPE SOUZA",
    "JOSE CICERO", "HENRIQUE JESUS", "HIGOR PEREIRA", "JOAO MARCOS", "FELIPE ROCHA",
    "PAULO HENRIQUE", "RENATO MARQUES", "FILIPE NASCIMENTO", "IGOR SÁ", "RIAN SANTOS",
    "JUCELI SOLEDADE", "ALEXANDRO BATISTA", "RAFAEL BARCELLOS", "VINICIUS SOUZA",
    "LUCAS NASCIMENTO", "RAFAEL TREVIZANELI", "FHELIPE SILVA", "LEONILSON SILVA"
]

# --- TRADUÇÃO DE DATA ---
def data_pt():
    meses = {"January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"}
    agora = datetime.now()
    return f"{agora.strftime('%d')} de {meses.get(agora.strftime('%B'))} de {agora.strftime('%Y')}"

# Carregar dados salvos ou usar os padrões acima
frota = carregar_do_github("frota.json", FROTA_PADRAO)
colaboradores = carregar_do_github("colaboradores.json", COLAB_PADRAO)
lista_total = sorted([item for sublist in frota.values() for item in sublist])

# --- INTERFACE ---
aba = st.sidebar.radio("Escolha:", ["Disponibilidade", "Equipamentos Utilizados", "Editar Listas"])

if aba == "Disponibilidade":
    st.title("🚜 Disponibilidade")
    rel_d = {}
    for cat, lista in frota.items():
        with st.expander(f"📂 {cat}"):
            for e in lista:
                tag = e.replace("-", " ")
                if st.checkbox(f"{tag}", key=f"d_{e}"):
                    obs = st.text_input(f"Defeito p/ {tag}", key=f"o_{e}")
                    if cat not in rel_d: rel_d[cat] = []
                    rel_d[cat].append(f"❌ {tag} - {obs}" if obs else f"✅ {tag}")
    if st.button("GERAR TEXTO"):
        res = f"DISPONIBILIDADE - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        for c, l in rel_d.items(): res += f"{c}\n" + "\n".join(l) + "\n\n"
        st.code(res, language="text")

elif aba == "Equipamentos Utilizados":
    st.title("📋 Utilizados")
    c1, c2, c3 = st.columns(3)
    with c1: saud = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    with c2: let = st.selectbox("Letra", ["A", "B", "C", "D"])
    with c3: tur = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])
    
    cp1, cp2 = st.columns(2)
    with cp1: superv = st.selectbox("Supervisor", colaboradores)
    with cp2: encar = st.selectbox("Encarregado", colaboradores)

    st.markdown("---")
    disp = lista_total.copy()
    u24 = st.multiselect("24h", disp); disp = [e for e in disp if e not in u24]
    u12 = st.multiselect("12h", disp); disp = [e for e in disp if e not in u12]
    uadm = st.multiselect("ADM", disp); disp = [e for e in disp if e not in uadm]
    uev = st.multiselect("EVENTUAL", disp)

    if st.button("GERAR WHATSAPP"):
        txt = f"{saud}\nCom segurança.\n\nHoje, {data_pt()}\nSegue relação:\n\n"
        s_nome = " ".join(superv.split()[:2])
        e_nome = " ".join(encar.split()[:2])
        txt += f"Supervisor: {s_nome}\nEncarregado: {e_nome}\nLetra: {let}\nTurno: {tur}\n\n"
        for t, l in [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", uadm), ("(EVENTUAL)", uev)]:
            if l:
                txt += f"{t}\n"
                for e in l: txt += f"✅ {e.replace('-', ' ')} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

elif aba == "Editar Listas":
    st.title("⚙️ Configurações Manuais")
    st.write("Use aqui apenas se precisar mudar algum nome ou máquina permanentemente.")
    
    if st.checkbox("Editar Nomes de Colaboradores"):
        novo_c = st.text_input("Adicionar Nome")
        if st.button("Salvar Novo Nome"):
            colaboradores.append(novo_c.upper())
            salvar_no_github("colaboradores.json", sorted(colaboradores))
            st.rerun()
        rem_c = st.selectbox("Remover Nome", colaboradores)
        if st.button("Remover"):
            colaboradores.remove(rem_c)
            salvar_no_github("colaboradores.json", colaboradores)
            st.rerun()
