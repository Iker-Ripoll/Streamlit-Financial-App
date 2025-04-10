import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go
import datetime
import google.generativeai as genai
import os

# CONFIGURACIÓN DE GEMINI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Función para llamar a Gemini y obtener resumen traducido
def llamar_a_gemini(prompt):
    modelo = genai.GenerativeModel("gemini-pro")
    respuesta = modelo.generate_content(prompt)
    return respuesta.text

# Función para calcular CAGR
def calcular_cagr(precios, periodos):
    inicio = precios.iloc[0]
    fin = precios.iloc[-1]
    cagr = (fin / inicio) ** (1 / periodos) - 1
    return cagr

# Configuración inicial de Streamlit
st.set_page_config(page_title="Análisis Financiero", page_icon="📊", layout="wide")
st.markdown("<h1 style='text-align: center;'>Análisis Financiero Interactivo</h1>", unsafe_allow_html=True)
st.markdown("""
Esta aplicación permite analizar el desempeño de una empresa en la bolsa de valores mediante el uso de datos históricos de precios de acciones y métricas financieras. 
Introduce el ticker de una acción para obtener información detallada, gráficas y análisis.
""")

# Entrada de datos - Ticker
ticker = st.text_input("Introduce el Ticker de la Empresa (Ej. AAPL, MSFT, TSLA):")

if ticker:
    try:
        empresa = yf.Ticker(ticker)
        info = empresa.info
        precios = empresa.history(period="5y")

        st.subheader(f"Información de {info['shortName']}")
        st.markdown(f"**Sector:** {info.get('sector', 'No disponible')}")

        # RESUMEN CON GEMINI
        resumen_largo = info.get("longBusinessSummary", "")
        if resumen_largo:
            prompt_resumen = f"""
            Actúa como un analista financiero bilingüe. Resume y traduce al español el siguiente perfil empresarial en un texto profesional, claro y orientado a inversionistas, con un máximo de 300 palabras:

            {resumen_largo}
            """
            resumen_es = llamar_a_gemini(prompt_resumen)
            st.subheader("📘 Resumen de la Empresa (Traducido y Resumido)")
            st.markdown(f"<div style='text-align: justify;'>{resumen_es}</div>", unsafe_allow_html=True)
        else:
            st.warning("No se encontró un resumen disponible para esta empresa.")

        st.markdown("---")

        # Precio histórico
        st.subheader("📈 Precio Histórico de Cierre Ajustado")
        fig = go.Figure(data=[go.Scatter(x=precios.index, y=precios['Close'], mode='lines', name='Precio de Cierre Ajustado')])
        fig.update_layout(title=f"Precio Histórico de Cierre Ajustado - {ticker} (2019-2024)",
                          xaxis_title="Fecha", yaxis_title="Precio (USD)",
                          template="plotly_dark", font=dict(size=14))
        st.plotly_chart(fig)

        st.markdown("""
        **Nota**: El gráfico de precio histórico muestra la evolución del valor de la acción en los últimos 5 años.
        """)
        st.markdown("---")

        # CAGR
        st.subheader("📈 Rendimientos Anualizados (CAGR)")
        cagr_1 = calcular_cagr(precios['Close'], 1)
        cagr_3 = calcular_cagr(precios['Close'], 3)
        cagr_5 = calcular_cagr(precios['Close'], 5)
        rendimientos = {
            "Periodo": ["1 Año", "3 Años", "5 Años"],
            "CAGR (%)": [round(cagr_1 * 100, 2), round(cagr_3 * 100, 2), round(cagr_5 * 100, 2)]
        }
        st.dataframe(pd.DataFrame(rendimientos))
        st.markdown("**Nota:** El CAGR indica el crecimiento anual compuesto del precio.")
        st.markdown("---")

        # Volatilidad
        st.subheader("📉 Volatilidad Anualizada")
        precios["Retornos Diarios"] = precios["Close"].pct_change()
        volatilidad = np.std(precios["Retornos Diarios"].dropna()) * np.sqrt(252)
        st.metric(label="Volatilidad Anualizada (%)", value=f"{round(volatilidad * 100, 2)}%")
        st.markdown("**Nota:** La volatilidad refleja el nivel de riesgo o variación de retornos.")
        st.markdown("---")

        # Histograma de retornos
        st.subheader("📊 Histograma de los Retornos Diarios")
        fig_vol = go.Figure(data=[go.Histogram(x=precios["Retornos Diarios"].dropna(), nbinsx=50)])
        fig_vol.update_layout(title="Histograma de los Retornos Diarios",
                              xaxis_title="Retornos Diarios", yaxis_title="Frecuencia",
                              template="plotly_dark", font=dict(size=14))
        st.plotly_chart(fig_vol)

        st.markdown("""
        **Nota**: Este histograma permite observar la distribución de rendimientos diarios de la acción.
        """)

    except (ValueError, KeyError):
        st.error("*Introduzca un ticker correcto.*")
else:
    st.info("*Introduce un ticker para comenzar el análisis.*")

# Footer
st.markdown("---")
st.markdown("**Desarrollado por Iker Ripoll Solana**")
st.markdown("**Lic. Administración y Finanzas**")
st.markdown("**ID: 0243449**")
st.markdown("**APP Desarrollada para el Examen de Ingeniería Financiera**")
