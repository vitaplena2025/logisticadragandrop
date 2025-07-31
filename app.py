import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit.components.v1 import html

st.set_page_config(page_title="Planificador de Rutas", layout="wide")
st.title("📋 Planificador de Rutas con Drag & Drop")

# 1️⃣ Sube tu Excel maestro
master_up = st.file_uploader("Sube tu Excel maestro", type=["xlsx","xls"])
if not master_up:
    st.stop()

# Leemos el maestro
df_master = pd.read_excel(master_up)
# Ajusta este nombre si tu columna ID es distinta
ID_COL = st.selectbox("Columna identificadora de facturas", df_master.columns, index=0)
items = df_master[ID_COL].astype(str).tolist()

# 2️⃣ Define los choferes (hasta 7)
st.subheader("Define los choferes")
default_drivers = ["Arnaldo","Pepo","Eliezer","Joselito","Luillo","Alexander","Chofer7"]
driver_names = []
for i in range(7):
    name = st.text_input(f"Chofer #{i+1}", default_drivers[i])
    driver_names.append(name or f"Chofer{i+1}")

# 3️⃣ Construye el HTML + SortableJS
list_items = "\n".join(
    f'<li data-key="{idx}">{items[idx]}</li>'
    for idx in range(len(items))
)
driver_divs = "\n".join(
    f'<div style="flex:1; min-width:150px; margin:5px;">'
    f'  <h4>{driver_names[i]}</h4>'
    f'  <ul id="route{i}" class="list"></ul>'
    f'</div>'
    for i in range(len(driver_names))
)

html_code = f"""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"/>
<style>
  .list {{ list-style:none; padding:0; min-height:200px; border:1px dashed #ccc; }}
  .list li {{ padding:8px; margin:4px; background:#f8f9fa; border:1px solid #ddd; cursor:grab; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>

<div class="container-fluid">
  <div class="row">
    <div class="col-3">
      <h4>Pool</h4>
      <ul id="pool" class="list">
        {list_items}
      </ul>
    </div>
    <div class="col-9 d-flex flex-wrap">
      {driver_divs}
    </div>
  </div>
  <button id="saveBtn" class="btn btn-primary mt-3">Guardar asignación</button>
</div>

<script>
  const group = {{ name:'shared', pull:true, put:true }};
  Sortable.create(pool, {{ group, animation:150 }});
  { "".join(f"Sortable.create(route{i}, {{ group, animation:150 }});\n" for i in range(len(driver_names))) }

  document.getElementById('saveBtn').onclick = () => {{
    const result = {{}};
    result['pool'] = Array.from(pool.children).map(li => li.dataset.key);
    { "".join(f"result['route{i}'] = Array.from(route{i}.children).map(li => li.dataset.key);\n" for i in range(len(driver_names))) }
    window.parent.postMessage({{ type:'ROUTES', data: result }}, '*');
  }};
</script>
"""

resp = html(html_code, height=600)

# 4️⃣ Cuando recibimos la asignación, la mostramos y permitimos exportar
if resp and isinstance(resp, dict) and resp.get("type") == "ROUTES":
    assigns = resp["data"]  # contiene 'pool' y 'route0'...'route6'
    
    st.subheader("✅ Asignación de facturas")
    dfs = {}
    
    # Pool restante
    pool_keys = [int(k) for k in assigns["pool"]]
    df_pool = df_master.iloc[pool_keys]
    st.markdown("**Pool restante**")
    st.dataframe(df_pool)
    dfs["Pool"] = df_pool
    
    # Rutas por chofer
    for i, name in enumerate(driver_names):
        keys = [int(k) for k in assigns[f"route{i}"]]
        df_route = df_master.iloc[keys]
        dfs[name] = df_route
        st.markdown(f"**Ruta: {name}**")
        st.dataframe(df_route)
    
    # 5️⃣ Descargar Excel final
    if st.button("📥 Descargar Excel de rutas"):
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            for sheet_name, df in dfs.items():
                # Excel limita los nombres de hoja a 31 caracteres
                safe_name = sheet_name[:31]
                df.to_excel(writer, sheet_name=safe_name, index=False)
        buf.seek(0)
        st.download_button(
            "⬇️ Descargar archivo de rutas",
            data=buf,
            file_name="rutas_asignadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
