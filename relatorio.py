import streamlit as st
import json
import base64
from github import Github
from datetime import datetime

# --- CONFIGURAÇÃO E CONEXÃO GITHUB ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["GITHUB_REPO"]
g = Github(TOKEN)
repo = g.get_repo(REPO_NAME)

def salvar_no_github(caminho_arquivo, dados):
    conteudo_json = json.dumps(dados, indent=4, ensure_ascii=False)
    contents = repo.get_contents(caminho_arquivo)
    repo.update_file(contents.path, f"Atualização de dados: {datetime.now()}", conteudo_json, contents.sha)

def carregar_do_github(caminho_arquivo, padrao):
    try:
        contents = repo.get_contents(caminho_arquivo)
        return json.loads(base64.b64decode(contents.content).decode('utf-8'))
    except:
        return padrao

# --- CARREGAMENTO INICIAL ---
frota = carregar_do_github("frota.json", {})
colaboradores = carregar_do_github("colaboradores.json", [])

# --- ABA DE GESTÃO (EXEMPLO DE SALVAMENTO REAL) ---
st.title("⚙️ Gestão de Obra")

with st.expander("👤 Adicionar Colaborador"):
    novo_nome = st.text_input("Nome")
    if st.button("Gravar no GitHub"):
        colaboradores.append(novo_nome)
        salvar_no_github("colaboradores.json", colaboradores)
        st.success("Gravado com sucesso no GitHub! Pode atualizar o código que este nome não some mais.")
        st.rerun()

# O restante das tuas abas de relatório continuam iguais...
