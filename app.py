import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Diagnóstico Financiero", layout="centered")

st.title("📊 Diagnóstico Comercial Inteligente")
st.write("Responde estas preguntas y descubre el portafolio ideal para el cliente.")

# =========================
# PREGUNTAS OPTIMIZADAS
# =========================
preguntas = [
    ("¿Cómo manejas hoy el dinero de tu negocio?",
     ["No llevo control","Anoto lo básico (ingresos y gastos)","Uso un sistema o software","Tengo reportes claros y los reviso"]),
    ("¿Cómo está tu contabilidad actualmente?",
     ["No la tengo organizada","Está incompleta o atrasada","Está al día","Está al día y bien analizada"]),
    ("¿Tienes claro si tu negocio realmente está ganando dinero?",
     ["No tengo idea","Tengo una idea general","Sí, con números básicos","Sí, con datos claros y confiables"]),
    ("¿Sabes cuánto dinero vas a tener en los próximos meses?",
     ["No lo sé","Solo veo lo que tengo hoy","Tengo una idea aproximada","Lo tengo proyectado y controlado"]),
    ("¿Cómo tomas decisiones importantes en tu negocio?",
     ["Por intuición","Con información incompleta","Con reportes financieros","Con análisis y apoyo profesional"]),
    ("¿Qué es lo que más necesitas hoy en tu negocio?",
     ["Poner orden","Cumplir con obligaciones","Tener más control","Crecer y tomar mejores decisiones"]),
    ("¿Qué nivel de análisis manejas actualmente?",
     ["No hago análisis","Solo reviso ingresos y gastos","Analizo rentabilidad","Analizo indicadores y tendencias"]),
    ("¿Cómo es tu negocio hoy?",
     ["Muy simple","Tiene una sola línea de ingresos","Tiene varias líneas o servicios","Es complejo y en crecimiento"]),
    ("¿Qué tipo de apoyo te gustaría tener?",
     ["Solo ayuda con impuestos","Ayuda para organizar el negocio","Seguimiento mensual","Acompañamiento estratégico"]),
    ("¿Cuál es tu prioridad en este momento?",
     ["Ordenar el negocio","Evitar errores o sanciones","Mejorar resultados","Hacer crecer el negocio"])
]

respuestas = []

st.divider()

for i, (pregunta, opciones) in enumerate(preguntas):
    r = st.radio(pregunta, opciones, key=i)
    respuestas.append(opciones.index(r))

st.divider()

# =========================
# BOTÓN DE EVALUACIÓN
# =========================
if st.button("🔍 Evaluar cliente"):

    nivel_score = (respuestas[0] + respuestas[4] + respuestas[6]) / 3

    if nivel_score < 1:
        nivel = "CONTABLE"
    elif nivel_score < 2:
        nivel = "GESTIÓN EMPRESARIAL"
    else:
        nivel = "DIRECCIÓN EMPRESARIAL"

    if respuestas[1] <= 1 and respuestas[3] <= 1:
        momento = "Setup"
    elif respuestas[3] >= 2:
        momento = "Upsell"
    else:
        momento = "Setup"

    portafolio = f"{nivel} ({momento})"

    # 🔧 FIX: guardar en session_state
    st.session_state["portafolio"] = portafolio
    st.session_state["respuestas"] = respuestas
    st.session_state["nivel"] = nivel

    st.success(f"📌 Portafolio recomendado: {portafolio}")

    st.markdown("### 🧠 Diagnóstico del cliente")
    if nivel == "CONTABLE":
        st.write("El negocio no tiene control financiero claro ni estructura organizada.")
    elif nivel == "GESTIÓN EMPRESARIAL":
        st.write("El negocio tiene información, pero no suficiente control ni seguimiento.")
    else:
        st.write("El negocio ya tiene base y necesita dirección estratégica para crecer.")

    st.markdown("### ⚠️ Hallazgos clave")
    hallazgos = []
    if respuestas[0] <= 1: hallazgos.append("Falta control del dinero")
    if respuestas[3] <= 1: hallazgos.append("No hay claridad sobre el futuro financiero")
    if respuestas[4] <= 1: hallazgos.append("Las decisiones no se basan en datos")
    if respuestas[6] <= 1: hallazgos.append("Bajo nivel de análisis del negocio")

    if hallazgos:
        for h in hallazgos:
            st.write(f"- {h}")
    else:
        st.write("El cliente tiene una base sólida de control.")

    st.markdown("### 💬 Argumento sugerido")
    if nivel == "CONTABLE":
        st.write("Hoy tu negocio no tiene una base clara de control...")
    elif nivel == "GESTIÓN EMPRESARIAL":
        st.write("Tu negocio ya tiene información...")
    else:
        st.write("Tu negocio ya tiene estructura...")

    # Guardar lead
    data = {
        "fecha": datetime.now(),
        "portafolio": portafolio,
        "respuestas": str(respuestas)
    }
    df = pd.DataFrame([data])
    try:
        df.to_csv("leads.csv", mode="a", header=False, index=False)
    except:
        df.to_csv("leads.csv", index=False)

    st.info("✅ Cliente guardado correctamente")

# 🔧 FIX: mostrar resultado persistente aunque se presione IA
if "portafolio" in st.session_state:
    st.markdown("## 📊 Resultado actual")
    st.success(f"📌 {st.session_state['portafolio']}")

# =========================
# 🤖 CONSULTOR IA (GROQ)
# =========================
st.divider()
st.markdown("## 🤖 Consultor IA para el asesor")

try:
    from openai import OpenAI
    import os

    groq_api = os.environ.get("GROQ_API_KEY")

    if not groq_api:
        st.warning("⚠️ Falta configurar GROQ_API_KEY")
    else:
        client = OpenAI(
            api_key=groq_api,
            base_url="https://api.groq.com/openai/v1"
        )

        pregunta_ia = st.text_input("Escribe la duda del cliente")

        if st.button("Consultar IA"):

            if not pregunta_ia:
                st.warning("Escribe una pregunta")
            else:
                # 🔧 FIX: usar session_state
                contexto = "Eres un asesor financiero experto en ventas. Cliente clasificado como " + str(st.session_state.get("portafolio","")) + ". Respuestas: " + str(st.session_state.get("respuestas","")) + ". Tu objetivo es cerrar la venta. Explica problema, riesgo, solución y beneficio de forma clara y persuasiva."

                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": contexto},
                            {"role": "user", "content": pregunta_ia}
                        ]
                    )

                    respuesta = response.choices[0].message.content

                    st.success("💬 Respuesta IA")
                    st.write(respuesta)

                except Exception as e:
                    st.error("❌ Error con Groq")
                    st.code(str(e))

except Exception as e:
    st.error("❌ Error inicializando IA")
    st.code(str(e))
