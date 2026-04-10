import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
from docx import Document

def rastreador_diputacion_final():
    # 1. Configuración de archivos
    directorio = os.path.dirname(os.path.abspath(__file__))
    fecha_hoy_str = datetime.now().strftime("%d_%m_%Y")
    nombre_word = os.path.join(directorio, f"Diputacion_Coruna_{fecha_hoy_str}.docx")
    
    print(f"\n--- 🏛️ VIGILANCIA FILTRADA: DIPUTACIÓN (BOE) + RRHH (BOP/DOG) ---")

    # DEFINICIÓN DE FILTROS
    entidad_cast = "diputación provincial de a coruña"
    entidad_gal = "deputación da coruña"
    
    # Términos de Recursos Humanos (Castellano y Gallego)
    rrhh_terminos = ["recursos humanos", "rrhh", "recursos humans", "oferta de empleo", "oferta de emprego", "proceso selectivo"]

    doc = Document()
    doc.add_heading(f'Alertas Diputación A Coruña - {datetime.now().strftime("%d/%m/%Y")}', 0)
    
    anuncios_finales = []
    hoy = datetime.now()

    # Rango de 4 días
    for i in range(4):
        fecha = hoy - timedelta(days=i)
        f_str = fecha.strftime("%d/%m/%Y")
        
        urls = {
            "BOE": fecha.strftime("https://www.boe.es/boe/dias/%Y/%m/%d/index.php?s=2B"),
            "BOE": fecha.strftime("https://www.boe.es/boe/dias/%Y/%m/%d/index.php?s=2A"),
            "BOP Coruña": f"https://bop.dacoruna.gal/bopportal/cambioBoletin.do?fechaInput={f_str}",
            "DOG": f"https://www.xunta.gal/diario-oficial-galicia/mostrarContenido.do?ruta=/{fecha.year}/{fecha.strftime('%Y%m%d')}/Secciones3_gl.html"
        }

        print(f"🔎 Revisando {f_str}...", end="\r")

        for fuente, url in urls.items():
            try:
                res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                if res.status_code != 200: continue

                sopa = BeautifulSoup(res.text, 'lxml')
                
                for item in sopa.find_all(['li', 'p', 'tr', 'td']):
                    texto = item.get_text(separator=" ").strip()
                    if len(texto) < 40: continue
                    txt_min = texto.lower()

                    encontrado = False

                    # LÓGICA DIFERENCIADA POR FUENTE:
                    if fuente == "BOE":
                        # En el BOE: Solo que mencione a la Diputación
                        if entidad_cast in txt_min or entidad_gal in txt_min:
                            encontrado = True
                    else:
                        # En BOP y DOG: Entidad + Término de RRHH (Doble validación)
                        tiene_entidad = (entidad_cast in txt_min or entidad_gal in txt_min)
                        tiene_rrhh = any(r in txt_min for r in rrhh_terminos)
                        if tiene_entidad and tiene_rrhh:
                            encontrado = True

                    if encontrado:
                        if not any(a['texto'] == texto for a in anuncios_finales):
                            anuncios_finales.append({
                                'texto': texto, 
                                'fuente': fuente, 
                                'fecha': f_str, 
                                'url': url
                            })
            except:
                continue

    # 3. Guardado
    if anuncios_finales:
        for a in anuncios_finales:
            p = doc.add_paragraph()
            p.add_run(f"📌 {a['fuente']} - {a['fecha']}").bold = True
            doc.add_paragraph(a['texto'])
            doc.add_paragraph(f"🔗 {a['url']}")
            doc.add_paragraph("-" * 30)
        
        doc.save(nombre_word)
        print(f"\n✅ ¡Hecho! {len(anuncios_finales)} resultados guardados.")
    else:
        print("\nℹ️ Sin novedades con estos filtros en los últimos 7 días.")

if __name__ == "__main__":
    rastreador_diputacion_final()
