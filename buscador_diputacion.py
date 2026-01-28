import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
from docx import Document

def rastreador_diputacion():
    directorio = os.path.dirname(os.path.abspath(__file__))
    fecha_hoy_str = datetime.now().strftime("%d_%m_%Y")
    nombre_word = os.path.join(directorio, f"Diputacion_Coruna_{fecha_hoy_str}.docx")
    
    print(f"\n--- 🏛️ BÚSQUEDA ESPECÍFICA: DIPUTACIÓN DA CORUÑA ---")

    terminos_entidad = [r"diputación provincial de a coruña", r"deputación da coruña"]
    terminos_bases = ["convocatoria", "bases", "proceso selectivo"]

    doc = Document()
    doc.add_heading(f'Alertas Diputación A Coruña - {datetime.now().strftime("%d/%m/%Y")}', 0)
    
    anuncios_finales = []
    hoy = datetime.now()

    for i in range(7):
        fecha = hoy - timedelta(days=i)
        f_str = fecha.strftime("%d/%m/%Y")
        url = f"https://bop.dacoruna.gal/bopportal/cambioBoletin.do?fechaInput={f_str}"

        try:
            res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code != 200: continue

            # Usamos lxml para mayor precisión en boletines oficiales
            sopa = BeautifulSoup(res.text, 'lxml')
            
            for item in sopa.find_all(['li', 'p', 'tr', 'td']):
                texto = item.get_text(separator=" ").strip()
                if len(texto) < 40: continue
                
                txt_min = texto.lower()
                es_diputacion = any(re.search(t, txt_min) for t in terminos_entidad)
                es_convocatoria = any(b in txt_min for b in terminos_bases)

                if es_diputacion and es_convocatoria:
                    # Evitar duplicados exactos en el mismo día
                    if not any(a['texto'] == texto for a in anuncios_finales):
                        anuncios_finales.append({'texto': texto, 'fecha': f_str, 'url': url})
        except Exception as e:
            print(f"Error en {f_str}: {e}")
            continue

    if anuncios_finales:
        for a in anuncios_finales:
            p = doc.add_paragraph()
            p.add_run(f"📌 {a['fecha']}").bold = True
            doc.add_paragraph(a['texto'])
            doc.add_paragraph(f"🔗 {a['url']}")
            doc.add_paragraph("-" * 20)
        
        doc.save(nombre_word)
        print(f"✅ Encontrados {len(anuncios_finales)} anuncios.")
    else:
        print("ℹ️ Sin novedades esta semana.")

if __name__ == "__main__":
    rastreador_diputacion()
