#pip install -r requirements.txt


# Bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from IPython.display import display, Markdown
from tabulate import tabulate
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

    dados = []
    for i in range(1, t + 1):
        pmt = float(npf.pmt(r / 12, t, -pv))
        ipmt = float(npf.ipmt(r / 12, i, t, -pv))
        ppmt = float(npf.ppmt(r / 12, i, t, -pv))
        dados.append({
            'Mês': i,
            'Prestação Mensal (R$)': round(pmt, 2),
            'Parcela de Juros (R$)': round(ipmt, 2),
            'Amortização do Principal (R$)': round(ppmt, 2)
        })

    df = pd.DataFrame(dados)
    juros_acumulado = []
    soma_juros = 0
    for valor in df['Parcela de Juros (R$)']:
        soma_juros += valor
        juros_acumulado.append(soma_juros)
    df['Juros Acumulados (R$)'] = juros_acumulado
    df['Amortização Acumulada (R$)'] = df['Amortização do Principal (R$)'].cumsum()

    # Gráfico com seaborn (valores acumulados)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Mês', y='Juros Acumulados (R$)', label='Juros Acumulados')
    sns.lineplot(data=df, x='Mês', y='Amortização Acumulada (R$)', label='Amortização Acumulada')
    plt.title('Acúmulo de Juros e Amortização ao Longo do Tempo')
    plt.xlabel('Mês')
    plt.ylabel('Valor (R$)')
    plt.grid(True)
    plt.legend()
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
    return df
