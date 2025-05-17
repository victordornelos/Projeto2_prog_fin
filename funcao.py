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


# Função para gerar a tabela Price
def tabela_price(valor_financiado, taxa_juros, num_prestacoes):
    """
    Gera a tabela Price no formato visualizado com as colunas:
    'Mês', 'Prestação', 'Juros da Parcela', 'Amortização do Principal', 'Saldo Devedor Restante'
    """
    tabela = []
    saldo_restante = valor_financiado

    for mes in range(1, num_prestacoes + 1):
        pgto = round(npf.pmt(taxa_juros, num_prestacoes, -valor_financiado), 2)
        jrs = round(float(npf.ipmt(taxa_juros, mes, num_prestacoes, -valor_financiado)), 2)
        principal = round(float(npf.ppmt(taxa_juros, mes, num_prestacoes, -valor_financiado)), 2)
        saldo_restante = round(saldo_restante + principal, 2)  # principal é negativo
        tabela.append([mes, pgto, jrs, -principal, saldo_restante])

    colunas = ['Mês', 'Prestação', 'Juros da Parcela', 'Amortização do Principal', 'Saldo Devedor Restante']
    return pd.DataFrame(tabela, columns=colunas)


# Teste da função
if __name__ == "__main__":
    df_teste = tabela_price(100000, 0.0118, 60)
    print(df_teste.head())
    # Exportar para Excel
    df_teste.to_excel("tabela_price_teste.xlsx", index=False)
    print("Arquivo Excel salvo como 'tabela_price_teste.xlsx'")
