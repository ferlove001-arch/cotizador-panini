import streamlit as st
import csv
import re

# 1. Configuración de la página web
st.set_page_config(page_title="Cotizador Panini", page_icon="⚽", layout="centered")
st.title("⚽ Cotizador Panini 2026")
st.markdown("Pega la lista de WhatsApp para cruzarla con el inventario en tiempo real.")

# 2. Cargar inventario desde el CSV
archivo_maestro = "Inventario_Panini_Mundial_2026 - Inventario_Master-2.csv"

# st.cache_data guarda el Excel en la memoria para que la web cargue rapidísimo
@st.cache_data
def cargar_inventario(ruta):
    inv = {}
    try:
        with open(ruta, mode='r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                id_e = fila['ID de la estampa'].strip().upper()
                try:
                    stock = int(fila['Stock actual'])
                    precio_str = fila['Precio MXN'].replace('$', '').replace(',', '').strip()
                    precio = float(precio_str)
                except ValueError:
                    stock = 0
                    precio = 0.0
                inv[id_e] = {'stock': stock, 'precio': precio, 'tipo': fila['Tipo de casilla']}
    except Exception:
        return None
    return inv

inventario = cargar_inventario(archivo_maestro)

# 3. Interfaz Visual
if not inventario:
    st.error("⚠️ No se encontró el archivo de inventario.")
else:
    # Cuadro de texto bonito
    texto_whatsapp = st.text_area("📦 Lista del cliente:", height=150, placeholder="Ej: MEX 1, FWC 2, 5, 8...")

    # Botón de acción
    if st.button("Generar Cotización 🚀"):
        if not texto_whatsapp.strip():
            st.warning("Pega una lista primero.")
        else:
            total_mxn = 0
            disponibles, agotadas, no_encontradas = [], [], []
            
            # El "Lector Inteligente" con memoria
            lista_inteligente = []
            prefijo_actual = ""
            for e in texto_whatsapp.split(","):
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
                if estampa in inventario:
                    datos = inventario[estampa]
                    if datos['stock'] > 0:
                        total_mxn += datos['precio']
                        disponibles.append(f"✅ {estampa} ({datos['tipo']}) -> ${datos['precio']} MXN")
                    else:
                        agotadas.append(f"❌ {estampa} -> AGOTADA")
                else:
                    no_encontradas.append(f"❓ {estampa} -> Error / No existe")

            # 4. Mostrar el Dashboard en la Web
            st.divider()
            st.subheader("📊 Dashboard Operativo")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total a Cobrar", value=f"${total_mxn} MXN")
            with col2:
                st.metric(label="Piezas Disponibles", value=len(disponibles))

            if disponibles:
                st.success("\n".join(disponibles))
            if agotadas:
                st.warning("⚠️ **SIN STOCK:**\n" + "\n".join(agotadas))
            if no_encontradas:
                st.error("🔍 **REVISIÓN MANUAL:**\n" + "\n".join(no_encontradas))

            # 5. El cuadro mágico para WhatsApp
            st.divider()
            st.subheader("📲 Mensaje para WhatsApp")
            if total_mxn > 0:
                mensaje = f"¡Hola! Ya crucé tu lista gigante con mi inventario de hoy. 🤩\nTe conseguí {len(disponibles)} estampas.\n"
                if agotadas or no_encontradas:
                    mensaje += f"(Solo me faltaron {len(agotadas) + len(no_encontradas)} que ya se me agotaron).\n"
                mensaje += f"\nEl total te queda en *${total_mxn} MXN*.\n\n¿Te armo tu paquete para coordinar la entrega?"
                
                # Esto genera un cuadro negro con un botón de "Copiar" automático en la esquina
                st.code(mensaje, language="text")
            else:
                st.info("¡Hola! Ya revisé el inventario, pero justo esas se me agotaron hoy. ¡Te aviso en cuanto me surtan!")
