#pip install -r requirements.txt


# Bibliotecas necessárias
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy_financial as npf


def simulador_carro(r, t, valor_total_bem, entrada_percentual=0.0):

    # Cálculo da entrada e valor financiado
    entrada = valor_total_bem * entrada_percentual
    pv_original = valor_total_bem - entrada

    # Cálculo do IOF
    dias = t * 30
    iof_adicional = 0.0038
    iof_diario = 0.000082
    iof_total_percentual = min(iof_adicional + iof_diario * dias, 0.0338)
    iof_valor = pv_original * iof_total_percentual

    pv = pv_original + iof_valor

    print(f"Valor total do bem: R${valor_total_bem:.2f}")
    print(f"Entrada ({entrada_percentual*100:.1f}%): R${entrada:.2f}")
    print(f"IOF Total aplicado: R${iof_valor:.2f} ({iof_total_percentual*100:.2f}%)")
    print(f"Valor financiado com IOF: R${pv:.2f}")

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
    df['Juros Acumulados (R$)'] = df['Parcela de Juros (R$)'].cumsum()
    df['Amortização Acumulada (R$)'] = df['Amortização do Principal (R$)'].cumsum()

    fig = px.line(
        df,
        x='Mês',
        y=['Juros Acumulados (R$)', 'Amortização Acumulada (R$)', 'Saldo Devedor (R$)'],
        labels={'value': 'Valor (R$)', 'variable': 'Categoria'},
        title='Evolução do Financiamento com IOF'
    )
    fig.for_each_trace(
        lambda t: t.update(line=dict(
            color={'Juros Acumulados (R$)': 'green',
                   'Amortização Acumulada (R$)': 'blue',
                   'Saldo Devedor (R$)': 'red'}[t.name])
        )
    )
    fig.show()

    # Gráfico com Seaborn
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='Mês', y='Juros Acumulados (R$)', label='Juros Acumulados', color='green')
    sns.lineplot(data=df, x='Mês', y='Amortização Acumulada (R$)', label='Amortização Acumulada', color='blue')
    sns.lineplot(data=df, x='Mês', y='Saldo Devedor (R$)', label='Saldo Devedor', color='red')
    plt.title('Evolução do Financiamento (Price) com IOF')
    plt.xlabel('Mês')
    plt.ylabel('R$')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show()

    valor_total_prestacoes = df['Prestação Mensal (R$)'].sum()
    valor_total_pago = valor_total_prestacoes + entrada
    relacao_total_por_valor_total = valor_total_pago / valor_total_bem

    print(f"Total pago em prestações: R${valor_total_prestacoes:.2f}")
    print(f"Valor total pago (incluindo entrada): R${valor_total_pago:.2f}")
    print(f"Relação (Total pago / Valor do bem à vista): {relacao_total_por_valor_total:.2f}")

    df.to_excel('simulador_carro_com_iof.xlsx', index=False)
    print("Tabela salva como 'simulador_carro_com_iof.xlsx'.")

    return df


# --- Adicionando simulador_casa ---
def simulador_casa(cet_anual, t, valor_total_bem, entrada_percentual=0.0, taxa_tr_anual=0.0):
    """
    Simula um financiamento imobiliário com recálculo mensal da amortização,
    considerando um Custo Efetivo Total (CET) e uma Taxa Referencial (TR).
    A TR corrige o saldo devedor. Os juros (CET) incidem sobre o saldo corrigido.
    A amortização é recalculada a cada mês como: Saldo Devedor Corrigido / Parcelas Restantes.
    As taxas anuais (CET, TR) são convertidas para mensais usando juros compostos.

    Parâmetros:
    cet_anual = Custo Efetivo Total anual (ex: 0.12 para 12% a.a)
    t         = número total de meses (parcelas)
    valor_total_bem = valor total do bem (valor financiado + entrada)
    entrada_percentual = percentual do valor total pago à vista como entrada (ex: 0.1 para 10%)
    taxa_tr_anual = taxa referencial anual que corrige o saldo devedor (ex: 0.01 para 1% a.a)

    Retorna:
    - DataFrame com prestações, juros, correção TR e amortização
    - Gráficos com evolução do financiamento
    - Impressão da relação total pago / valor à vista
    """
    # --- Validações Iniciais ---
    if not isinstance(cet_anual, (int, float)) or cet_anual < 0:
        print("Erro: O CET anual (cet_anual) deve ser um número não negativo.")
        return None
    if not isinstance(t, int) or t <= 0:
        print("Erro: O número total de meses (t) deve ser um inteiro positivo.")
        return None
    # ... (restante das validações como antes) ...
    if not isinstance(valor_total_bem, (int, float)) or valor_total_bem <= 0:
        print("Erro: O valor total do bem deve ser um número positivo.")
        return None
    if not isinstance(entrada_percentual, (int, float)) or not (0 <= entrada_percentual <= 1):
        print("Erro: O percentual de entrada deve ser um número entre 0 e 1 (ex: 0.1 para 10%).")
        return None
    if not isinstance(taxa_tr_anual, (int, float)) or taxa_tr_anual < 0:
        print("Erro: A taxa TR anual deve ser um número não negativo.")
        return None

    # --- Cálculos Iniciais ---
    entrada = valor_total_bem * entrada_percentual
    pv = valor_total_bem - entrada  # Valor financiado (Principal Value)

    print(f"--- Resumo da Simulação de Financiamento Imobiliário (Amortização Recalculada com CET e TR) ---")
    print(f"Valor total do bem: R${valor_total_bem:,.2f}")
    print(f"Entrada ({entrada_percentual * 100:.1f}%): R${entrada:,.2f}")
    print(f"Valor Financiado (PV): R${pv:,.2f}")
    print(f"Custo Efetivo Total (CET) Anual: {cet_anual * 100:.2f}% a.a.")
    print(f"Taxa Referencial (TR) Anual: {taxa_tr_anual * 100:.2f}% a.a.")
    print(f"Prazo do Financiamento: {t} meses")
    print("--------------------------------------------------------------------")

    if pv == 0:  # Se o bem foi pago integralmente com a entrada
        print("\nO valor do bem foi totalmente coberto pela entrada. Não há financiamento a simular.")
        colunas = ['Mês', 'Saldo Devedor Inicial (R$)', 'Correção TR (R$)',
                   'Saldo Devedor Pós-TR (R$)', 'Parcela de Juros (R$)',
                   'Amortização do Principal (R$)', 'Prestação Mensal (R$)',
                   'Saldo Devedor Final (R$)', 'Juros Acumulados (R$)',
                   'Amortização Acumulada (R$)', 'Correção TR Acumulada (R$)']
        df_vazio = pd.DataFrame(columns=colunas)
        try:
            df_vazio.to_excel('simulador_casa_amort_recalc.xlsx', index=False)
            print("Tabela vazia salva como 'simulador_casa_amort_recalc.xlsx'.")
        except Exception as e:
            print(f"Ocorreu um erro ao salvar o arquivo Excel: {e}")
        return df_vazio

    # A amortização base A = pv / t não é mais usada como fixa.
    saldo_devedor_corrente = pv
    dados = []

    if cet_anual == 0:
        taxa_cet_mensal = 0.0
    else:
        taxa_cet_mensal = math.pow(1 + cet_anual, 1 / 12) - 1

    if taxa_tr_anual == 0:
        tr_mensal = 0.0
    else:
        tr_mensal = math.pow(1 + taxa_tr_anual, 1 / 12) - 1

    print(f"Taxa CET Mensal (calculada): {taxa_cet_mensal * 100:.6f}% a.m.")
    print(f"Taxa TR Mensal (calculada): {tr_mensal * 100:.6f}% a.m.")
    print("--------------------------------------------------------------------")

    for i in range(1, t + 1):
        saldo_devedor_inicio_mes = saldo_devedor_corrente

        # 1. Correção Monetária pela TR
        if saldo_devedor_inicio_mes <= 0.005:  # Se já está quitado (considerando pequena tolerância)
            correcao_monetaria_mes = 0.0
            saldo_devedor_apos_tr = 0.0
        else:
            correcao_monetaria_mes = saldo_devedor_inicio_mes * tr_mensal
            saldo_devedor_apos_tr = saldo_devedor_inicio_mes + correcao_monetaria_mes

        # Se a TR for muito negativa e zerar ou negativar o saldo
        if saldo_devedor_apos_tr < 0:
            # A correção monetária é o valor que 'negativou'. A 'dívida' acabou.
            # Para fins de cálculo de juros e amortização, consideramos o saldo como zero.
            saldo_devedor_apos_tr = 0.0

        # 2. Cálculo de Juros (CET)
        if saldo_devedor_apos_tr <= 0.005:  # Usar uma pequena tolerância para zero
            juros_mes = 0.0
            saldo_devedor_apos_tr = 0.0  # Normaliza se for um valor residual muito pequeno
        else:
            juros_mes = saldo_devedor_apos_tr * taxa_cet_mensal

        # 3. Cálculo da Amortização (Recalculada Mensalmente)
        if saldo_devedor_apos_tr <= 0:  # Se saldo já é zero (ou virou zero após TR/Juros)
            amortizacao_mes = 0.0
        else:
            parcelas_restantes = t - i + 1
            if parcelas_restantes > 0:
                amortizacao_mes = saldo_devedor_apos_tr / parcelas_restantes
            else:  # Não deve acontecer em um loop normal até t
                amortizacao_mes = saldo_devedor_apos_tr  # Segurança para quitar

        prestacao_mes = amortizacao_mes + juros_mes

        # 4. Atualização do Saldo Devedor
        saldo_devedor_fim_mes = saldo_devedor_apos_tr - amortizacao_mes

        # Ajuste de precisão para o saldo final do mês
        if abs(saldo_devedor_fim_mes) < 0.01:
            saldo_devedor_fim_mes = 0.0

        # No último mês, o saldo DEVE ser zero.
        # A lógica de amortizacao_mes = saldo_devedor_apos_tr / 1 (para i=t) já garante isso.
        # Este é um reforço para casos extremos de arredondamento acumulado.
        if i == t and saldo_devedor_fim_mes != 0.0:
            # Se não zerou perfeitamente, ajusta a última amortização para forçar o zero
            # Isso só deve acontecer por problemas de ponto flutuante muito pequenos
            if saldo_devedor_apos_tr > 0:  # Apenas se havia saldo
                amortizacao_mes = saldo_devedor_apos_tr  # Garante que a amortização quite
                prestacao_mes = amortizacao_mes + juros_mes  # Recalcula a prestação
            saldo_devedor_fim_mes = 0.0

        dados.append({
            'Mês': i,
            'Saldo Devedor Inicial (R$)': round(saldo_devedor_inicio_mes, 2),
            'Correção TR (R$)': round(correcao_monetaria_mes, 2),
            'Saldo Devedor Pós-TR (R$)': round(saldo_devedor_apos_tr, 2),
            'Parcela de Juros (R$)': round(juros_mes, 2),
            'Amortização do Principal (R$)': round(amortizacao_mes, 2),
            'Prestação Mensal (R$)': round(prestacao_mes, 2),
            'Saldo Devedor Final (R$)': round(saldo_devedor_fim_mes, 2)
        })

        saldo_devedor_corrente = saldo_devedor_fim_mes
        # Lógica para quitação antecipada (se saldo zerar antes do prazo)
        if saldo_devedor_corrente <= 0.005 and i < t:  # Usar tolerância
            print(f"\nAVISO: O financiamento foi quitado no mês {i} de {t}.")
            for j_fill in range(i + 1, t + 1):
                dados.append({
                    'Mês': j_fill, 'Saldo Devedor Inicial (R$)': 0, 'Correção TR (R$)': 0,
                    'Saldo Devedor Pós-TR (R$)': 0, 'Parcela de Juros (R$)': 0,
                    'Amortização do Principal (R$)': 0, 'Prestação Mensal (R$)': 0,
                    'Saldo Devedor Final (R$)': 0
                })
            break  # Interrompe o loop principal

    df = pd.DataFrame(dados)
    # ... (restante do código para gráficos, resultados finais e salvamento do Excel como antes) ...
    # ATENÇÃO: Mudar o nome do arquivo Excel na hora de salvar.
    # Ex: df.to_excel('simulador_casa_amort_recalc.xlsx', index=False)

    df['Juros Acumulados (R$)'] = df['Parcela de Juros (R$)'].cumsum()
    df['Amortização Acumulada (R$)'] = df['Amortização do Principal (R$)'].cumsum()
    df['Correção TR Acumulada (R$)'] = df['Correção TR (R$)'].cumsum()

    print("\nGerando gráficos da evolução do financiamento...")
    try:
        fig_plotly = px.line(
            df, x='Mês',
            y=['Juros Acumulados (R$)', 'Amortização Acumulada (R$)', 'Correção TR Acumulada (R$)',
               'Saldo Devedor Final (R$)'],
            labels={'value': 'Valor (R$)', 'variable': 'Legenda'},
            title='Evolução do Financiamento (SAC com TR)'
        )
        fig_plotly.for_each_trace(
            lambda trace: trace.update(line=dict(
                color={'Juros Acumulados (R$)': 'green',
                       'Amortização Acumulada (R$)': 'blue',
                       'Correção TR Acumulada (R$)': 'orange',
                       'Saldo Devedor Final (R$)': 'red'}.get(trace.name, 'grey')
            ))
        )
        fig_plotly.show()

        plt.figure(figsize=(14, 7))
        sns.lineplot(data=df, x='Mês', y='Juros Acumulados (R$)', label='Juros Acumulados (R$)', color='green',
                     marker='.')
        sns.lineplot(data=df, x='Mês', y='Amortização Acumulada (R$)', label='Amortização Acumulada (R$)', color='blue',
                     marker='.')
        sns.lineplot(data=df, x='Mês', y='Correção TR Acumulada (R$)', label='Correção TR Acumulada (R$)',
                     color='orange', marker='.')
        sns.lineplot(data=df, x='Mês', y='Saldo Devedor Final (R$)', label='Saldo Devedor Final (R$)', color='red',
                     marker='.')

        plt.title('Evolução do Financiamento (SAC com TR)')
        plt.xlabel('Mês')
        plt.ylabel('Valor (R$)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Ocorreu um erro ao gerar os gráficos: {e}")

    valor_total_prestacoes = df['Prestação Mensal (R$)'].sum()
    valor_total_pago = valor_total_prestacoes + entrada

    relacao_total_por_valor_total = valor_total_pago / valor_total_bem if valor_total_bem > 0 else 0

    print(f"\n--- Resultados Finais da Simulação ---")
    print(f"Total pago em prestações: R${valor_total_prestacoes:,.2f}")
    print(f"Valor total pago (incluindo entrada): R${valor_total_pago:,.2f}")
    if valor_total_bem > 0:
        print(f"Relação (Total pago / Valor do bem): {relacao_total_por_valor_total:.2f}")

    saldo_residual_final = df['Saldo Devedor Final (R$)'].iloc[-1] if not df.empty else 0.0
    if abs(saldo_residual_final) > 0.01:  # Deveria ser zero com a nova lógica
        print(f"ATENÇÃO: Saldo devedor residual ao final dos {t} meses: R${saldo_residual_final:,.2f}")
    elif pv > 0:
        print("O financiamento foi quitado ao final do período.")
    print("--------------------------------------")

    try:
        nome_arquivo_excel = 'simulador_casa.xlsx'
        df.to_excel(nome_arquivo_excel, index=False)
        print(f"\nTabela detalhada salva como '{nome_arquivo_excel}'.")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo Excel: {e}")

    return df
