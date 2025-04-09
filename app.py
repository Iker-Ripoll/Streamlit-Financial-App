import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go
import datetime

# Función para calcular el CAGR (Tasa de Crecimiento Compuesta Anual)
def calcular_cagr(precios, periodos):
    inicio = precios.iloc[0]
    fin = precios.iloc[-1]
    cagr = (fin / inicio) ** (1 / periodos) - 1
    return cagr

# Configuración inicial de Streamlit
st.set_page_config(page_title="Análisis Financiero", page_icon="📊", layout="wide")

# Título centrado
st.markdown("<h1 style='text-align: center;'>Análisis Financiero Interactivo</h1>", unsafe_allow_html=True)

st.markdown("""
Esta aplicación permite analizar el desempeño de una empresa en la bolsa de valores mediante el uso de datos históricos de precios de acciones y métricas financieras. 
Introduce el ticker de una acción para obtener información detallada, gráficas y análisis.
""")

# Entrada de datos - Ticker de la empresa
ticker = st.text_input("Introduce el Ticker de la Empresa (Ej. AAPL, MSFT, TSLA):")

if ticker:
    # Extracción de información con yfinance
    try:
        empresa = yf.Ticker(ticker)
        info = empresa.info
        precios = empresa.history(period="5y")  # Obtiene datos de 5 años

        # Mostrar información fundamental
        st.subheader(f"Información de {info['shortName']}")
        st.markdown(f"**Sector:** {info['sector']}")
        st.markdown(f"**Descripción:** {info['longBusinessSummary']}")

        # Visualización de precios históricos
        st.subheader("📉 Precio Histórico de Cierre Ajustado")
        fig = go.Figure(data=[go.Scatter(x=precios.index, y=precios['Close'], mode='lines', name='Precio de Cierre Ajustado')])
        fig.update_layout(title=f"Precio Histórico de Cierre Ajustado - {ticker} (2019-2024)",
                          xaxis_title="Fecha",
                          yaxis_title="Precio (USD)",
                          template="plotly_dark")
        st.plotly_chart(fig)

        # Cálculo de rendimientos anualizados (CAGR)
        st.subheader("📈 Rendimientos Anualizados (CAGR)")
        cagr_1 = calcular_cagr(precios['Close'], 1)
        cagr_3 = calcular_cagr(precios['Close'], 3)
        cagr_5 = calcular_cagr(precios['Close'], 5)

        rendimientos = {
            "Periodo": ["1 Año", "3 Años", "5 Años"],
            "CAGR (%)": [round(cagr_1 * 100, 2), round(cagr_3 * 100, 2), round(cagr_5 * 100, 2)]
        }

        st.dataframe(pd.DataFrame(rendimientos))
        st.markdown("""
        **Nota:** El rendimiento anualizado (CAGR) se calcula como el crecimiento compuesto anual del precio de la acción para cada período.
        """)

        # Cálculo de volatilidad anualizada
        st.subheader("📉 Volatilidad Anualizada")
        precios["Retornos Diarios"] = precios["Close"].pct_change()
        volatilidad = np.std(precios["Retornos Diarios"].dropna()) * np.sqrt(252)
        st.metric(label="Volatilidad Anualizada (%)", value=f"{round(volatilidad * 100, 2)}%")
        st.markdown("""
        **Nota:** La volatilidad mide el riesgo, basada en la desviación estándar de los retornos diarios de la acción.
        """)

        # Gráfico adicional de volatilidad (histograma de los retornos diarios)
        st.subheader("📊 Histograma de los Retornos Diarios")
        fig_volatilidad = go.Figure(data=[go.Histogram(x=precios["Retornos Diarios"].dropna(), nbinsx=50)])
        fig_volatilidad.update_layout(title="Histograma de los Retornos Diarios",
                                      xaxis_title="Retornos Diarios",
                                      yaxis_title="Frecuencia",
                                      template="plotly_dark")
        st.plotly_chart(fig_volatilidad)

    except ValueError:
        st.error("Ticker inválido, por favor revise e intente de nuevo.")
else:
    st.info("Introduce un ticker para comenzar el análisis.")

# Footer
st.markdown("---")
st.markdown("Desarrollado por Iker Ripoll Solana")

