import os
import re
import subprocess
import imageio_ffmpeg
import streamlit as st
from pytubefix import YouTube

# --- DISEÑO DE LA INTERFAZ WEB ---
st.set_page_config(page_title="Descargador de YouTube HD", page_icon="🎥")

st.title("🎥 Descargador de Videos HD")
st.write("Pega el enlace de cualquier video de YouTube. El sistema procesará la mejor calidad disponible y te dará un botón para guardarlo.")

# Caja de texto para que el usuario pegue la URL
url = st.text_input("Enlace del video de YouTube:")

# Botón para iniciar el proceso
if st.button("Procesar Video"):
    if url:
        # st.spinner muestra una "ruedita de carga" mientras el código trabaja
        with st.spinner('Conectando con YouTube y fusionando HD... (esto puede tardar unos minutos)'):
            try:
                yt = YouTube(url)
                titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", yt.title)
                
                # Descargamos pistas
                video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
                audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
                
                video_stream.download(filename="temp_video.mp4")
                audio_stream.download(filename="temp_audio.mp4")
                
                archivo_final = f"{titulo_limpio}.mp4"
                ruta_ffmpeg_seguro = imageio_ffmpeg.get_ffmpeg_exe()
                
                comando = [
                    ruta_ffmpeg_seguro, '-y', '-i', 'temp_video.mp4', '-i', 'temp_audio.mp4', 
                    '-c:v', 'copy', '-c:a', 'aac', archivo_final
                ]
                
                proceso = subprocess.run(comando, capture_output=True, text=True)
                
                if proceso.returncode == 0:
                    # Borramos temporales
                    os.remove("temp_video.mp4")
                    os.remove("temp_audio.mp4")
                    
                    st.success(f"¡Video procesado con éxito: {titulo_limpio}!")
                    
                    # --- EL BOTÓN DE DESCARGA PARA EL USUARIO ---
                    with open(archivo_final, "rb") as file:
                        st.download_button(
                            label="⬇️ Guardar Video en mi Computadora",
                            data=file,
                            file_name=archivo_final,
                            mime="video/mp4"
                        )
                        
                else:
                    st.error(f"Error interno al procesar el video. Detalles: {proceso.stderr}")
                    
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")
    else:
        st.warning("Por favor, ingresa un enlace válido primero.")