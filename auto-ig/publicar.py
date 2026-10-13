#!/usr/bin/env python3
"""
Publicador de historias de Instagram para Grupo Loinaz Martinez Seguros.

Flujo (API de publicacion de contenido de Instagram):
  1. Sube la imagen generada a un hosting publico (la API exige una URL publica).
  2. Crea un contenedor con media_type=STORIES.
  3. Espera a que el contenedor quede listo y publica.

Credenciales: NUNCA se escriben en este archivo. Se leen de variables de entorno.

    IG_USER_ID       id de la cuenta de Instagram profesional
    IG_ACCESS_TOKEN  token de acceso con instagram_basic + instagram_content_publish
    IMGBB_API_KEY    (opcional) clave del hosting de imagenes
    HOSTING_BASE_URL (opcional) si subis las imagenes a tu propio servidor

Uso:
    python3 publicar.py                      -> publica la imagen de ultima.txt
    python3 publicar.py --imagen ruta.png    -> publica una imagen puntual
    python3 publicar.py --simular            -> hace todo menos publicar
"""

import argparse
import os
import pathlib
import sys
import time

import requests

BASE = pathlib.Path(__file__).resolve().parent
API = "https://graph.facebook.com/v23.0"
LOG = BASE / "registro.log"


def log(mensaje):
    linea = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {mensaje}"
    print(linea)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(linea + "\n")


def entorno(nombre, obligatoria=True):
    valor = os.environ.get(nombre, "").strip()
    if obligatoria and not valor:
        log(f"[error] falta la variable de entorno {nombre}")
        sys.exit(1)
    return valor


def subir_imagen(ruta):
    """Devuelve una URL publica de la imagen. La API de Instagram la descarga de ahi."""
    base_propia = os.environ.get("HOSTING_BASE_URL", "").strip()
    if base_propia:
        # Variante para servidor propio: la imagen ya quedo servida por el sitio.
        destino = pathlib.Path(os.environ["HOSTING_DIR"]) / ruta.name
        destino.write_bytes(ruta.read_bytes())
        url = f"{base_propia.rstrip('/')}/{ruta.name}"
        log(f"[ok] imagen disponible en {url}")
        return url

    clave = entorno("IMGBB_API_KEY")
    respuesta = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": clave, "expiration": 86400},
        files={"image": ruta.read_bytes()},
        timeout=90,
    )
    respuesta.raise_for_status()
    url = respuesta.json()["data"]["url"]
    log(f"[ok] imagen subida: {url}")
    return url


def crear_contenedor(ig_user_id, token, image_url):
    respuesta = requests.post(
        f"{API}/{ig_user_id}/media",
        data={"image_url": image_url, "media_type": "STORIES", "access_token": token},
        timeout=60,
    )
    datos = respuesta.json()
    if "id" not in datos:
        log(f"[error] no se pudo crear el contenedor: {datos}")
        sys.exit(1)
    log(f"[ok] contenedor creado: {datos['id']}")
    return datos["id"]


def esperar_contenedor(contenedor, token, intentos=12, espera=5):
    for i in range(intentos):
        datos = requests.get(
            f"{API}/{contenedor}",
            params={"fields": "status_code,status", "access_token": token},
            timeout=30,
        ).json()
        estado = datos.get("status_code")
        if estado == "FINISHED":
            return True
        if estado == "ERROR":
            log(f"[error] el contenedor fallo: {datos}")
            return False
        log(f"[...] contenedor {estado or 'sin estado'} ({i + 1}/{intentos})")
        time.sleep(espera)
    log("[error] el contenedor nunca quedo listo")
    return False


def publicar(ig_user_id, token, contenedor):
    datos = requests.post(
        f"{API}/{ig_user_id}/media_publish",
        data={"creation_id": contenedor, "access_token": token},
        timeout=60,
    ).json()
    if "id" not in datos:
        log(f"[error] no se pudo publicar: {datos}")
        sys.exit(1)
    log(f"[ok] historia publicada: {datos['id']}")
    return datos["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagen", help="ruta de la imagen a publicar")
    ap.add_argument("--simular", action="store_true", help="no publica, solo prueba")
    args = ap.parse_args()

    if args.imagen:
        ruta = pathlib.Path(args.imagen)
    else:
        marcador = BASE / "ultima.txt"
        if not marcador.exists():
            log("[error] no hay imagen generada; ejecutá primero generar.py")
            sys.exit(1)
        ruta = pathlib.Path(marcador.read_text(encoding="utf-8").strip())

    if not ruta.exists():
        log(f"[error] no existe la imagen {ruta}")
        sys.exit(1)

    ig_user_id = entorno("IG_USER_ID")
    token = entorno("IG_ACCESS_TOKEN")

    url = subir_imagen(ruta)
    contenedor = crear_contenedor(ig_user_id, token, url)
    if not esperar_contenedor(contenedor, token):
        sys.exit(1)

    if args.simular:
        log("[simulacion] todo listo: no se publico nada")
        return
    publicar(ig_user_id, token, contenedor)


if __name__ == "__main__":
    sys.exit(main())
