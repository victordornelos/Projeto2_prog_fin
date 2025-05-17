#pip install -r requirements.txt


# Bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy_financial as npf


def simulador_carro(r, t, valor_total_bem, entrada_percentual=0.0):
    """
    Simula um financiamento com parcelas mensais fixas (Tabela Price),
    e retorna uma tabela com a composição de juros e amortização,
    além de um gráfico e a razão entre valor total pago e valor à vista.

    Parâmetros:
    r  = taxa de juros anual (ex: 0.12 para 12% a.a)
    t  = número total de meses (parcelas)
    valor_total_bem = valor total do bem (valor financiado + entrada)
    entrada_percentual = percentual do valor total pago à vista como entrada (ex: 0.1 para 10%)

    Retorna:
    - DataFrame com prestações, juros e amortização
    - Gráfico com evolução de juros e amortização
    - Impressão da relação total pago / valor à vista
    """
    entrada = valor_total_bem * entrada_percentual
    pv = valor_total_bem - entrada
    print(f"Valor total do bem: R${valor_total_bem:.2f}")
    print(f"Entrada ({entrada_percentual*100:.1f}%): R${entrada:.2f}")

    saldo_devedor = pv

    dados = []
    for i in range(1, t + 1):
        pmt = float(npf.pmt(r / 12, t, -pv))
        ipmt = float(npf.ipmt(r / 12, i, t, -pv))
        ppmt = float(npf.ppmt(r / 12, i, t, -pv))
        saldo_devedor -= ppmt
        dados.append({
            'Mês': i,
            'Prestação Mensal (R$)': round(pmt, 2),
            'Parcela de Juros (R$)': round(ipmt, 2),
            'Amortização do Principal (R$)': round(ppmt, 2),
            'Saldo Devedor (R$)': round(saldo_devedor, 2)
        })

    df = pd.DataFrame(dados)
    juros_acumulado = []
    soma_juros = 0
    for valor in df['Parcela de Juros (R$)']:
        soma_juros += valor
        juros_acumulado.append(soma_juros)
    df['Juros Acumulados (R$)'] = juros_acumulado
    df['Amortização Acumulada (R$)'] = df['Amortização do Principal (R$)'].cumsum()

    import plotly.express as px

    fig = px.line(
        df,
        x='Mês',
        y=['Juros Acumulados (R$)', 'Amortização Acumulada (R$)', 'Saldo Devedor (R$)'],
        labels={'value': 'Valor (R$)', 'variable': 'Categoria'},
        title='Evolução do Financiamento'
    )
    fig.for_each_trace(
        lambda t: t.update(line=dict(
            color={'Juros Acumulados (R$)': 'green',
                   'Amortização Acumulada (R$)': 'blue',
                   'Saldo Devedor (R$)': 'red'}[t.name])
        )
    )
    fig.show()

    # Gráfico Seaborn para os mesmos dados acumulados
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Mês', y='Juros Acumulados (R$)', label='Juros Acumulados', color='green')
    sns.lineplot(data=df, x='Mês', y='Amortização Acumulada (R$)', label='Amortização Acumulada', color='blue')
    sns.lineplot(data=df, x='Mês', y='Saldo Devedor (R$)', label='Saldo Devedor', color='red')
    plt.title('Evolução do Financiamento (PRICE)')
    plt.xlabel('Mês')
    plt.ylabel('(R$)')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()

    # Valor total pago (incluindo entrada)
    valor_total_prestacoes = df['Prestação Mensal (R$)'].sum()
    valor_total_pago = valor_total_prestacoes + entrada
    relacao_total_por_valor_total = valor_total_pago / valor_total_bem

    # Exibindo a relação total pago / valor do bem
    print(f"Total pago em prestações: R${valor_total_prestacoes:.2f}")
    print(f"Valor total pago (incluindo entrada): R${valor_total_pago:.2f}")
    print(f"Relação (Total pago / Valor do carro): {relacao_total_por_valor_total:.2f}")

    df.to_excel('simulador_carro.xlsx', index=False)
    print("Tabela salva como 'simulador_carro.xlsx'.")

    return df


# --- Adicionando simulador_casa ---
def simulador_casa(r, t, valor_total_bem, entrada_percentual=0.0):
    """
    Simula um financiamento com parcelas decrescentes (Sistema SAC),
    e retorna uma tabela com a composição de juros e amortização,
    além de gráficos e a razão entre valor total pago e valor à vista.

    Parâmetros:
    r  = taxa de juros anual (ex: 0.12 para 12% a.a)
    t  = número total de meses (parcelas)
    valor_total_bem = valor total do bem (valor financiado + entrada)
    entrada_percentual = percentual do valor total pago à vista como entrada (ex: 0.1 para 10%)

    Retorna:
    - DataFrame com prestações, juros e amortização
    - Gráficos com evolução do financiamento
    - Impressão da relação total pago / valor à vista
    """
    entrada = valor_total_bem * entrada_percentual
    pv = valor_total_bem - entrada
    print(f"Valor total do bem: R${valor_total_bem:.2f}")
    print(f"Entrada ({entrada_percentual*100:.1f}%): R${entrada:.2f}")

    A = pv / t
    saldo_devedor = pv

    dados = []
    for i in range(1, t + 1):
        juros = saldo_devedor * (r / 12)
        prestacao = A + juros
        dados.append({
            'Mês': i,
            'Prestação Mensal (R$)': round(prestacao, 2),
            'Parcela de Juros (R$)': round(juros, 2),
            'Amortização do Principal (R$)': round(A, 2),
            'Saldo Devedor (R$)': round(saldo_devedor, 2)
        })
        saldo_devedor -= A

    df = pd.DataFrame(dados)
    df['Juros Acumulados (R$)'] = df['Parcela de Juros (R$)'].cumsum()
    df['Amortização Acumulada (R$)'] = df['Amortização do Principal (R$)'].cumsum()

    fig = px.line(
        df,
        x='Mês',
        y=['Juros Acumulados (R$)', 'Amortização Acumulada (R$)', 'Saldo Devedor (R$)'],
        labels={'value': 'Valor (R$)', 'variable': 'Categoria'},
        title='Evolução do Financiamento (SAC)'
    )
    fig.for_each_trace(
        lambda t: t.update(line=dict(
            color={'Juros Acumulados (R$)': 'green',
                   'Amortização Acumulada (R$)': 'blue',
                   'Saldo Devedor (R$)': 'red'}[t.name])
        )
    )
    fig.show()

    # Gráfico Seaborn
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Mês', y='Juros Acumulados (R$)', label='Juros Acumulados', color='green')
    sns.lineplot(data=df, x='Mês', y='Amortização Acumulada (R$)', label='Amortização Acumulada', color='blue')
    sns.lineplot(data=df, x='Mês', y='Saldo Devedor (R$)', label='Saldo Devedor', color='red')
    plt.title('Evolução do Financiamento (SAC)')
    plt.xlabel('Mês')
    plt.ylabel('Valor (R$)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    valor_total_prestacoes = df['Prestação Mensal (R$)'].sum()
    valor_total_pago = valor_total_prestacoes + entrada
    relacao_total_por_valor_total = valor_total_pago / valor_total_bem

    print(f"Total pago em prestações: R${valor_total_prestacoes:.2f}")
    print(f"Valor total pago (incluindo entrada): R${valor_total_pago:.2f}")
    print(f"Relação (Total pago / Valor do bem): {relacao_total_por_valor_total:.2f}")
    df.to_excel('simulador_casa.xlsx', index=False)
    print("Tabela salva como 'simulador_casa.xlsx'.")
    return df
