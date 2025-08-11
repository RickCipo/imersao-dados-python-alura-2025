import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon=":📊",
    layout="wide",
)

#Carregar o conteudo das aulas do Colab

df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Barra Lateral de Filtros
st.sidebar.header("Filtros")

#Filtro do Ano

anos_disponiveis = sorted(df["ano"].unique())
ano_selecionado = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

#Filtro de Senioridade

senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridade_selecionada = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)


#Filtro de Tipo de Contratação

contratos_disponiveis = sorted(df["contrato"].unique())
contratos_selecionada = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

#Filtro de Tamanho da Empresa
tamanhos_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanho_selecionado = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)


#----Filtragem do DataFrame----

df_filtrado = df[
    (df["ano"].isin(ano_selecionado)) &
    (df["senioridade"].isin(senioridade_selecionada)) &
    (df["contrato"].isin(contratos_selecionada)) &
    (df["tamanho_empresa"].isin(tamanho_selecionado))
]

#----Conteudo Principal----

st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos ultimos anos")


#----Métricas Principais (KPI's)----

st.subheader("Métricas gerais(Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0,

col1,col2,col3,col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f'{total_registros:,}')  
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

#----Gráficos com Pyplot----

st.subheader("Gráficos")

col1_graf1, col2_graf2 = st.columns(2)

with col1_graf1:
    if not df_filtrado.empty:
        top_cargos= df_filtrado.groupby('cargo') ['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation = "h",
            title="Top 10 Cargos com Maior Salário Médio",
            labels={"usd": "Média salarial(USD)", "cargo": ""},
        )

        grafico_cargos.update_layout( title_x=0.1, yaxis = {'categoryorder': "total ascending"})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de cargos.")


with col2_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x="usd",
            nbins=30,
            title="Distribuição de Salários Anuais",
            labels={"usd": "Faixa Salarial (USD)", 'count':''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)

    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de distribuição de salários.")

#----Gráfico de Dispersão----

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_traalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_traalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole = 0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:       
        st.warning("Nenhum dado para exibir no gráfico d dos tipos de trabalho.")


with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_pais = px.choropleth(media_ds_pais,
            locations = 'residencia_iso3',
            color = 'usd',
            color_continuous_scale='rdylgn',
            title = 'Salário Médio de Cientista de Dados por país',
            labels = {'usd':'Saláio médio(USD)','residencia_iso3': 'País'})
        grafico_pais.update_layout(title_x=0.1)
        st.plotly_chart(grafico_pais, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir o gráfico de salários por país.")


#---Tabela de Dados Detalhados---

st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)