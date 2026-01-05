import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor Regalikos", layout="wide")

# --- ESTILOS CSS PARA EL FONDO VERDE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0f2f6; }
    .pedido-listo { background-color: #d4edda; border-radius: 10px; padding: 20px; border: 1px solid #c3e6cb; margin-bottom: 10px; }
    .pedido-pendiente { background-color: #ffffff; border-radius: 10px; padding: 20px; border: 1px solid #e6e6e6; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_stdio=True)

st.title("📦 Control de Producción y Recolección")

uploaded_file = st.file_uploader("Sube el CSV de pedidos", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Name'] = df['Name'].ffill()
    
    # --- 1. LÓGICA DE DETECCIÓN DE EXTRAS MEJORADA ---
    palabras_extras = ["extra de productos", "embalaje", "2 unidad", "toploader", "sobre personalizado", "base de lampara"]
    
    def es_extra(nombre):
        nombre = str(nombre).lower()
        return any(p in nombre for p in palabras_extras)

    df['es_extra'] = df['Lineitem name'].apply(es_extra)

    # --- 2. CONTEO DE PRODUCTOS TOTALES (RESUMEN ARRIBA) ---
    # Filtramos para no contar el embalaje como producto en el resumen
    df_resumen = df[~df['Lineitem name'].str.contains("Embalaje", case=False)]
    resumen = df_resumen.groupby('Lineitem name')['Lineitem quantity'].sum().sort_values(ascending=False)

    with st.expander("📊 RESUMEN DE PRODUCCIÓN TOTAL", expanded=False):
        cols = st.columns(3)
        for i, (nombre, cant) in enumerate(resumen.items()):
            cols[i % 3].write(f"**{cant}x** {nombre}")

    st.divider()

    # --- 3. LISTADO DE PEDIDOS ---
    pedidos_unicos = df['Name'].unique()

    for pedido in pedidos_unicos:
        items_pedido = df[df['Name'] == pedido]
        
        # Estado del pedido en session_state
        if f"done_{pedido}" not in st.session_state:
            st.session_state[f"done_{pedido}"] = False

        # Clase CSS según estado
        clase_fondo = "pedido-listo" if st.session_state[f"done_{pedido}"] else "pedido-pendiente"
        
        with st.container():
            st.markdown(f'<div class="{clase_fondo}">', unsafe_allow_stdio=True)
            
            col_info, col_btn = st.columns([3, 1])
            
            with col_info:
                st.subheader(f"📋 Pedido {pedido}")
                
                checks_listo = []
                for idx, row in items_pedido.iterrows():
                    nombre = row['Lineitem name']
                    cant = row['Lineitem quantity']
                    tipo_extra = row['es_extra']
                    
                    # Generamos un checkbox para cada item (principal o extra)
                    label = f"{nombre} (x{cant})"
                    if tipo_extra:
                        # Sangría para extras
                        check = st.checkbox(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ {label}", key=f"chk_{pedido}_{idx}")
                    else:
                        check = st.checkbox(f"**🟢 {label}**", key=f"chk_{pedido}_{idx}")
                    
                    checks_listo.append(check)

            with col_btn:
                st.write("###")
                # El botón solo se activa si todos los checks anteriores son True
                todo_marcado = all(checks_listo)
                
                if st.session_state[f"done_{pedido}"]:
                    st.success("✅ EMPAQUETADO")
                    if st.button("Deshacer", key=f"undo_{pedido}"):
                        st.session_state[f"done_{pedido}"] = False
                        st.rerun()
                else:
                    btn_label = "EMPAQUETAR" if todo_marcado else "Faltan productos..."
                    if st.button(btn_label, key=f"btn_{pedido}", disabled=not todo_marcado):
                        st.session_state[f"done_{pedido}"] = True
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_stdio=True)

else:
    st.info("Sube el archivo CSV para empezar.")
