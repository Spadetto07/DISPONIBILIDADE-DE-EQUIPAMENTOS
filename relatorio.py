import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Turno", layout="wide")

# --- 1. BANCO DE DADOS ---
ARQUIVO_DADOS = 'frota.json'

FROTA_PADRAO = {
    "GERAL": [
        "CSP-078 - CAT 938G II", "ESE-019 - CAT 320 C", "CAM-185 - FORD 2626",
        "MON-021 - CAT 12H II", "RTE-029 - CAT 416E", "TSE-019 - CAT D6D"
    ]
}

def carregar_frota():
    if not os.path.exists(ARQUIVO_DADOS):
        return FROTA_PADRAO
    with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_frota(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

frota = carregar_frota()
# Transforma a frota numa lista única para facilitar a seleção por turno
lista_completa = []
for cat in frota:
    lista_completa.extend(frota[cat])
lista_completa = sorted(list(set(lista_completa)))

# --- 2. GESTÃO NA BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações da Frota")
with st.sidebar.expander("➕ Adicionar / ✏️ Editar / ❌ Excluir"):
    modo = st.radio("Ação", ["Adicionar", "Editar", "Excluir"])
    
    if modo == "Adicionar":
        novo = st.text_input("Novo Equipamento")
        if st.button("Salvar Novo"):
            if "GERAL" not in frota: frota["GERAL"] = []
            frota["GERAL"].append(novo)
            salvar_frota(frota)
            st.rerun()
            
    elif modo == "Editar":
        item_ed = st.selectbox("Selecionar", lista_completa)
        novo_ed = st.text_input("Corrigir para", value=item_ed)
        if st.button("Atualizar"):
            for c in frota:
                if item_ed in frota[c]:
                    idx = frota[c].index(item_ed)
                    frota[c][idx] = novo_ed
            salvar_frota(frota)
            st.rerun()

    elif modo == "Excluir":
        item_ex = st.selectbox("Remover", lista_completa)
        if st.button("Confirmar Exclusão"):
            for c in frota:
                if item_ex in frota[c]: frota[c].remove(item_ex)
            salvar_frota(frota)
            st.rerun()

# --- 3. INTERFACE DE CABEÇALHO ---
st.title("📝 Relatório de Escala e Disponibilidade")

col1, col2, col3 = st.columns(3)
with col1:
    saudacao = st.selectbox("Saudação", ["Bom dia!!", "Boa tarde!!", "Boa noite!!"])
    letra = st.selectbox("Letra", ["A", "B", "C", "D"])
with col2:
    horario = st.selectbox("Turno", ["06:00 às 18:00", "18:00 às 06:00"])
with col3:
    data_manual = st.date_input("Data", datetime.now())

st.divider()

# --- 4. DISTRIBUIÇÃO DOS EQUIPAMENTOS POR JORNADA ---
def montar_bloco(titulo_bloco):
    st.subheader(titulo_bloco)
    selecionados = st.multiselect(f"Selecione os equipamentos para {titulo_bloco}", lista_completa, key=f"sel_{titulo_bloco}")
    
    resultados = []
    for item in selecionados:
        tag_limpa = item.replace("-", " ", 1)
        # Checkbox lateral para saber se está quebrado
        col_check, col_obs = st.columns([1, 3])
        with col_check:
            quebrado = st.checkbox(f"❌ {tag_limpa}", key=f"q_{titulo_bloco}_{item}")
        with col_obs:
            if quebrado:
                defeito = st.text_input(f"Defeito", key=f"d_{titulo_bloco}_{item}")
                resultados.append(f"❌ {tag_limpa} - {defeito if defeito else 'Manutenção'}")
            else:
                resultados.append(f"✅ {tag_limpa}")
    return resultados

bloco_24h = montar_bloco("(24 horas)")
st.divider()
bloco_12h = montar_bloco("(12 horas)")
st.divider()
bloco_adm = montar_bloco("(ADM)")

# --- 5. GERAÇÃO DO RELATÓRIO FINAL ---
if st.button("🚀 GERAR RELATÓRIO COMPLETO"):
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_nome = dias_semana[data_manual.weekday()]
    data_str = data_manual.strftime("%d de %B de %Y") # Mês em inglês por padrão no Python, podemos ajustar se quiseres
    
    texto = f"{saudacao}\nCom segurança.\n\n"
    texto += f"{dia_nome}, dia {data_manual.strftime('%d de janeiro de %Y')}\n\n" # Ajustado para Janeiro conforme o print
    texto += "Segue a relação de equipamentos utilizados:\n\n"
    texto += f"Letra: {letra}\nTurno: {horario}\n\n"
    
    if bloco_24h:
        texto += "(24 horas)\n" + "\n".join(bloco_24h) + "\n\n"
    if bloco_12h:
        texto += "(12 horas)\n" + "\n".join(bloco_12h) + "\n\n"
    if bloco_adm:
        texto += "(ADM)\n" + "\n".join(bloco_adm) + "\n\n"
    
    st.success("Relatório gerado!")
    st.code(texto, language="text")