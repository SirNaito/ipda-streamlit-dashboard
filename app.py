import streamlit as st
import pandas as pd
import plotly.express as px

# Config da Página
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Análise Salarial na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# Carregamento dos Dados pro DataFrame do Dashboard - Usando Pandas
df = pd.read_csv("https://raw.githubusercontent.com/SirNaito/ipda-streamlit-dashboard/refs/heads/main/dados-imersao-final.csv")

# Header da Barra Lateral (Filtros)
st.sidebar.header("🔍📊 Filtros")

# Filtro de Ano Fiscal
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("👔 Ano Fiscal", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("💻 Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("🕗 Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtragem por Alocação
alocacoes_disponiveis = sorted(df['remoto'].unique())
alocacoes_selecionadas = st.sidebar.multiselect("📍 Regime de alocação", alocacoes_disponiveis, default=alocacoes_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("🏢 Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# Filtro por Moeda
moedas_disponiveis = sorted(df['moeda'].unique())
moedas_selecionadas = st.sidebar.multiselect("💵 Moeda", moedas_disponiveis, default=moedas_disponiveis)

# Filtro por País
paises_disponiveis = list(df['residencia_iso3'].unique())
paises_selecionados = st.sidebar.multiselect("🌎 Localidade", paises_disponiveis, default=paises_disponiveis)

# Filtragem do DataFrame 
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['remoto'].isin(alocacoes_selecionadas)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados)) &
    (df['moeda'].isin(moedas_selecionadas)) &
    (df['residencia_iso3'].isin(paises_selecionados))
]

# Painel Principal
st.title("📊 Análise Salarial na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# Métricas Principais (KPIs)
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
    tipo_contrato_frequente = df_filtrado["contrato"].mode()[0]
    alocaçao_mais_frequente = df_filtrado["remoto"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum, contrato_mais_comum, alocacao_comum = 0, 0, 0, "", "", "", ""

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Regime contratual mais frequente", tipo_contrato_frequente)
col5.metric("Alocação mais frequente", alocaçao_mais_frequente)
col6.metric("Cargo mais frequente", cargo_mais_frequente)

# Divisão entre as métricas e os gráficos
st.markdown("---")

# Quebra de div para os gráficos interativos com Plotly 
st.subheader("Gráficos")

# Define 2 colunas para os gráficos
col_graf1, col_graf2 = st.columns(2)

# Gráfico de Barras - Top 10 Cargos por Salário Médio
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            color='usd',
            color_continuous_scale='Viridis',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True, theme="streamlit")
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

# Gráfico de Distribuição - Histograma de Salários Anuais
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''},
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True, theme="streamlit")
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

# Definição dos Graficos 3 e 4 (Graficos das segunda linhas ainda dentro das duas colunas)
col_graf3, col_graf4 = st.columns(2)

# Gráfico de Pizza - Proporção dos Tipos de Trabalho
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            color = 'tipo_trabalho',
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title='Proporção do regime de alocação',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True, theme="streamlit")
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

# Gráfico de Mapa - Salário Médio de Data Scientists por País
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Viridis',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True, theme="streamlit")
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# Divisão entre os Gráficos e os DataFrame
st.markdown("---")

# Exibição do dados exibidos pelo DataFrame
st.subheader("Detalhamentos dos Dados")
st.dataframe(df_filtrado)