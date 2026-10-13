#!/bin/bash
# Historia del dia para Grupo Loinaz Martinez Seguros.
# Se ejecuta de lunes a viernes por cron. Ver README.md.
cd "$(dirname "$0")" || exit 1
[ -f .env ] && set -a && . ./.env && set +a
python3 generar.py && python3 publicar.py
