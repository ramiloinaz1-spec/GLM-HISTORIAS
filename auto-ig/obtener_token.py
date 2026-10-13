#!/usr/bin/env python3
"""
Obtiene el token de acceso de Instagram y lo guarda en el archivo .env.

Camino usado: Instagram API con inicio de sesion de Instagram (no requiere
pagina de Facebook).

Antes de ejecutarlo necesitas:
  1. El Instagram App ID y el App Secret (panel de desarrolladores).
  2. El codigo de autorizacion, que sale de abrir esta direccion en el navegador
     y copiar lo que aparece despues de code= en la barra de direcciones
     (sin el #_ final):

     https://www.instagram.com/oauth/authorize
        ?client_id=TU_APP_ID
        &redirect_uri=https://localhost/
        &scope=instagram_business_basic,instagram_business_content_publish
        &response_type=code

El codigo vale una hora y se usa una sola vez.
Nada de lo que escribas se muestra en pantalla ni sale de esta computadora.
"""

import getpass
import pathlib
import sys

import requests

BASE = pathlib.Path(__file__).resolve().parent
ENV = BASE / ".env"
REDIRECT = "https://localhost/"


def guardar_env(valores):
    """Escribe o actualiza claves en .env sin perder lo que ya estaba."""
    lineas = {}
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.strip().startswith("#"):
                clave, _, valor = linea.partition("=")
                lineas[clave.strip()] = valor
    lineas.update(valores)
    ENV.write_text(
        "\n".join(f"{k}={v}" for k, v in lineas.items()) + "\n", encoding="utf-8"
    )
    ENV.chmod(0o600)


def main():
    print("Configuracion del token de Instagram\n")
    app_id = input("Instagram App ID: ").strip()
    app_secret = getpass.getpass("Instagram App Secret (no se muestra): ").strip()
    codigo = getpass.getpass("Codigo de autorizacion (no se muestra): ").strip()
    codigo = codigo.removesuffix("#_")

    print("\n[1/4] Canjeando el codigo por un token de corta duracion...")
    r = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT,
            "code": codigo,
        },
        timeout=60,
    )
    datos = r.json()
    if "access_token" not in datos:
        print(f"[error] {datos}")
        print("Revisa el App ID, la clave secreta y que el codigo no este vencido.")
        sys.exit(1)
    corto = datos["access_token"]

    print("[2/4] Cambiandolo por el token de 60 dias...")
    r = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": app_secret,
            "access_token": corto,
        },
        timeout=60,
    )
    datos = r.json()
    if "access_token" not in datos:
        print(f"[error] {datos}")
        sys.exit(1)
    largo = datos["access_token"]
    dias = int(datos.get("expires_in", 0)) // 86400

    print("[3/4] Consultando el ID de la cuenta...")
    r = requests.get(
        "https://graph.instagram.com/v23.0/me",
        params={"fields": "id,username", "access_token": largo},
        timeout=60,
    )
    cuenta = r.json()
    if "id" not in cuenta:
        print(f"[error] {cuenta}")
        sys.exit(1)

    print("[4/4] Guardando en .env...")
    guardar_env(
        {
            "IG_APP_SECRET": app_secret,
            "IG_ACCESS_TOKEN": largo,
            "IG_USER_ID": cuenta["id"],
        }
    )

    print(f"\nListo. Cuenta conectada: @{cuenta.get('username', '?')}")
    print(f"El token vence en unos {dias} dias y se renueva solo en cada publicacion.")
    print("Probá ahora:  python3 generar.py --indice 0 && python3 publicar.py --simular")


if __name__ == "__main__":
    sys.exit(main())
