import streamlit as st
import requests
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import os


st.set_page_config(page_title="Catálogo P360", layout="wide")
st.title("Comparação de Produtos")
# Verifica se os itens foram carregados na sessão
items = st.session_state.get("items", [])

if not items:
    st.warning("Nenhum item carregado. Volte à página principal e faça login.")
    st.stop()

# Criar lista de nomes para o selectbox
#item_names = [item["nome"] for item in items]
item_names = [item["nome"] for item in items if item["nome"]]

col1, col2 = st.columns(2)

with col1:
    item1_name = st.selectbox("Selecione o 1º produto", [""] + item_names)
with col2:
    item2_name = st.selectbox("Selecione o 2º produto", [""] + item_names)

# Obter os itens selecionados
item1 = next((i for i in items if i["nome"] == item1_name), None)
item2 = next((i for i in items if i["nome"] == item2_name), None)
TARGET_SIZE = (350, 350)

# Apenas mostra o botão se ambos forem escolhidos
if item1 and item2:
    if st.button("Comparar"):
        
        #st.subheader(f"**{item1['nome']}** VS **{item2['nome']}**")
        try:
            # Pega a imagem da URL
            response1 = requests.get(item1['image'])
            img1 = Image.open(BytesIO(response1.content))
            img1 = img1.resize(TARGET_SIZE)
            with col1:
                st.image(img1, caption="Imagem do Produto", use_container_width =False)
                st.subheader(f"{item1['nome']}")
            response2 = requests.get(item2['image'])
            img2 = Image.open(BytesIO(response2.content))
            img2 = img2.resize(TARGET_SIZE)
            with col2:
                st.image(img2, caption="Imagem do Produto", use_container_width =False)
                st.subheader(f"{item2['nome']}")
        except:
            # Se a URL estiver quebrada, cria placeholder
            img = Image.new("RGB", TARGET_SIZE, color=(200, 200, 200))
            st.image(img, caption="Sem Imagem", use_container_width=False)
        
        # Tabela comparativa simples
        df_comp = pd.DataFrame({
            "Atributo": ["Nome", "Marca", "Segmento", "Preço"],
            item1["nome"]: [item1["nome"], item1["brand"], item1["segmento"], item1["preco"]],
            item2["nome"]: [item2["nome"], item2["brand"], item2["segmento"], item2["preco"]],
        })

        #st.table(df_comp)
        html = df_comp.to_html(
        index=False,
        header=False,
        border=0,
        classes="p360-table"
        )

        st.markdown(
                """
                <style>
                    .p360-table {
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 14px;
                    }
                    .p360-table td {
                        padding: 4px 6px;
                        border: none !important;
                    }
                    .p360-table th {
                        display: none; /* garante que headers sumam */
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
        st.markdown(html, unsafe_allow_html=True)
        st.divider()

        # Comparação das tabelas de atributos internas
        st.subheader("**Atributos:**")

        # Mescla atributos dos dois itens
        df1 = item1["attributes_df"].rename(columns={"Valor": item1["nome"]})
        df2 = item2["attributes_df"].rename(columns={"Valor": item2["nome"]})

        # Mescla pela coluna "Atributo"
        df_merge = pd.merge(df1, df2, on="Atributo", how="outer")

        #st.dataframe(df_merge)
        html = df_merge.to_html(
        index=False,
        header=False,
        border=0,
        classes="p360-table"
        )

        st.markdown(
                """
                <style>
                    .p360-table {
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 16px;
                        background-color: #323542;
                    }
                    .p360-table td {
                        padding: 4px 6px;
                        border: 1px !important;
                    }
                    .p360-table th {
                        display: none; /* garante que headers sumam */
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
        st.markdown(html, unsafe_allow_html=True)
        st.divider()
