#!/usr/bin/env python3
"""
Generador de historias de Instagram para Grupo Loinaz Martinez Seguros.

Toma el contenido del dia desde contenidos.json y arma la imagen 1080x1920
respetando la identidad de marca (verde salvia, slab serif, arcos y logo).

Uso:
    python3 generar.py                 -> genera la historia que toca hoy
    python3 generar.py --indice 5      -> genera un contenido puntual
    python3 generar.py --todos         -> genera el banco completo (para revisar)
"""

import argparse
import base64
import json
import os
import pathlib
import sys
from datetime import date

from PIL import Image, ImageFont
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).resolve().parent
ASSETS = BASE / "assets"
FONTS = BASE / "fonts"
SALIDA = BASE / "salida"
ESTADO = BASE / "estado.json"

# --- Identidad de marca -----------------------------------------------------
SALVIA = "#8AB09B"
OSCURO = "#3A5C4C"
CREMA = "#F4F1EA"
BLANCO = "#FFFFFF"

ANCHO, ALTO = 1080, 1920
MARGEN = 110
ANCHO_UTIL = ANCHO - 2 * MARGEN  # 860

PALETAS = {
    # tema: (fondo, texto, acento, logo, arco)
    "salvia": (SALVIA, BLANCO, BLANCO, "blanco", BLANCO),
    "crema": (CREMA, OSCURO, SALVIA, "verde", SALVIA),
    "oscuro": (OSCURO, BLANCO, SALVIA, "blanco", SALVIA),
}


def b64(ruta):
    return base64.b64encode(pathlib.Path(ruta).read_bytes()).decode()


def ajustar_titulo(texto, maximo=118, minimo=64):
    """Baja el cuerpo hasta que la linea mas larga entre en el ancho util."""
    lineas = texto.split("\n")
    for tam in range(maximo, minimo - 1, -2):
        fuente = ImageFont.truetype(str(FONTS / "ZillaSlab-Bold.ttf"), tam)
        if max(fuente.getlength(l) for l in lineas) <= ANCHO_UTIL + 180:
            return tam
    return minimo


def ancho_volanta(texto, tam=28):
    fuente = ImageFont.truetype(str(FONTS / "Oswald.ttf"), tam)
    return fuente.getlength(texto) + len(texto) * tam * 0.34


def html_historia(item):
    tema = item.get("tema", "salvia")
    fondo, texto, acento, logo, arco = PALETAS[tema]
    titulo = item["titulo"]
    tam_titulo = ajustar_titulo(titulo)
    vol = item["volanta"].upper()

    fuentes = {
        "zb": b64(FONTS / "ZillaSlab-Bold.ttf"),
        "os": b64(FONTS / "Oswald.ttf"),
        "ws": b64(FONTS / "WorkSans.ttf"),
    }
    logo_b64 = b64(ASSETS / f"logo_{logo}.png")
    icono_b64 = b64(ASSETS / f"icono_{logo}.png")

    cuerpo = item.get("texto", "")
    pie = item.get("pie", "")

    return f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:Zilla;font-weight:700;src:url(data:font/ttf;base64,{fuentes['zb']})}}
@font-face{{font-family:Oswald;font-weight:200 700;src:url(data:font/ttf;base64,{fuentes['os']})}}
@font-face{{font-family:Work;font-weight:100 900;src:url(data:font/ttf;base64,{fuentes['ws']})}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{ANCHO}px;height:{ALTO}px;background:{fondo};color:{texto};
 display:flex;flex-direction:column;align-items:center;text-align:center;
 padding:220px {MARGEN}px 180px;position:relative;overflow:hidden}}
.marca{{position:absolute;left:-470px;bottom:-40px;width:1600px;opacity:.09}}
.arcos{{position:absolute;left:0;bottom:430px;opacity:.5}}
.volanta{{display:flex;align-items:center;gap:30px;width:100%;
 font-family:Oswald;font-weight:400;letter-spacing:.34em;font-size:28px;
 color:{acento};white-space:nowrap}}
.volanta:before,.volanta:after{{content:'';flex:1;height:2px;background:{acento};opacity:.9}}
h1{{font-family:Zilla;font-weight:700;font-size:{tam_titulo}px;line-height:.98;
 text-transform:uppercase;margin:120px -90px 0;width:1040px}}
p{{font-family:Work;font-weight:400;font-size:44px;line-height:1.4;margin-top:70px;
 max-width:780px;opacity:.95}}
.pie{{font-family:Oswald;font-weight:400;letter-spacing:.3em;font-size:26px;
 margin-top:56px;border:2px solid {acento};padding:22px 40px;color:{acento}}}
.logo{{width:520px;margin-top:auto}}
</style></head><body>
<img class="marca" src="data:image/png;base64,{icono_b64}">
<svg class="arcos" width="{ANCHO}" height="150" viewBox="0 0 1080 150">
<path d="M-20 140 H270 Q540 30 810 140 H1100" fill="none" stroke="{arco}" stroke-width="3"/>
<path d="M-20 105 H330 Q540 -10 750 105 H1100" fill="none" stroke="{arco}" stroke-width="3"/></svg>
<div class="volanta">{vol}</div>
<h1>{titulo.replace(chr(10), '<br>')}</h1>
{f'<p>{cuerpo}</p>' if cuerpo else ''}
{f'<div class="pie">{pie.upper()}</div>' if pie else ''}
<img class="logo" src="data:image/png;base64,{logo_b64}">
</body></html>"""


def render(items, destino=SALIDA):
    destino.mkdir(parents=True, exist_ok=True)
    generados = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(
            viewport={"width": ANCHO, "height": ALTO}, device_scale_factor=2
        )
        for item in items:
            pagina.set_content(html_historia(item))
            pagina.wait_for_timeout(350)
            tmp = destino / f"_tmp_{item['id']}.png"
            pagina.screenshot(path=str(tmp))
            imagen = Image.open(tmp).resize((ANCHO, ALTO), Image.LANCZOS)
            # PNG para compartir a mano; JPEG porque la API de Instagram solo acepta JPEG.
            imagen.save(destino / f"historia_{item['id']}.png")
            final = destino / f"historia_{item['id']}.jpg"
            imagen.convert("RGB").save(final, "JPEG", quality=92, subsampling=0)
            tmp.unlink()
            generados.append(final)
            print(f"[ok] {final.name} — {item['volanta']}")
        navegador.close()
    return generados


def cargar_contenidos():
    datos = json.loads((BASE / "contenidos.json").read_text(encoding="utf-8"))
    return datos["historias"]


def proximo_indice(total):
    """Rota el banco de contenidos sin repetir hasta agotarlo."""
    estado = {"ultimo": -1}
    if ESTADO.exists():
        estado = json.loads(ESTADO.read_text(encoding="utf-8"))
    siguiente = (estado.get("ultimo", -1) + 1) % total
    ESTADO.write_text(
        json.dumps({"ultimo": siguiente, "fecha": date.today().isoformat()}),
        encoding="utf-8",
    )
    return siguiente


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indice", type=int, help="genera un contenido puntual")
    ap.add_argument("--todos", action="store_true", help="genera el banco completo")
    args = ap.parse_args()

    historias = cargar_contenidos()
    if args.todos:
        render(historias)
        return
    if args.indice is not None:
        render([historias[args.indice % len(historias)]])
        return

    item = historias[proximo_indice(len(historias))]
    rutas = render([item])
    # El publicador lee esta ruta para subir la historia del dia.
    # Se guarda relativa a esta carpeta para que sirva tambien en GitHub Actions.
    relativa = rutas[0].relative_to(BASE)
    (BASE / "ultima.txt").write_text(str(relativa).replace("\\", "/"), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
