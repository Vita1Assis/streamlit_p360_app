import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard P360", layout="wide")

# Verifica se os itens foram carregados na sessão
items = st.session_state.get("items", [])

if not items:
    st.warning("Nenhum item carregado. Volte à página principal e faça login.")
    st.stop()

df = pd.DataFrame(items)
df["preco"] = (
    df["preco"]
    .astype(str)
    .str.replace(",", ".")
    .astype(float)
)

st.title("Dashboard de Produtos")
# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Produtos", len(df))
c2.metric("Segmentos", df["segmento"].nunique())
c3.metric("Preço Médio", f"R$ {df['preco'].mean():,.2f}")

st.divider()

# Gráficos
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    df["segmento"].value_counts().plot(kind="bar", ax=ax1)
    ax1.set_title("Produtos por Segmento", fontsize=12)
    ax1.set_xlabel("")
    ax1.set_ylabel("Qtd")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    df.groupby("segmento")["preco"].mean().sort_values().plot(kind="barh", ax=ax2)
    ax2.set_title("Preço Médio por Segmento", fontsize=12)
    ax2.set_xlabel("R$")
    ax2.set_ylabel("")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)

st.divider()

col1, col2 = st.columns(2)

with col2:
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(df["preco"], bins=20)
    ax.set_title("Distribuição de Preços", fontsize=12)
    ax.set_xlabel("Preço")
    ax.set_ylabel("Qtd")
    plt.tight_layout()
    st.pyplot(fig)

with col1:
    fig3, ax3 = plt.subplots(figsize=(5, 3))
    df["brand"].value_counts().plot(kind="bar", ax=ax3)
    ax3.set_title("Produtos por Marca", fontsize=12)
    ax3.set_xlabel("")
    ax3.set_ylabel("Qtd")
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)



