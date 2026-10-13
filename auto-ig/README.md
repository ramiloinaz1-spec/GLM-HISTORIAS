# Historias automáticas · Grupo Loinaz Martinez Seguros

Sistema que genera y publica una historia de Instagram por día hábil, con la
identidad visual de la marca, sin intervención manual.

## Qué hace cada archivo

| Archivo | Para qué sirve |
|---|---|
| `contenidos.json` | El banco de contenidos. **Es el único archivo que vas a querer tocar.** |
| `generar.py` | Arma la imagen 1080×1920 del día con la plantilla de la marca. |
| `publicar.py` | Sube la imagen y la publica como historia por la API de Instagram. |
| `ejecutar_diario.sh` | Ejecuta los dos pasos. Es lo que corre el programador. |
| `.env.ejemplo` | Modelo del archivo de credenciales. |
| `assets/` | Logo vectorizado, isotipo e imágenes de marca. |
| `fonts/` | Tipografías (Zilla Slab, Oswald, Work Sans). |
| `salida/` | Las imágenes generadas. |
| `registro.log` | Historial de publicaciones y errores. |

---

## Configuración inicial (una sola vez)

### 1. La cuenta de Instagram tiene que ser profesional

Solo las cuentas de empresa pueden publicar historias por la API. En la app:
**Configuración → Tipo de cuenta → Cambiar a cuenta profesional**, y vinculala a
una página de Facebook de la aseguradora.

### 2. Crear la app en Meta

1. Entrá a `developers.facebook.com` con el usuario que administra la página.
2. Creá una app de tipo **Negocios**.
3. Agregá el producto **Instagram** / **Instagram Graph API**.
4. Pedí los permisos `instagram_basic` e `instagram_content_publish`.

### 3. Obtener el token y el ID de la cuenta

- El **token** conviene que sea de *usuario del sistema* desde el Business
  Manager: no vence. Un token común de usuario vence a los 60 días y hay que
  renovarlo a mano.
- El **ID de la cuenta de Instagram** lo obtenés con el Explorador de la API
  de Graph consultando la página vinculada.

> **Importante:** el token es una llave de acceso a la cuenta. No lo pegues en
> un chat, ni en un mail, ni dentro de estos archivos. Va únicamente en el
> archivo `.env`, que queda en el servidor.

### 4. Cargar las credenciales

```bash
cp .env.ejemplo .env
# editá .env y completá IG_USER_ID, IG_ACCESS_TOKEN e IMGBB_API_KEY
chmod 600 .env
```

`IMGBB_API_KEY` es de un hosting gratuito de imágenes: la API de Instagram
exige que la imagen esté en una URL pública para poder descargarla. Si preferís
tu propio servidor, usá `HOSTING_BASE_URL` y `HOSTING_DIR` en lugar de esa clave.

### 5. Instalar dependencias

```bash
pip install pillow playwright requests
playwright install chromium
```

### 6. Probar sin publicar

```bash
python3 generar.py --indice 0        # genera una historia de muestra
python3 publicar.py --imagen salida/historia_01-franquicia.png --simular
```

Si el simulacro llega hasta "todo listo", la configuración está bien.

### 7. Programar la ejecución diaria

**Linux / macOS** (`crontab -e`), de lunes a viernes a las 9:40:

```
40 9 * * 1-5 /ruta/a/auto-ig/ejecutar_diario.sh >> /ruta/a/auto-ig/cron.log 2>&1
```

**Windows:** Programador de tareas → Crear tarea básica → Diariamente →
ejecutar `ejecutar_diario.sh` con Git Bash o convertirlo a `.bat`.

La computadora o el servidor tienen que estar encendidos a esa hora.

---

## Uso diario

Ninguno. El sistema solo:

1. Toma el siguiente contenido de `contenidos.json` (rota en orden y vuelve a
   empezar al terminar la lista).
2. Genera la imagen con la plantilla de la marca.
3. La publica como historia.
4. Lo registra en `registro.log`.

## Para cambiar los contenidos

Editá `contenidos.json`. Cada historia es un bloque así:

```json
{
  "id": "16-nuevo-tema",
  "volanta": "Coberturas",
  "titulo": "Un título\nen dos líneas",
  "texto": "Texto explicativo, breve.",
  "pie": "Escribinos",
  "tema": "salvia"
}
```

- `tema`: `salvia` (verde claro), `crema` (fondo claro) u `oscuro` (verde oscuro).
- `titulo`: usá `\n` para cortar las líneas donde quieras. El tamaño de letra se
  ajusta solo para que nunca se desborde.
- `texto` y `pie` son opcionales.

## Límites que conviene conocer

- Las historias publicadas por API **no admiten stickers interactivos**
  (encuestas, preguntas, enlaces, cuenta regresiva). Si querés usarlos, esa
  historia hay que subirla a mano.
- No se pueden agregar a Destacadas por API: eso se hace desde la app.
- Las historias duran 24 horas, como cualquier otra.
- Hay un tope de 50 publicaciones por API cada 24 horas, muy por encima de una
  por día.

## Si algo falla

Mirá `registro.log`. Los errores más comunes:

| Mensaje | Causa |
|---|---|
| `falta la variable de entorno` | El `.env` no está cargado o está incompleto. |
| `no se pudo crear el contenedor` | Token vencido, o la cuenta no es profesional. |
| `el contenedor nunca quedo listo` | La URL de la imagen no era accesible públicamente. |
