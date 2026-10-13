#!/usr/bin/env python3
"""
Renueva el token de larga duracion de Instagram.

El token dura unos 60 dias y se puede renovar mientras siga vigente. Este script
se ejecuta antes de cada publicacion: si al token le quedan menos de 20 dias, lo
renueva y actualiza el .env. Asi, mientras el sistema publique, nunca vence.

No imprime el token en ningun momento.
"""

import json
import os
import pathlib
import sys
import time

import requests

BASE = pathlib.Path(__file__).resolve().parent
ENV = BASE / ".env"
MARCA = BASE / "token_estado.json"
DIAS_MINIMOS = 20


def guardar_env(valores):
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
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        print("[token] no hay IG_ACCESS_TOKEN; ejecutá obtener_token.py")
        return 1

    # Si lo renovamos hace poco, no hace falta volver a hacerlo.
    if MARCA.exists():
        estado = json.loads(MARCA.read_text(encoding="utf-8"))
        quedan = (estado.get("vence_en", 0) - time.time()) / 86400
        if quedan > DIAS_MINIMOS:
            print(f"[token] vigente, quedan {int(quedan)} días")
            return 0

    r = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=60,
    )
    datos = r.json()
    if "access_token" not in datos:
        print(f"[token] no se pudo renovar: {datos.get('error', datos)}")
        return 1

    segundos = int(datos.get("expires_in", 0))
    guardar_env({"IG_ACCESS_TOKEN": datos["access_token"]})
    MARCA.write_text(
        json.dumps({"vence_en": time.time() + segundos}), encoding="utf-8"
    )
    print(f"[token] renovado, vence en {segundos // 86400} días")
    return 0


if __name__ == "__main__":
    sys.exit(main())
