import streamlit as st
import requests
import pandas as pd
from PIL import Image, ImageDraw
from io import BytesIO
import os

# Importa o mapeamento de marcas e a lista de segmentos
from brand_segment_map import BRAND_SEGMENT_MAP, SEGMENTS, BRANDS

# -----------------------------
# CONFIGURAÇÃO STREAMLIT
# -----------------------------
st.set_page_config(page_title="Catálogo P360", layout="wide")
st.title("Catálogo de Produtos - Product 360 (Informatica MDM Cloud)")

# -----------------------------
# INPUTS DE LOGIN
# -----------------------------
# Sidebar

if not st.session_state.get("logged_in", False):
    st.sidebar.header("Login Informatica Cloud")
    username = st.sidebar.text_input("Usuário", value="", type="default")
    password = st.sidebar.text_input("Senha", value="", type="password")
    load_button = st.sidebar.button("Carregar Produtos")
else:
    st.sidebar.header('Informatica Product 360')
    st.sidebar.text(f"Você está na org: Triade LLC")
    st.sidebar.text(f"no usuário: {st.session_state.get('username')}")             
    username = password = load_button = None

# -----------------------------
# FUNÇÃO PARA LOGIN E PEGAR SESSION ID
# -----------------------------
def get_session_id(username, password):
    url = "https://dmp-us.informaticacloud.com/saas/public/core/v3/login"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.2"
    }
    resp = requests.post(url, json=payload,headers=headers)
    

    if resp.status_code != 200:
        raise Exception(f"Erro ao autenticar: {resp.text}")

    data = resp.json()
    session_id = data["userInfo"]["sessionId"]
    org_name = data["userInfo"]["orgName"]
    return session_id, org_name


# -----------------------------
# FUNÇÃO PARA CHAMAR O PRODUCT 360
# -----------------------------
def get_p360_items(session_id):
    url = "https://usw1-mdm.dmp-us.informaticacloud.com/search/public/api/v1/search"

    payload = {
        "entityType": "p360.item",
        "pageSize": 200,
        "recordsToReturn": 1000,
        "recordOffset": 0,
        "search": "*",
        "filters": {
            "filter": [
                {
                "comparator": "GREATER_THAN",
                "fieldName": "p360item.sellingPrice.sellingPriceAmount",
                "fieldValue": "0"
                }
            ]
        }
    }

    headers = {
        "IDS-SESSION-ID": session_id,
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.32.2"
    }

    resp = requests.post(url, json=payload, headers=headers)
    try:
        return resp.json()
    except Exception as e:
        st.error("Erro ao converter para JSON")
        st.code(resp.text)
        raise e

def normalize_items(api_data):
    records = api_data.get("searchResult", {}).get("records", [])
    items = []

    for r in records:
        # Nome do item
        nome = r.get("p360item.X_item_name", "")
        image = r.get("p360item.X_imageUrl", "")
        brand = r.get("p360item.brand", "")
        
        # --- INÍCIO DA MODIFICAÇÃO: Adiciona o Segmento ---
        # Busca o segmento no mapeamento. Se não encontrar, usa "Outros"
        segmento = BRAND_SEGMENT_MAP.get(brand, "Outros")
        # --- FIM DA MODIFICAÇÃO ---
        
        # Descrição — pode vir shortDescription ou longDescription
        descr = ""
        desc_list = r.get("p360item.description", [])
        if desc_list:
            descr = (
                desc_list[0].get("shortDescription") 
                or desc_list[0].get("longDescription") 
                or ""
            )
        # Preço — pego o primeiro preço
        preco = ""
        preco_list = r.get("p360item.sellingPrice", [])
        if preco_list:
            preco = preco_list[0].get("sellingPriceAmount", "")
        
        attributes_list = r.get("p360item.X_attributes", []) or []
        attribute_names = []
        attribute_values = []
        if attributes_list:
            for i in attributes_list:
                attribute_names.append(i.get("X_name"))
                attribute_values.append(i.get("X_value"))
        df = pd.DataFrame({
            "Atributo": attribute_names,
            "Valor": attribute_values
        })

        items.append({
            "nome": nome,
            "descricao": descr,
            "brand": brand,
            "segmento": segmento, # Adiciona o segmento ao item
            "preco": preco,
            "image":image,
            "attributes_df": df
        }
        )

    return items


# ============================
# ESTADO PARA PAGINAÇÃO
# ============================
if "page" not in st.session_state:
    st.session_state.page = 1

ITEMS_PER_PAGE = 50

# -----------------------------
# INTERFACE DE BUSCA E FILTRO
# -----------------------------

# Cria a barra lateral para o filtro de segmento
st.sidebar.header("Segmento")
selected_segment = st.sidebar.radio(
    "Selecione o Segmento",
    SEGMENTS,
    index=0 # "Tudo" é o primeiro elemento
)
st.sidebar.header("Marca")
selected_brand = st.sidebar.radio(
    "Selecione a Marca",
    BRANDS,
    index=0
)

search_query = st.text_input("Pesquisar por nome", value="")

def apply_filters(items, query, segment, brand):
    # 1. Filtro por busca (nome)
    if query:
        query = query.lower()
        items = [item for item in items if query in item["nome"].lower()]
        
    # 2. Filtro por segmento
    if segment != "Tudo":
        items = [item for item in items if item.get("segmento") == segment]
    
    # 3. Filtro por marca
    if brand != "Tudo":
        items = [item for item in items if item.get("brand") == brand]
        
    return items

# -----------------------------
# BOTÃO LOAD
# -----------------------------

if load_button:
    if not username or not password:
        st.error("Insira usuário e senha.")
    else:
        with st.spinner("Autenticando..."):
            try:
                # login
                session_id, org_name = get_session_id(username, password)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.org_name = org_name


                # pega produtos
                data = get_p360_items(session_id)
                items = normalize_items(data)

                # salva produtos
                st.session_state.items = items
                st.session_state.page = 1

            except Exception as e:
                st.error(str(e))

# -----------------------------
# EXIBIÇÃO DOS DADOS
# -----------------------------
items = st.session_state.get("items", [])

if items:
    # A coleta de marcas não é mais necessária aqui, pois o filtro de segmento está sendo usado
    # brand_list = []
    # for b in items:
    #     brand_list.append(b.get("brand"))
    # brand_list = sorted(list(set([b for b in brand_list if b]))) 
    
    # --- MODIFICAÇÃO: Aplica os filtros de busca e segmento ---
    filtered_items = apply_filters(items, search_query, selected_segment, selected_brand)
    # --- FIM DA MODIFICAÇÃO ---
    
    total_items = len(filtered_items)
    total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    # Corrigir página fora do limite
    if st.session_state.page > total_pages:
        st.session_state.page = total_pages

    # Índice dos itens
    start = (st.session_state.page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = filtered_items[start:end]

    st.subheader(f"Página {st.session_state.page} de {total_pages}")
    st.write(f"Mostrando {len(page_items)} de {total_items} itens encontrados")
    # st.write(brand_list) # Remove a exibição da lista de marcas

    cols = st.columns(2)

    for i, item in enumerate(page_items):
        with cols[i % 2]:
            st.markdown(f"### {item['nome']}")
            st.markdown(f"**Segmento:** {item['segmento']}") # Exibe o segmento
            url=item['image']
            TARGET_SIZE = (350, 350) 
            if url:
                try:
                    # Pega a imagem da URL
                    response = requests.get(url)
                    img = Image.open(BytesIO(response.content))
                    # Reduz o tamanho em 40%
                    new_width = int(img.width * 0.6)
                    new_height = int(img.height * 0.6)
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

            st.write(item["descricao"])
            st.write(item["brand"])
            
            st.write(f"**Preço:** R$ {item['preco']}")
            html = item["attributes_df"].to_html(
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

    # -----------------------------
    # CONTROLES DE PAGINAÇÃO
    # -----------------------------
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅ Página anterior", disabled=(st.session_state.page == 1)):
            st.session_state.page -= 1

    with col3:
        if st.button("Próxima página ➡", disabled=(st.session_state.page == total_pages)):
            st.session_state.page += 1
