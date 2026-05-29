import streamlit as st
import csv
import re
import os

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y PESTAÑA
# ==========================================
st.set_page_config(page_title="Panini Tracker Pro", page_icon="🏆", layout="centered")

# --- INYECCIÓN DE CSS PARA DISEÑO PREMIUM ---
st.markdown("""
    <style>
    /* Ocultar menú de Streamlit por defecto para que se vea como app propia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Colores y tipografía de los títulos */
    h1 {
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: -10px;
    }
    
    /* Estilo del Botón Principal */
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Diseño de los números del Dashboard */
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        color: #1E3A8A;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CABECERA Y BRANDING VISUAL
# ==========================================
col1, col2 = st.columns([1, 4])
with col1:
    # Si subes tu logo.png a GitHub, cambia el enlace por "logo.png"
    # Por ahora, usamos un ícono de trofeo premium genérico temporal
    st.image("https://cdn-icons-png.flaticon.com/512/3113/3113054.png", width=70) 
with col2:
    st.title("Panini Tracker Pro")
    st.caption("⚡️ Motor Inteligente de Cotización y Logística")

st.divider()

# ==========================================
# 3. LÓGICA DEL INVENTARIO (Tu motor intacto)
# ==========================================
archivo_maestro = "Inventario_Panini_Mundial_2026 - Inventario_Master-2.csv"

@st.cache_data
def cargar_inventario(ruta):
    inv = {}
    if not os.path.exists(ruta):
        st.error(f"⚠️ Archivo de base de datos no detectado.")
        return None
    try:
        with open(ruta, mode='r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            lector.fieldnames = [name.strip() for name in lector.fieldnames] if lector.fieldnames else []
            for fila in lector:
                id_e = fila.get('ID de la estampa', '').strip().upper()
                if not id_e: continue
                try:
                    stock = int(fila.get('Stock actual', 0))
                    precio_str = fila.get('Precio MXN', '0').replace('$', '').replace(',', '').strip()
                    precio = float(precio_str)
                except ValueError:
                    stock, precio = 0, 0.0
                inv[id_e] = {'stock': stock, 'precio': precio, 'tipo': fila.get('Tipo de casilla', 'Regular')}
    except Exception as e:
        return None
    return inv

inventario = cargar_inventario(archivo_maestro)

# ==========================================
# 4. INTERFAZ OPERATIVA DE LA APP
# ==========================================
if inventario:
    st.markdown("### 📥 Recepción de Pedidos")
    texto_whatsapp = st.text_area("Pega aquí la lista enviada por el cliente:", height=120, placeholder="Ej: MEX 1, FWC 2 y 5...")

    if st.button("PROCESAR COTIZACIÓN 🚀"):
        if not texto_whatsapp.strip():
            st.warning("⚠️ El campo está vacío. Pega una lista para procesar.")
        else:
            total_mxn = 0
            disponibles, agotadas, no_encontradas = [], [], []
            
            # La Licuadora de Texto
            texto_limpio = texto_whatsapp.replace('\n', ',').replace(' y ', ',').replace(' Y ', ',').replace('-', ',')

            lista_inteligente = []
            prefijo_actual = ""
            for e in texto_limpio.split(","):
                e = e.strip().upper()
                if not e: continue
                
                letras = re.search(r'[A-Z]+', e)
                numeros = re.search(r'\d+', e)
                
                if letras:
                    prefijo_actual = letras.group()
                
                if numeros and prefijo_actual:
                    lista_inteligente.append(f"{prefijo_actual} {numeros.group()}")
                else:
                    lista_inteligente.append(e)

            # Cruce de datos
            for estampa in lista_inteligente:
                estampa = estampa.replace("FRAN ", "FRA ")
                
                if estampa in inventario:
                    datos = inventario[estampa]
                    if datos['stock'] > 0:
                        total_mxn += datos['precio']
                        disponibles.append(f"✅ {estampa} -> ${datos['precio']} MXN")
                    else:
                        agotadas.append(f"❌ {estampa} -> AGOTADA")
                else:
                    no_encontradas.append(f"❓ {estampa} -> Inválida")

            # Despliegue de Resultados (Estilo Dashboard)
            st.divider()
            st.markdown("### 📊 Panel de Resultados")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total Autorizado", value=f"${total_mxn:.2f} MXN")
            with col2:
                st.metric(label="Piezas Separadas", value=len(disponibles))

            # Diseño de las listas
            if disponibles: 
                with st.expander("✅ Ver piezas listas para entrega", expanded=True):
                    st.write("\n\n".join(disponibles))
            if agotadas: 
                with st.expander("⚠️ Ver piezas sin stock actual"):
                    st.write("\n\n".join(agotadas))
            if no_encontradas: 
                with st.expander("🔍 Ver errores de lectura"):
                    st.write("\n\n".join(no_encontradas))

            # Mensaje final pulido
            st.divider()
            st.markdown("### 📲 Mensaje de Cierre (Copia y pega)")
            if total_mxn > 0:
                mensaje = (f"¡Hola! Ya procesé tu lista en mi sistema. 🤖\n"
                           f"Te logré apartar {len(disponibles)} estampas exactas.\n")
                if agotadas or no_encontradas:
                    mensaje += f"(Solo faltaron {len(agotadas) + len(no_encontradas)} que volaron en rutas anteriores).\n"
                mensaje += f"\nTu total cerrado es de *${total_mxn:.2f} MXN*.\n\n¿Me confirmas para armar tu paquete y coordinar la entrega en CUGS? 🚀"
                st.code(mensaje, language="text")
            else:
                st.info("¡Hola! Ya revisé el sistema, pero justo esas piezas se me agotaron hoy. ¡Te aviso en cuanto se actualice el inventario!")
