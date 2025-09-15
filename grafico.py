import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import unicodedata
import re

# Configura tema do Plotly para fundo branco e fonte maior
pio.templates.default = "plotly_white"

# Carrega as planilhas
df_mercado = pd.read_excel('Participacao_Mercado.xlsx')
df_meio = pd.read_excel('Meio_Acesso.xlsx')

# Unifica nomes e coloca tudo em maiúsculo
df_mercado[df_mercado.columns[0]] = df_mercado[df_mercado.columns[0]].str.upper()
df_meio[df_meio.columns[0]] = df_meio[df_meio.columns[0]].str.upper()

# Corrige nomes específicos para unificar em "N-MULTIFIBRA"
df_mercado[df_mercado.columns[0]] = df_mercado[df_mercado.columns[0]].replace({
    'N-MULTIMIDIA TELECOMUNICACOES LTDA': 'N-MULTIFIBRA',
    'NMULTIFIBRA TELECOMUNICACAO LTDA': 'N-MULTIFIBRA',
    'NMULTIFIBRA': 'N-MULTIFIBRA'
})

# Agrupa acessos por provedora
df_grouped = df_mercado.groupby(df_mercado.columns[0], as_index=False)[df_mercado.columns[1]].sum()
df_grouped = df_grouped.sort_values(df_grouped.columns[1], ascending=False)

# Total de acessos
total_acessos = df_grouped[df_grouped.columns[1]].sum()

st.set_page_config(page_title="Dashboard Provedoras de Internet", layout="wide")
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Dashboard Provedoras de Internet</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sessão de métricas gerais
col1, col2 = st.columns([2, 8])
with col1:
    st.metric('Total de Acessos', f'{int(total_acessos):,}')
with col2:
    st.write("")

# Tabs para dividir o dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    '📊 Comparar Provedoras',
    '🏆 Ranking Horizontal',
    '🔎 Buscar Provedora',
    '🛠 Meios de Acesso'
])

with tab1:
    st.markdown("<h3 style='color: #34495e;'>Comparação entre Provedoras</h3>", unsafe_allow_html=True)
    provedoras = df_grouped[df_grouped.columns[0]].tolist()
    selecionadas = st.multiselect(
        'Selecione as provedoras para comparar:',
        provedoras,
        default=provedoras[:5]
    )
    df_selecionadas = df_grouped[df_grouped[df_grouped.columns[0]].isin(selecionadas)]
    fig = px.bar(
        df_selecionadas,
        x=df_selecionadas.columns[0],
        y=df_selecionadas.columns[1],
        text=df_selecionadas.columns[1],
        color=df_selecionadas.columns[0],
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={df_selecionadas.columns[0]: 'OPERADORA', df_selecionadas.columns[1]: 'ACESSOS'},
        hover_data={df_selecionadas.columns[0]: True, df_selecionadas.columns[1]: ':.0f'}
    )
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker_line_width=2,
        marker_line_color='black',
        hovertemplate='<b>%{x}</b><br>Acessos: %{y:,}<extra></extra>'
    )
    fig.update_layout(
        xaxis_title='Operadora',
        yaxis_title='Acessos',
        showlegend=False,
        margin=dict(t=80, r=40, b=40, l=40),
        font=dict(size=16),
        height=500,
        bargap=0.25,
    )
    fig.update_xaxes(tickangle=45, automargin=True)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("<h3 style='color: #34495e;'>Ranking Geral de Provedoras</h3>", unsafe_allow_html=True)
    fig2 = px.bar(
        df_grouped,
        x=df_grouped.columns[1],
        y=df_grouped.columns[0],
        orientation='h',
        text=df_grouped.columns[1],
        color=df_grouped.columns[0],
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={df_grouped.columns[0]: 'OPERADORA', df_grouped.columns[1]: 'ACESSOS'},
        hover_data={df_grouped.columns[0]: True, df_grouped.columns[1]: ':.0f'}
    )
    fig2.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker_line_width=2,
        marker_line_color='black',
        hovertemplate='<b>%{y}</b><br>Acessos: %{x:,}<extra></extra>'
    )
    fig2.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title='Acessos',
        yaxis_title='Operadora',
        showlegend=False,
        margin=dict(t=80, r=40, b=40, l=40),
        font=dict(size=16),
        height=max(600, 30 * len(df_grouped)),  # barras mais largas se houver muitas operadoras
        bargap=0.25,
    )
    st.plotly_chart(fig2, use_container_width=True)

def normaliza(texto):
    # Remove acentos, transforma em maiúsculo e tira caracteres especiais
    texto = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^A-Z0-9]', '', texto.upper())
    return texto

with tab3:
    st.markdown("<h3 style='color: #34495e;'>Buscar Provedora</h3>", unsafe_allow_html=True)
    busca = st.text_input('Digite o nome da provedora:')
    if busca:
        busca_norm = normaliza(busca)
        # Cria coluna temporária normalizada para busca
        df_grouped['__norm'] = df_grouped[df_grouped.columns[0]].apply(normaliza)
        resultado = df_grouped[df_grouped['__norm'].str.contains(busca_norm, na=False)]
        df_grouped.drop(columns='__norm', inplace=True)
        if not resultado.empty:
            st.success(f'Encontrado(s) {len(resultado)} resultado(s):')
            st.dataframe(resultado.drop(columns='__norm'), use_container_width=True)
            fig3 = px.bar(
                resultado,
                x=resultado.columns[0],
                y=resultado.columns[1],
                text=resultado.columns[1],
                color=resultado.columns[0],
                color_discrete_sequence=px.colors.qualitative.Bold,
                labels={resultado.columns[0]: 'OPERADORA', resultado.columns[1]: 'ACESSOS'},
            )
            fig3.update_traces(texttemplate='%{text:,}', textposition='outside', marker_line_width=2, marker_line_color='black')
            fig3.update_layout(
                font=dict(size=16),
                height=400,
                margin=dict(t=60, r=40, b=40, l=40),
                bargap=0.25,
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning('Provedora não encontrada.')

with tab4:
    st.markdown("<h3 style='color: #34495e;'>Meios de Acesso</h3>", unsafe_allow_html=True)
    st.write("Distribuição dos acessos por tipo de meio de acesso.")
    # Supondo que a primeira coluna é o nome do meio e a segunda é o total de acessos
    fig_pizza = px.pie(
        df_meio,
        names=df_meio.columns[0],
        values=df_meio.columns[1],
        color_discrete_sequence=px.colors.qualitative.Bold,
        hole=0.3,
        labels={df_meio.columns[0]: 'Meio de Acesso', df_meio.columns[1]: 'Acessos'}
    )
    fig_pizza.update_traces(textinfo='percent+label', pull=[0.05]*len(df_meio))
    fig_pizza.update_layout(
        font=dict(size=16),
        margin=dict(t=60, r=40, b=40, l=40),
        legend_title_text='Meio de Acesso',
        height=500
    )
    st.plotly_chart(fig_pizza, use_container_width=True)
    st.markdown("### Dados detalhados")
    st.dataframe(df_meio, use_container_width=True)
