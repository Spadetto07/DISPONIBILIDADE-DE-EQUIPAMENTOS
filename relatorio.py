import streamlit as st
import json
import base64
from github import Github
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Obra Pro", layout="wide")

# --- CONEXÃO COM GITHUB (BANCO DE DADOS REAL) ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["GITHUB_REPO"]
    g = Github(TOKEN)
    repo = g.get_repo(REPO_NAME)
except Exception as e:
    st.error("Erro nas permissões (Secrets). Verifique o Token no Passo 2.")
    st.stop()

def carregar_do_github(caminho, padrao):
    try:
        contents = repo.get_contents(caminho)
        return json.loads(base64.b64decode(contents.content).decode('utf-8'))
    except:
        return padrao

def salvar_no_github(caminho, dados):
    conteudo_json = json.dumps(dados, indent=4, ensure_ascii=False)
    try:
        contents = repo.get_contents(caminho)
        repo.update_file(contents.path, f"Update {caminho} via App", conteudo_json, contents.sha)
    except:
        repo.create_file(caminho, f"Create {caminho} via App", conteudo_json)

# --- TRADUÇÃO DE DATA ---
def data_em_portugues():
    meses = {"January": "Janeiro", "February": "Fevereiro", "March": "Março", "April": "Abril", "May": "Maio", "June": "Junho", "July": "Julho", "August": "Agosto", "September": "Setembro", "October": "Outubro", "November": "Novembro", "December": "Dezembro"}
    agora = datetime.now()
    return f"{agora.strftime('%d')} de {meses.get(agora.strftime('%B'))} de {agora.strftime('%Y')}"

# --- CARREGAR DADOS ---
frota = carregar_do_github("frota.json", {})
colaboradores = carregar_do_github("colaboradores.json", ["ADILSON JESUS", "HANDREY FRITZ", "JONATAS FAGUNDES", "PAULO SILAS"])

# --- MENU LATERAL ---
aba = st.sidebar.radio("Navegação", ["Disponibilidade", "Equipamentos Utilizados", "Gestão de Frota", "Gestão de Pessoal"])

# --- ABA: DISPONIBILIDADE ---
if aba == "Disponibilidade":
    st.title("🚜 Relatório de Disponibilidade")
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

# --- ABA: EQUIPAMENTOS UTILIZADOS ---
elif aba == "Equipamentos Utilizados":
    st.title("📋 Relatório de Utilizados")
    lista_total = sorted([item for sublist in frota.values() for item in sublist])
    
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

    if st.button("GERAR TEXTO WHATSAPP"):
        txt = f"{saud}\nCom segurança.\n\nHoje, {data_em_portugues()}\nSegue relação:\n\n"
        s_nome = " ".join(superv.split()[:2])
        e_nome = " ".join(encar.split()[:2])
        txt += f"Supervisor: {s_nome}\nEncarregado: {e_nome}\nLetra: {let}\nTurno: {tur}\n\n"
        for t, l in [("(24 horas)", u24), ("(12 horas)", u12), ("(ADM)", uadm), ("(EVENTUAL)", uev)]:
            if l:
                txt += f"{t}\n"
                for e in l: txt += f"✅ {e.replace('-', ' ')} CASP\n"
                txt += "\n"
        st.code(txt, language="text")

# --- ABA: GESTÃO DE FROTA ---
elif aba == "Gestão de Frota":
    st.title("⚙️ Gerir Equipamentos")
    with st.expander("➕ Criar/Adicionar"):
        nova_cat = st.text_input("Nova Categoria (ou selecione abaixo)")
        cat_sel = st.selectbox("Categorias Existentes", list(frota.keys()) if frota else ["Nenhuma"])
        novo_e = st.text_input("Tag (Ex: ESE-048)")
        if st.button("Salvar Equipamento"):
            target = nova_cat if nova_cat else cat_sel
            if target not in frota: frota[target] = []
            if novo_e: frota[target].append(novo_e)
            salvar_no_github("frota.json", frota)
            st.rerun()
    with st.expander("✏️ Editar/Excluir"):
        if frota:
            ce = st.selectbox("Categoria ", list(frota.keys()))
            ie = st.selectbox("Equipamento", frota[ce])
            ne = st.text_input("Novo Nome", value=ie)
            c_ed1, c_ed2 = st.columns(2)
            with c_ed1:
                if st.button("Atualizar"):
                    frota[ce].remove(ie); frota[ce].append(ne)
                    salvar_no_github("frota.json", frota); st.rerun()
            with c_ed2:
                if st.button("Excluir"):
                    frota[ce].remove(ie)
                    salvar_no_github("frota.json", frota); st.rerun()

# --- ABA: GESTÃO DE PESSOAL ---
elif aba == "Gestão de Pessoal":
    st.title("👤 Gestão de Colaboradores")
    with st.expander("➕ Adicionar Novo"):
        novo_c = st.text_input("Nome Completo")
        if st.button("Gravar no GitHub"):
            if novo_c:
                colaboradores.append(novo_c.upper())
                salvar_no_github("colaboradores.json", sorted(colaboradores))
                st.rerun()
    if colaboradores:
        c_sel = st.selectbox("Editar/Remover", colaboradores)
        novo_n = st.text_input("Corrigir Nome", value=c_sel)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Atualizar Nome"):
                colaboradores.remove(c_sel); colaboradores.append(novo_n.upper())
                salvar_no_github("colaboradores.json", sorted(colaboradores)); st.rerun()
        with col2:
            if st.button("Excluir Permanente"):
                colaboradores.remove(c_sel)
                salvar_no_github("colaboradores.json", colaboradores); st.rerun()