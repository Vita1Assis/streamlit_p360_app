import streamlit as st
import pandas as pd

st.title("🔍 Comparação de Produtos")

# Verifica se os itens foram carregados na sessão
items = st.session_state.get("items", [])

if not items:
    st.warning("Nenhum item carregado. Volte à página principal e faça login.")
    st.stop()

# Criar lista de nomes para o selectbox
item_names = [item["nome"] for item in items]

col1, col2 = st.columns(2)

with col1:
    item1_name = st.selectbox("Selecione o 1º produto", [""] + item_names)
with col2:
    item2_name = st.selectbox("Selecione o 2º produto", [""] + item_names)

# Obter os itens selecionados
item1 = next((i for i in items if i["nome"] == item1_name), None)
item2 = next((i for i in items if i["nome"] == item2_name), None)

# Apenas mostra o botão se ambos forem escolhidos
if item1 and item2:
    if st.button("Comparar"):
        
        st.subheader(f"Comparando: **{item1['nome']}** VS **{item2['nome']}**")
        
        # Tabela comparativa simples
        df_comp = pd.DataFrame({
            "Atributo": ["Nome", "Marca", "Segmento", "Preço"],
            item1["nome"]: [item1["nome"], item1["brand"], item1["segmento"], item1["preco"]],
            item2["nome"]: [item2["nome"], item2["brand"], item2["segmento"], item2["preco"]],
        })

        st.table(df_comp)

        # Comparação das tabelas de atributos internas
        st.subheader("Atributos Internos")

        # Mescla atributos dos dois itens
        df1 = item1["attributes_df"].rename(columns={"Valor": item1["nome"]})
        df2 = item2["attributes_df"].rename(columns={"Valor": item2["nome"]})

        # Mescla pela coluna "Atributo"
        df_merge = pd.merge(df1, df2, on="Atributo", how="outer")

        st.dataframe(df_merge)
