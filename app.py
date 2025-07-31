import streamlit as st
import pandas as pd
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Drag & Drop to Excel", layout="wide")
st.title("📋 Arrastra y suelta para definir el orden")

# Lista base (puede venir de tu Excel maestro)
items = ["SKU-001","SKU-002","SKU-003","SKU-004","SKU-005","SKU-006"]

df = pd.DataFrame({"SKU": items})

# Configurar AgGrid para drag-and-drop de filas
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(rowDrag=True)
gb.configure_grid_options(domLayout="normal")
grid_response = AgGrid(
    df,
    gridOptions=gb.build(),
    height=300,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
)

# Extraer el nuevo orden
ordered_df = pd.DataFrame(grid_response["data"])
ordered_df["Orden"] = list(range(1, len(ordered_df) + 1))

st.subheader("🔀 Orden resultante")
st.dataframe(ordered_df)

# Botón para descargar Excel
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    ordered_df[["Orden","SKU"]].to_excel(writer, index=False, sheet_name="Orden")
buffer.seek(0)

st.download_button(
    "📥 Descargar Excel",
    data=buffer,
    file_name="orden_skus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
