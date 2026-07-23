import io
import zipfile
import pandas as pd
import qrcode
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Generador Masivo de QR", page_icon="📱", layout="centered")

st.title("📱 Generador Masivo de Códigos QR")
st.write("Sube tu archivo Excel, elige la columna con los datos y descarga todos tus QR en un archivo ZIP con fondo transparente.")

# 1. Carga del archivo Excel
uploaded_file = st.file_uploader("Carga tu archivo Excel (.xlsx o .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("¡Archivo cargado correctamente!")
        
        # 2. Selección de la columna
        column = st.selectbox("Selecciona la columna que contiene los datos para el QR:", df.columns)
        
        if column:
            # Mostrar vista previa de los datos
            st.write("**Vista previa de los datos seleccionados:**")
            st.dataframe(df[[column]].dropna().head(5))
            
            # Opción de color para los módulos del QR
            qr_color = st.color_picker("Elige el color del código QR:", "#000000")
            
            if st.button("🚀 Generar Códigos QR", type="primary"):
                # Crear buffer en memoria para el archivo ZIP
                zip_buffer = io.BytesIO()
                
                # Filtrar valores vacíos y convertir a lista
                data_list = df[column].dropna().astype(str).tolist()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, item in enumerate(data_list):
                        # Generar el código QR
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_M,
                            box_size=10,
                            border=2,
                        )
                        qr.add_data(item)
                        qr.make(fit=True)
                        
                        # Crear imagen base
                        img = qr.make_image(fill_color=qr_color, back_color="white").convert("RGBA")
                        
                        # Convertir el fondo blanco en transparente
                        datas = img.getdata()
                        new_data = []
                        for pixel in datas:
                            # Si el píxel es blanco (o casi blanco), hacerlo transparente
                            if pixel[0] > 220 and pixel[1] > 220 and pixel[2] > 220:
                                new_data.append((255, 255, 255, 0))
                            else:
                                new_data.append(pixel)
                        img.putdata(new_data)
                        
                        # Guardar imagen PNG en memoria
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format="PNG")
                        
                        # Limpiar el nombre del archivo para evitar caracteres inválidos
                        clean_filename = "".join(c for c in item if c.isalnum() or c in (" ", "_", "-")).rstrip()
                        if not clean_filename:
                            clean_filename = f"qr_{idx+1}"
                        
                        # Añadir al ZIP
                        zip_file.writestr(f"{clean_filename}.png", img_byte_arr.getvalue())
                        
                        # Actualizar barra de progreso
                        progress = (idx + 1) / len(data_list)
                        progress_bar.progress(progress)
                        status_text.text(f"Generando {idx + 1} de {len(data_list)} QRs...")
                
                status_text.success("¡Generación completada con éxito!")
                
                # Botón de descarga del ZIP
                st.download_button(
                    label="📦 Descargar todos los QR (.zip)",
                    data=zip_buffer.getvalue(),
                    file_name="codigos_qr_transparentes.zip",
                    mime="application/zip",
                )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")