import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Pedidos - Sublimación", layout="wide")

st.title("📦 Panel de Control de Producción")

# 1. Carga de archivo
uploaded_file = st.file_uploader("Sube el CSV de pedidos", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Filtrar solo columnas necesarias para no saturar la vista
    columnas_interes = ['Name', 'Lineitem name', 'Lineitem quantity']
    df_pedidos = df[columnas_interes].copy()

    # Identificar extras (Lógica solicitada)
    palabras_extras = ["extra de productos", "embalaje", "2 unidad al 45%"]
    
    def es_extra(nombre):
        nombre = str(nombre).lower()
        return any(palabra in nombre for palabra in palabras_extras)

    # Agrupar por Pedido
    pedidos_unicos = df_pedidos['Name'].unique()

    st.sidebar.metric("Pedidos Pendientes", len(pedidos_unicos))

    for pedido in pedidos_unicos:
        with st.expander(f"📋 Pedido {pedido}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            items_pedido = df_pedidos[df_pedidos['Name'] == pedido]
            
            with col1:
                for _, row in items_pedido.iterrows():
                    nombre_item = row['Lineitem name']
                    cantidad = row['Lineitem quantity']
                    
                    if not es_extra(nombre_item):
                        # PRODUCTO PRINCIPAL
                        st.markdown(f"**🟢 {nombre_item}** (x{cantidad})")
                    else:
                        # EXTRA
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*↳ {nombre_item}* (x{cantidad})")
            
            with col2:
                # Controles de estado digitales
                st.checkbox("🖨️ Diseño Impreso", key=f"imp_{pedido}")
                st.checkbox("📦 Empaquetado", key=f"pack_{pedido}")

else:
    st.info("Por favor, sube el archivo CSV exportado para empezar a trabajar.")
