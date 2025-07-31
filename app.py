import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_sortable import sortable_list

st.set_page_config(page_title="Drag & Drop to Excel", layout="wide")

st.title("📋 Arrastra y suelta para definir el orden")
st.markdown("Reordena los elementos de la lista con drag-and-drop y luego descarga un Excel con ese orden.")

# 1) Define tu lista inicial (puede venir de un Excel o de código)
items = [
    "SKU-001", "SKU-002", "SKU-003", "SKU-004",
    "SKU-005", "SKU-006", "SKU-007", "SKU-008",
]

# 2) Mostrar la lista arrastrable
st.subheader("🔀 Arrastra para reordenar")
ordered = sortable_list(items, key="sortable")

# 3) Cuando el usuario quiera, genera el Excel
if st.button("📥 Generar y descargar Excel"):
    df = pd.DataFrame({
        "Orden": list(range(1, len(ordered)+1)),
        "SKU": ordered
    })
    # Escribir a Excel en memoria
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Orden")
    buffer.seek(0)
    st.download_button(
        "⬇️ Descargar Excel",
        data=buffer,
        file_name="orden_skus.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
