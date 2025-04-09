import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis Financiero", layout="centered")

# Sidebar - Entrada del usuario
st.sidebar.title("Parámetros de Búsqueda")
ticker_input = st.sidebar.text_input("Ingresa el Ticker (ej. AAPL)", value="AAPL")
hoy = datetime.date.today()
inicio = hoy - datetime.timedelta(days=5*365)
fecha_inicio = st.sidebar.date_input("Fecha de inicio", inicio)
fecha_fin = st.sidebar.date_input("Fecha de fin", hoy)

st.title("📊 Análisis Financiero con Streamlit")

# Validación del ticker
try:
    ticker = yf.Ticker(ticker_input)
    info = ticker.info
    nombre = info.get("longName", "Nombre no disponible")
    sector = info.get("sector", "Sector no disponible")
    descripcion = info.get("longBusinessSummary", "Descripción no disponible")
except Exception:
    st.error("❌ Ticker inválido. Por favor, intenta con otro.")
    st.stop()

# Mostrar información de la empresa
st.header(f"{nombre}")
st.markdown(f"**Sector:** {sector}")
st.markdown(f"**Descripción:** {descripcion}")

# Descargar precios históricos
df = ticker.history(start=fecha_inicio, end=fecha_fin)
if df.empty:
    st.error("No hay datos disponibles para el rango de fechas seleccionado.")
    st.stop()

df = df[["Close"]]
df.rename(columns={"Close": "Precio Cierre"}, inplace=True)

# Gráfica de precios históricos
st.subheader("📈 Precio histórico de cierre ajustado")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Precio Cierre"], mode="lines", name=ticker_input))
fig.update_layout(title=f"Precio histórico - {ticker_input}",
                  xaxis_title="Fecha", yaxis_title="Precio de Cierre (USD)")
st.plotly_chart(fig)

# Cálculo de CAGR
def calcular_cagr(precios, años):
    if len(precios) < 2:
        return None
    return ((precios[-1] / precios[0]) ** (1/años)) - 1

st.subheader("📊 Rendimientos Anualizados")
import pandas as pd
import numpy as np
import datetime
import streamlit as st

# Asegúrate de que 'fechas' (el índice del DataFrame) sea de tipo datetime
fechas = pd.to_datetime(df.index)

# Asegúrate de que 'fecha_fin' sea de tipo datetime
fecha_fin = pd.to_datetime(fecha_fin)

# Calcula el CAGR para 1, 3 y 5 años
cagr_1 = calcular_cagr(df["Precio Cierre"].loc[fechas >= (fecha_fin - datetime.timedelta(days=365))], 1)
cagr_3 = calcular_cagr(df["Precio Cierre"].loc[fechas >= (fecha_fin - datetime.timedelta(days=3*365))], 3)
cagr_5 = calcular_cagr(df["Precio Cierre"], 5)

# Crear un diccionario con los resultados del CAGR
rendimientos = {
    "Periodo": ["1 año", "3 años", "5 años"],
    "CAGR (%)": [round(c * 100, 2) if c is not None else "N/A" for c in [cagr_1, cagr_3, cagr_5]]
}

# Mostrar los rendimientos en Streamlit
st.dataframe(pd.DataFrame(rendimientos))

# Explicación en markdown sobre el cálculo del CAGR
st.markdown(
    "📌 **Nota:** El rendimiento anualizado (CAGR) se calcula como el crecimiento compuesto anual del precio de la acción para cada período."
)

# Cálculo de volatilidad anualizada
st.subheader("📉 Volatilidad Anualizada")
df["Retornos Diarios"] = df["Precio Cierre"].pct_change()

# Cálculo de volatilidad basada en los retornos diarios
volatilidad = np.std(df["Retornos Diarios"].dropna()) * np.sqrt(252)

# Mostrar la volatilidad anualizada en Streamlit
st.metric(label="Volatilidad anualizada (%)", value=f"{round(volatilidad*100, 2)}%")
st.markdown("📌 **Nota:** La volatilidad mide el riesgo, basada en la desviación estándar de los retornos diarios.")

# Footer
st.markdown("---")
st.markdown("Desarrollado por Iker Ripoll Solana")

