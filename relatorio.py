import streamlit as st
import json
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Turno", layout="wide")

# --- 1. SISTEMA DE BANCO DE DADOS ---
ARQUIVO_DADOS = 'frota.json'

FROTA_PADRAO = {
    "CARREGADEIRA": [
        "CSP-078 - CAT 938G II", "CSP-090 - CAT 938K", "CSP-091 - CAT 938K",
        "CSP-093 - CAT 924K", "CSP-094 - CAT 938K", "CSP-096 - CAT 938K",
        "CSP-097 - CAT 938K", "CSP-098 - CAT 924K", "CSP-100 - CAT 950L",
        "CSP-104 - CAT 938K", "CSP-106 - CAT 924K", "CSP-107 - CAT 924K"
    ],
    "ESCAVADEIRA": [
        "ESE-019 - CAT 320 C", "ESE-023 - CAT 320 C", "ESE-031 - CAT 312 C",
        "ESE-036 - HYUNDAI R260LC", "ESE-039 - HYUNDAI R220LC-9S", "ESE-047 - CAT 320LBR",
        "ESE-048 - CAT 320GX", "ESE-049 - CAT 320LBR", "ESE-050 - CAT 320LBR",
        "ESE-053 - CAT 320GC", "ESE-055 - CAT 320GC", "LOC-3456 - HYUNDAI R220LC-9S",
        "LOC-7726 - HYUNDAI R220LC-9S"
    ],
    "CAMINHÃO": [
        "CAM-185 - FORD 2626", "CAM-250 - MB L-1620/51", "CAM-267 - MB 1718/48",
        "CAM-279 - VW 24.260", "CAM-306 - VW 26.260"
    ],
    "MOTONIVELADORA": ["MON-021 - CAT 12H II", "MON-022 - CAT 12H II"],
    "RETRO ESCAVADEIRA": [
        "RTE-029 - CAT 416E", "RTE-030 - CAT 416E", "RTE-034 - CAT 416F", "RTE-035 - CAT 416F"
    ],
    "TRATOR DE ESTEIRA": [
        "TSE-019 - CAT D6D", "TSE-036 - CAT D6M", "TSE-037 - CAT D6M",
        "TSE-046 - CAT D5", "TSE-052 - CAT D4"
    ],
    "MINI CARREGADEIRA / ESCAVADEIRA": ["MCP-007 - CAT 226B3", "MEE-007 - CAT 305.5"],
    "PLANTAS": [
        "ALV-001 - BRITADOR SXBM 6240", "CMB-002 - BRITADOR CÔNICO SYMONS",
        "CMP-001 - PENEIRA AZUL", "USC-001 - USINA DE REVSOL CINZA"
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

# --- 2. BARRA LATERAL ---
st.sidebar.header("⚙️ Gerenciar Frota")
with st.sidebar.expander("➕ Adicionar Novo"):
    cat_add = st.selectbox("Categoria", list(frota.keys()))
    novo_nome = st.text_input("Nome/Tag")
    if st.button("Salvar Novo"):
        if novo_nome:
            frota[cat_add].append(novo_nome)
            salvar_frota(frota)
            st.rerun()

with st.sidebar.expander("❌ Remover Equipamento"):
    cat_rem = st.selectbox("Categoria Rem.", list(frota.keys()))
    item_rem = st.selectbox("Equipamento Rem.", frota[cat_rem])
    if st.button("Remover"):
        frota[cat_rem].remove(item_rem)
        salvar_frota(frota)
        st.rerun()

# --- 3. ÁREA PRINCIPAL ---
st.title("🚜 Controle de Turno")
st.info("Marque o quadrado para incluir no relatório. Se tiver defeito, escreva no campo de texto.")

# Dicionário para guardar as linhas do relatório final, separadas por categoria
relatorio_por_categoria = {}

# Loop pelas categorias
for categoria, lista_equipamentos in frota.items():
    with st.expander(f"📂 {categoria}", expanded=True):
        linhas_desta_categoria = []
        
        for item in lista_equipamentos:
            # Checkbox para selecionar (Diz se vai pro relatório ou não)
            selecionado = st.checkbox(f"{item}", key=item)
            
            if selecionado:
                # Se selecionado, mostra campo de observação
                obs = st.text_input(f"📝 Observação para {item} (Deixe vazio se estiver OK)", key=f"obs_{item}")
                
                if obs:
                    # Tem texto = Tem defeito (❌)
                    linhas_desta_categoria.append(f"❌ {item} - {obs}")
                else:
                    # Sem texto = Está Disponível (✅)
                    linhas_desta_categoria.append(f"✅ {item}")
        
        # Guarda o resultado desta categoria se houver algum item selecionado
        if linhas_desta_categoria:
            relatorio_por_categoria[categoria] = linhas_desta_categoria

st.write("---")

# --- 4. GERAÇÃO DO RELATÓRIO ---
if st.button("GERAR RELATÓRIO PARA E-MAIL"):
    if not relatorio_por_categoria:
        st.warning("Nenhum equipamento foi selecionado!")
    else:
        st.success("Relatório gerado! Copie abaixo:")
        
        # Monta o texto final
        texto_final = "RELATÓRIO DE PASSAGEM DE TURNO\n"
        texto_final += "================================\n"
        
        for cat, linhas in relatorio_por_categoria.items():
            texto_final += f"\n>> {cat}\n"
            texto_final += "\n".join(linhas)
            texto_final += "\n"
            
        texto_final += "\n================================"
        
        st.text_area("Copie aqui:", value=texto_final, height=500)