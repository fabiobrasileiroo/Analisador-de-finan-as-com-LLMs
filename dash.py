import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Carregar dados
df = pd.read_csv("finances.csv")
df_original = df.copy()  # Mantém uma cópia do DataFrame original para cálculo de totais

# Preprocessamento para exibir os valores como "1" na tabela e gráfico de pizza
del df["ID"]
df["Mês"] = df["Data"].apply(lambda x: "-".join(x.split("-")[:-1]))
df["Data"] = pd.to_datetime(df["Data"])
df["Data"] = df["Data"].apply(lambda x: x.date())
df = df[df["Categoria"] != "Receitas"]
df["Valor"] = 1  # Define o valor como "1" para a exibição na tabela e no gráfico

# Processamento do DataFrame original para cálculos de totais
del df_original["ID"]
df_original["Mês"] = df_original["Data"].apply(lambda x: "-".join(x.split("-")[:-1]))
df_original["Data"] = pd.to_datetime(df_original["Data"])
df_original["Data"] = df_original["Data"].apply(lambda x: x.date())
df_original = df_original[df_original["Categoria"] != "Receitas"]

# Função para filtrar os dados com base nos meses e categorias selecionadas
def filter_data(df, selected_months, selected_categories):
    if selected_months:
        df_filtered = df[df['Mês'].isin(selected_months)]
    else:
        df_filtered = df
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(selected_categories)]
    return df_filtered

# Título do Dashboard
st.title("Dashboard de Finanças Pessoais")

# Filtros de data
st.sidebar.header("Filtros")

# Permitir seleção de múltiplos meses
meses = st.sidebar.multiselect("Mês", df["Mês"].unique(), default=df["Mês"].unique())

# Filtro de categoria
categories = df["Categoria"].unique().tolist()
selected_categories = st.sidebar.multiselect("Filtrar por Categorias", categories, default=categories)

# Filtrando os dados
df_filtered = filter_data(df, meses, selected_categories)
df_original_filtered = filter_data(df_original, meses, selected_categories)  # Filtrando para o cálculo de totais

# ====================
# Exibir a Tabela Filtrada e o Gráfico

# Layout de colunas
c1, c2 = st.columns([0.6, 0.4])

# Exibir a tabela de dados filtrados com "Valor" como "1"
c1.subheader("Tabela de Finanças Filtradas")
c1.dataframe(df_filtered)

# Exibir a distribuição das categorias em um gráfico de pizza com "Valor" como "1"
c2.subheader("Distribuição de Categorias")
category_distribution = df_filtered.groupby("Categoria")["Valor"].sum().reset_index()
fig = px.pie(
    category_distribution, 
    values='Valor', 
    names='Categoria', 
    title='Distribuição por Categoria',
    hole=0.3
)
fig.update_traces(textinfo='percent+label')  # Exibir porcentagens e rótulos
c2.plotly_chart(fig, use_container_width=True)

# Exibir tabela com o total gasto real por categoria usando os valores do CSV original
st.subheader("Total Gasto por Categoria")
total_por_categoria = df_original_filtered.groupby("Categoria")["Valor"].sum().reset_index()
total_por_categoria.columns = ["Categoria", "Total Gasto"]

# Format the "Total Gasto" column with "R$" and two decimal places
total_por_categoria["Total Gasto"] = total_por_categoria["Total Gasto"].apply(lambda x: f"R$ {x:,.2f}")

# Display the formatted table
st.table(total_por_categoria)


# ====================
# Cálculo de Entradas, Saídas e Diferença

# Filtrar valores de entrada e saída
total_entradas = df_original_filtered[df_original_filtered["Valor"] > 0]["Valor"].sum()
total_saidas = df_original_filtered[df_original_filtered["Valor"] < 0]["Valor"].sum()
diferenca = total_entradas + total_saidas  # Diferença entre entradas e saídas

# Exibir os resultados formatados com duas casas decimais
st.subheader("Resumo de Entradas e Saídas")
st.metric("Total Entradas", f"R$ {total_entradas:,.2f}")
st.metric("Total Saídas", f"R$ {total_saidas:,.2f}")
st.metric("Diferença", f"R$ {diferenca:,.2f}")
