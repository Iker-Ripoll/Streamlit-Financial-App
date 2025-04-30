import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import httpx
import json
import os

# --- CONFIGURACION GENERAL ---
st.set_page_config(page_title="Asesor de Inversión", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    body { background-color: #ffffff; color: #000000; }
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #1DA1F2; }
    .stButton>button { background-color: #1DA1F2; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Asesor de Inversión Personalizado")

# --- FUNCION PARA CONSULTAR A CLAUDE AI ---
async def analizar_perfil_con_claude(respuestas_dict):
    api_key = os.getenv("CLAUDE_API_KEY")
    prompt_sistema = """Como analista experto en riesgos de inversión con más de 20 años de experiencia...
    (el prompt completo va aquí, recortado por brevedad)"""
    mensaje_usuario = f"Estas son las respuestas del usuario: {json.dumps(respuestas_dict)}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensaje_usuario}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        return r.json()["content"]

# --- CUESTIONARIO DIVIDIDO POR SECCIONES ---
respuestas = {}
secciones = {
    "1. Datos Personales y Financieros": ["Edad", "Situación laboral", "Ingreso anual", "% a invertir"],
    "2. Experiencia y Conocimientos": ["Nivel de conocimiento", "Tipo de inversiones realizadas"],
    "3. Tolerancia al Riesgo": ["Reacción ante pérdidas", "Expectativas de rendimiento"],
    "4. Objetivos de Inversión": ["Objetivo principal", "Horizonte de uso del capital"],
    "5. Circunstancias Personales": ["Dependientes económicos", "Estabilidad laboral"],
    "6. Factores Psicológicos": ["Actitud ante decisiones", "Reacción emocional ante pérdidas"],
    "7. Capacidad Financiera": ["% del patrimonio invertido", "Fondo de emergencia"]
}

with st.form("cuestionario_form"):
    st.subheader("📝 Cuestionario de Perfil de Riesgo")
    for seccion, preguntas in secciones.items():
        with st.expander(seccion):
            for pregunta in preguntas:
                respuestas[pregunta] = st.text_input(pregunta)
    enviado = st.form_submit_button("Enviar respuestas")

# --- ANALISIS DE RESPUESTAS ---
if enviado:
    st.success("✅ Respuestas enviadas. Analizando perfil con Claude AI...")

    import asyncio
    resultado = asyncio.run(analizar_perfil_con_claude(respuestas))

    st.subheader("🔍 Resultado de Claude AI")
    st.markdown(resultado)

    st.divider()
    st.header("📈 Portafolio Recomendado")

    portafolio = {"Tesla": 0.4, "Apple": 0.3, "Microsoft": 0.3}
    monto = st.number_input("💰 Ingresa el monto a invertir:", min_value=1000, step=1000)

    if monto:
        tickers = list(portafolio.keys())
        data = yf.download(tickers, period="1d")['Adj Close']
        precios_actuales = data.iloc[0].to_dict()

        st.subheader("📊 Distribución del Portafolio")
        pesos = [v for v in portafolio.values()]
        fig = px.pie(names=tickers, values=pesos, title="Distribución %")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Detalle del Portafolio")
        df = pd.DataFrame({
            "Empresa": tickers,
            "% del Portafolio": pesos,
            "Precio Actual": [precios_actuales[t] for t in tickers],
            "Monto Invertido": [monto * p for p in pesos]
        })
        df["Acciones Compradas"] = df["Monto Invertido"] / df["Precio Actual"]
        df["Precio de Compra"] = df["Precio Actual"]  # Simulado
        df["Ganancia/Perdida $"] = 0
        df["Ganancia/Perdida %"] = 0

        st.dataframe(df, use_container_width=True)
