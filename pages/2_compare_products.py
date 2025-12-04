import streamlit as st
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Catálogo P360", layout="wide")

# Verifica se os itens foram carregados na sessão
items = st.session_state.get("items", [])

session = st.session_state['session']

if not items:
    st.warning("Nenhum item carregado. Volte à página principal e faça login.")
    st.stop()

# Limpa os nomes (remove nulos e vazios)
item_names = [
    item["nome"].strip()
    for item in items
    if item["nome"] and item["nome"].strip()
]
segmento_escolhido = 'Smartphones'
items_filtrados = [
    item for item in items
    if item['segmento'] == segmento_escolhido
]
# Inicializa quantidade de itens selecionáveis
if "compare_count" not in st.session_state:
    st.session_state.compare_count = 2  # começa com 2 itens

# -----------------------------
# Botões para adicionar / remover
# -----------------------------
colAdd, colRemove = st.columns([1, 1])

with colAdd:
    if st.button("➕ Adicionar item"):
        if st.session_state.compare_count < 4:
            st.session_state.compare_count += 1

with colRemove:
    if st.button("➖ Remover item"):
        if st.session_state.compare_count > 2:
            st.session_state.compare_count -= 1

selected_items = []

st.subheader("Selecione os itens:")

for i in range(st.session_state.compare_count):
    item_name = st.selectbox(
        f"Item {i+1}",
        [""] + item_names,
        key=f"compare_select_{i}"
    )
    selected_items.append(item_name)

if st.button("Comparar"):
    valid_items = [name for name in selected_items if name]

    if len(valid_items) < 2:
        st.error("Selecione pelo menos 2 itens.")
        st.stop()

    selected_objects = [
        next((i for i in items if i["nome"] == name), None)
        for name in valid_items
    ]

    cols = st.columns(len(selected_objects))
    TARGET_SIZE = (350, 350)

    for idx, (col, obj) in enumerate(zip(cols, selected_objects)):
        with col:
            try:
                response = session.get(obj["image"])
                img = Image.open(BytesIO(response.content)).resize(TARGET_SIZE)
            except:
                img = Image.new("RGB", TARGET_SIZE, color=(200, 200, 200))
            st.image(img, caption=obj["nome"], use_container_width=False)
    st.subheader("Informações Gerais")

    df_comp = pd.DataFrame({
        "Atributo": ["Nome", "Marca", "Segmento", "Preço"]
    })

    for obj in selected_objects:
        df_comp[obj["nome"]] = [
            obj["nome"],
            obj["brand"],
            obj["segmento"],
            obj["preco"],
        ]

    # Renderiza HTML
    html = df_comp.to_html(
        index=False,
        header=False,
        border=0,
        classes="comparison-table"
    )

    st.markdown(
        """
        <style>
            .comparison-table {
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                font-size: 15px;
            }
            .comparison-table tr:nth-child(odd) {
                background-color: #323542;
            }
            .comparison-table tr:nth-child(even) {
                background-color: #323542;
            }
            .comparison-table td {
                padding: 8px 10px;
                border-bottom: 1px solid #e0e0e0;
            }
            .comparison-table td:first-child {
                font-weight: bold;
                background-color: #323542;
                width: 25%;
            }
            .comparison-table th {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(html, unsafe_allow_html=True)
    st.divider()
    st.subheader("Atributos Internos")

    # base para merge
    df_merge = None
    for obj in selected_objects:
        df_attr = obj["attributes_df"].rename(columns={"Valor": obj["nome"]})
        df_attr[obj["nome"]] = df_attr[obj["nome"]].fillna("-")
        df_attr[obj["nome"]] = df_attr[obj["nome"]].replace("", "-", regex=False)
        if df_merge is None:
            df_merge = df_attr
        else:
            df_merge = pd.merge(df_merge, df_attr, on="Atributo", how="outer")
    if df_merge is not None:
        df_merge = df_merge.fillna("-")
    if df_merge is not None:
        df_merge = df_merge.replace("", "-", regex=False)

    html = df_merge.to_html(
        index=False,
        header=False,
        border=0,
        classes="comparison-attributes"
    )

    st.markdown(
        """
        <style>
            .comparison-attributes {
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                font-size: 15px;
            }
            .comparison-attributes tr:nth-child(odd) {
                background-color: #323542;
            }
            .comparison-attributes tr:nth-child(even) {
                background-color: #323542;
            }
            .comparison-attributes td {
                padding: 6px 8px;
                border-bottom: 1px solid #ddd;
            }
            .comparison-attributes td:first-child {
                font-weight: bold;
                background-color: #323542;
                width: 25%;
            }
            .comparison-attributes th {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(html, unsafe_allow_html=True)
    st.divider()

    st.title("Produtos relacionados:")

    cols = st.columns(4)
    for i, item in enumerate(items_filtrados):
        with cols[i % 4]:
            st.text(f"{item['nome']}")
            st.text(f"Segmento: {item['segmento']}") # Exibe o segmento
            url=item['image']
            TARGET_SIZE = (350, 350) 
            if url:
                try:
                    # Pega a imagem da URL
                    response = session.get(url, stream=True)
                    #response = requests.get(url)
                    img = Image.open(BytesIO(response.content))
                    img = img.resize(TARGET_SIZE)
                    st.image(img, caption="Imagem do Produto", use_container_width =False)
                except:
                    # Se a URL estiver quebrada, cria placeholder
                    img = Image.new("RGB", TARGET_SIZE, color=(200, 200, 200))
                    st.image(img, caption="Sem Imagem", use_container_width=False)
            else:
                # Placeholder cinza
                img = Image.new("RGB", TARGET_SIZE, color=(200, 200, 200))
                st.image(img, caption="Sem Imagem", use_container_width=False)         
            st.write(f"**Preço:** R$ {item['preco']}")
            st.divider()