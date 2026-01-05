import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Gestor Regalikos", layout="wide")

# --- CSS CORREGIDO ---
st.markdown("""
    <style>
    /* Estilo para los botones de empaquetar */
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; font-weight: bold; }
    /* Ajuste de márgenes para los checkboxes */
    .stCheckbox { margin-bottom: -15px; }
    /* Estilo para los productos principales */
    .prod-principal { color: #2e7d32; font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 Control de Producción y Recolección")

uploaded_file = st.file_uploader("Sube el CSV de pedidos", type="csv")

if uploaded_file:
    # 1. CARGA Y LIMPIEZA
    df = pd.read_csv(uploaded_file)
    df['Name'] = df['Name'].ffill()
    
    # 2. IDENTIFICACIÓN DE EXTRAS (Ajustada a tu feedback)
    # Ahora incluimos explícitamente "Extras de productos" y "TopLoader"
    palabras_extras = ["extra de productos", "embalaje", "2 unidad", "toploader", "sobre personalizado", "base de lampara"]
    
    def es_extra(nombre):
        n = str(nombre).lower()
        return any(p in n for p in palabras_extras)

    df['es_extra'] = df['Lineitem name'].apply(es_extra)

    # 3. RESUMEN DE CARGA (Conteo total arriba)
    # Filtramos el "Embalaje" para que no ensucie la lista de producción
    df_resumen = df[~df['Lineitem name'].str.contains("Embalaje", case=False)]
    conteo_total = df_resumen.groupby('Lineitem name')['Lineitem quantity'].sum().sort_values(ascending=False)

    with st.expander("📊 RESUMEN DE MATERIAL TOTAL (Hoy)", expanded=True):
        col_res1, col_res2, col_res3 = st.columns(3)
        for i, (nombre, cant) in enumerate(conteo_total.items()):
            col = [col_res1, col_res2, col_res3][i % 3]
            col.write(f"**{int(cant)}x** {nombre}")

    st.divider()

    # 4. LISTADO DE PEDIDOS
    pedidos = df['Name'].unique()

    for ped_id in pedidos:
        items = df[df['Name'] == ped_id]
        
        # Estado de empaquetado en memoria
        if f"listo_{ped_id}" not in st.session_state:
            st.session_state[f"listo_{ped_id}"] = False

        # Contenedor con borde para cada pedido
        with st.container(border=True):
            
            # Cabecera dinámica: Si está empaquetado, se vuelve verde (st.success)
            if st.session_state[f"listo_{ped_id}"]:
                st.success(f"✅ PEDIDO {ped_id} - EMPAQUETADO Y LISTO")
            else:
                st.subheader(f"📋 Pedido {ped_id}")

            col_lista, col_accion = st.columns([3, 1])
            
            with col_lista:
                item_checks = []
                for idx, row in items.iterrows():
                    nombre = row['Lineitem name']
                    cantidad = row['Lineitem quantity']
                    es_item_extra = row['es_extra']
                    
                    key_check = f"chk_{ped_id}_{idx}"
                    
                    # Renderizado según tipo de producto
                    if es_item_extra:
                        # Extras: con sangría (↳) y sin color verde
                        c = st.checkbox(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ {nombre} (x{cantidad})", key=key_check)
                    else:
                        # Principales: En negrita y con círculo verde
                        c = st.checkbox(f"**🟢 {nombre}** (x{cantidad})", key=key_check)
                    
                    item_checks.append(c)

            with col_accion:
                st.write("###") # Espaciador
                
                # Lógica del botón: se activa solo si TODOS los items están marcados
                todo_marcado = all(item_checks)
                
                if st.session_state[f"listo_{ped_id}"]:
                    if st.button("⏪ Deshacer", key=f"undo_{ped_id}"):
                        st.session_state[f"listo_{ped_id}"] = False
                        st.rerun()
                else:
                    # El botón está bloqueado (disabled) hasta que marques todo
                    label_btn = "EMPAQUETAR" if todo_marcado else "Faltan items..."
                    # Si todo está marcado, el botón se vuelve azul (primary)
                    if st.button(label_btn, key=f"btn_{ped_id}", 
                                 disabled=not todo_marcado, 
                                 type="primary" if todo_marcado else "secondary"):
                        st.session_state[f"listo_{ped_id}"] = True
                        st.rerun()
else:
    st.info("Sube el archivo CSV de pedidos para empezar el control.")
