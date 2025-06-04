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

# Total de acessos
total_acessos = df_grouped[df_grouped.columns[1]].sum()

# Título
st.title('Dashboard Provedoras de Internet')

# Mostra o total de acessos
st.metric('Total de Acessos', f'{int(total_acessos):,}')

# Gráfico de comparação entre provedoras
fig = px.bar(
    df_grouped,
    x=df_grouped.columns[0],
    y=df_grouped.columns[1],
    text=df_grouped.columns[1],
    color=df_grouped.columns[0],
    color_discrete_sequence=px.colors.sequential.Viridis,
    labels={df_grouped.columns[0]: 'OPERADORA', df_grouped.columns[1]: 'ACESSOS'},
    hover_data={df_grouped.columns[0]: True, df_grouped.columns[1]: ':.0f'}
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

# Campo de busca para provedora específica
st.subheader('Buscar Provedora')
busca = st.text_input('Digite o nome da provedora (não importa maiúsculo/minúsculo):')

if busca:
    busca_upper = busca.upper()
    resultado = df_grouped[df_grouped[df_grouped.columns[0]].str.contains(busca_upper, case=False, na=False)]
    if not resultado.empty:
        st.write('Resultado da busca:')
        st.dataframe(resultado)
        # Gráfico só da provedora buscada
        fig2 = px.bar(
            resultado,
            x=resultado.columns[0],
            y=resultado.columns[1],
            text=resultado.columns[1],
            color=resultado.columns[0],
            color_discrete_sequence=px.colors.sequential.Viridis,
            labels={resultado.columns[0]: 'OPERADORA', resultado.columns[1]: 'ACESSOS'},
        )
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning('Provedora não encontrada.')

# Exemplo de integração com a planilha Meio_Acesso (opcional)
st.subheader('Dados de Meio de Acesso (opcional)')
st.dataframe(df_meio)