import streamlit as st
import pandas as pd
import plotly.express as px

# Carrega as planilhas
df_mercado = pd.read_excel('Participacao_Mercado.xlsx')
df_meio = pd.read_excel('Meio_Acesso.xlsx')

# Unifica nomes e coloca tudo em maiúsculo
df_mercado[df_mercado.columns[0]] = df_mercado[df_mercado.columns[0]].replace({
    'NMULTIFIBRA TELECOMUNICACAO LTDA': 'N-multimidia Telecomunicacoes Ltda',
    'N-multimidia Telecomunicacoes Ltda': 'N-multimidia Telecomunicacoes Ltda'
})
df_mercado[df_mercado.columns[0]] = df_mercado[df_mercado.columns[0]].str.upper()
df_meio[df_meio.columns[0]] = df_meio[df_meio.columns[0]].str.upper()

# Agrupa acessos por provedora
df_grouped = df_mercado.groupby(df_mercado.columns[0], as_index=False)[df_mercado.columns[1]].sum()
df_grouped = df_grouped.sort_values(df_grouped.columns[1], ascending=False)

# Total de acessos
total_acessos = df_grouped[df_grouped.columns[1]].sum()

st.title('Dashboard Provedoras de Internet')

# Sessão de métricas gerais
st.metric('Total de Acessos', f'{int(total_acessos):,}')

# Tabs para dividir o dashboard
tab1, tab2, tab3 = st.tabs(['Comparar Provedoras', 'Ranking Horizontal', 'Buscar Provedora'])

with tab1:
    st.header('Comparação entre Provedoras')
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
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={df_selecionadas.columns[0]: 'OPERADORA', df_selecionadas.columns[1]: 'ACESSOS'},
        hover_data={df_selecionadas.columns[0]: True, df_selecionadas.columns[1]: ':.0f'}
    )
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Acessos: %{y:,}<extra></extra>'
    )
    fig.update_layout(
        xaxis_title='Operadora',
        yaxis_title='Acessos',
        showlegend=False,
        margin=dict(t=80, r=40, b=40, l=40),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header('Ranking Geral de Provedoras')
    fig2 = px.bar(
        df_grouped,
        x=df_grouped.columns[1],
        y=df_grouped.columns[0],
        orientation='h',
        text=df_grouped.columns[1],
        color=df_grouped.columns[0],
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={df_grouped.columns[0]: 'OPERADORA', df_grouped.columns[1]: 'ACESSOS'},
        hover_data={df_grouped.columns[0]: True, df_grouped.columns[1]: ':.0f'}
    )
    fig2.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Acessos: %{x:,}<extra></extra>'
    )
    fig2.update_layout(
        yaxis={'categoryorder':'total ascending'},
        xaxis_title='Acessos',
        yaxis_title='Operadora',
        showlegend=False,
        margin=dict(t=80, r=40, b=40, l=40),
        height=600
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.header('Buscar Provedora')
    busca = st.text_input('Digite parte do nome da provedora (não importa maiúsculo/minúsculo):')
    if busca:
        resultado = df_grouped[df_grouped[df_grouped.columns[0]].str.contains(busca, case=False, na=False)]
        if not resultado.empty:
            st.write('Resultado da busca:')
            st.dataframe(resultado)
            fig3 = px.bar(
                resultado,
                x=resultado.columns[0],
                y=resultado.columns[1],
                text=resultado.columns[1],
                color=resultado.columns[0],
                color_discrete_sequence=px.colors.sequential.Viridis,
                labels={resultado.columns[0]: 'OPERADORA', resultado.columns[1]: 'ACESSOS'},
            )
            fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning('Provedora não encontrada.')

# Sessão opcional: mostrar dados de meio de acesso
with st.expander('Ver dados de Meio de Acesso'):
    st.dataframe(df_meio)
