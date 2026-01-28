name: Buscador Diputacion Coruña

on:
  schedule:
    - cron: '30 8 * * 1-6' # Se ejecuta a las 8:30 AM de Lunes a Sábado
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Descargar codigo
        uses: actions/checkout@v3

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Instalar librerias
        run: pip install requests beautifulsoup4 python-docx

      - name: Ejecutar buscador Diputacion
        run: python buscador_diputacion.py

      - name: Enviar Email
        if: always()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 465
          secure: true
          username: ${{ secrets.EMAIL_USER }}
          password: ${{ secrets.EMAIL_PASS }}
          subject: "🏛️ Alerta Diputación Coruña"
          to: ${{ secrets.EMAIL_USER }}
          from: "Buscador Diputación"
          body: "Se adjunta el boletín de la Diputación de A Coruña."
          attachments: "Diputacion_Coruna_*.docx"
