import streamlit as st
import csv
import re
import os


st.set_page_config(page_title="Cotizador Panini", page_icon="⚽", layout="centered")
st.title("⚽ Cotizador Panini 2026")
st.markdown("Pega la lista de WhatsApp para cruzarla con el inventario en tiempo real.")

archivo_maestro = "Inventario_Panini_Mundial_2026 - Inventario_Master-2.csv"


@st.cache_data
def cargar_inventario(ruta):
    inv = {}
    if not os.path.exists(ruta):
        st.error(f"⚠️ El archivo '{ruta}' no fue encontrado en GitHub.")
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
        st.error(f" Error al leer el CSV: {e}")
        return None
    return inv

inventario = cargar_inventario(archivo_maestro)


if inventario:
    texto_whatsapp = st.text_area("Lista del cliente:", height=150, placeholder="Ej: MEX 1\nFWC 2 y 5\n...")

    if st.button("Generar Cotización "):
        if not texto_whatsapp.strip():
            st.warning("Por favor, pega una lista primero.")
        else:
            total_mxn = 0
            disponibles, agotadas, no_encontradas = [], [], []
            
            
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

            
            for estampa in lista_inteligente:
               
                estampa = estampa.replace("FRAN ", "FRA ")
                
                if estampa in inventario:
                    datos = inventario[estampa]
                    if datos['stock'] > 0:
                        total_mxn += datos['precio']
                        disponibles.append(f"✅ {estampa} ({datos['tipo']}) -> ${datos['precio']} MXN")
                    else:
                        agotadas.append(f"❌ {estampa} -> AGOTADA")
                else:
                    no_encontradas.append(f"❓ {estampa} -> Revisión Manual")

        
            st.divider()
            st.subheader("Dashboard Operativo")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total a Cobrar", value=f"${total_mxn:.2f} MXN")
            with col2:
                st.metric(label="Piezas Disponibles", value=len(disponibles))

            if disponibles: st.success("\n\n".join(disponibles))
            if agotadas: st.warning("⚠️ **SIN STOCK:**\n\n" + "\n\n".join(agotadas))
            if no_encontradas: st.error("**REVISIÓN MANUAL:**\n\n" + "\n\n".join(no_encontradas))

            
            st.divider()
            st.subheader("Mensaje para WhatsApp")
            if total_mxn > 0:
                mensaje = (f"¡Hola! Ya crucé tu lista con mi inventario de hoy. 🤩\n"
                           f"Te conseguí {len(disponibles)} estampas.\n")
                if agotadas or no_encontradas:
                    mensaje += f"(Solo me faltaron {len(agotadas) + len(no_encontradas)} que ya se me agotaron).\n"
                mensaje += f"\nEl total te queda en *${total_mxn:.2f} MXN*.\n\n¿Te armo tu paquete para coordinar la entrega?"
                st.code(mensaje, language="text")
            else:
                st.info("¡Hola! Ya revisé, pero justo esas se me agotaron. ¡Te aviso en cuanto me surtan!")
