# Dejar las historias publicándose solas (GitHub Actions)

Son 10 minutos, una sola vez. Después se publica una historia por día hábil sin
que toques nada, sin depender de tu computadora.

## 1. Crear la cuenta de GitHub

Entrá a [github.com](https://github.com) → **Sign up**. Con el mail y una
contraseña alcanza. Es gratis.

## 2. Crear el repositorio

1. Arriba a la derecha, el **+** → **New repository**.
2. Nombre: `glm-historias`.
3. Elegí **Public**. Tiene que ser público para que Instagram pueda descargar las
   imágenes. El token NO va acá: se guarda aparte, cifrado (paso 4).
4. **Create repository**.

## 3. Subir los archivos

1. En el repositorio vacío, clic en **uploading an existing file**.
2. Descomprimí el zip que te pasé y arrastrá **todo lo que está adentro de la
   carpeta `auto-ig`** (no la carpeta en sí): `generar.py`, `publicar.py`,
   `contenidos.json`, las carpetas `assets`, `fonts` y `.github`, etc.
3. Abajo, **Commit changes**.

> Si al arrastrar no aparece la carpeta `.github`, subila aparte: es la que
> contiene la automatización. En Windows puede estar oculta.

## 4. Guardar el token

1. En el repositorio: **Settings** → menú izquierdo **Secrets and variables** →
   **Actions**.
2. Botón **New repository secret**.
3. Name: `IG_ACCESS_TOKEN`
4. Secret: pegá el token que generaste en el panel de Meta.
5. **Add secret**.

Desde acá el token queda cifrado. No se ve en el repositorio, no aparece en los
registros y yo tampoco lo veo.

## 5. Probar

1. Pestaña **Actions** → si pide confirmación, **I understand my workflows, go
   ahead and enable them**.
2. En la lista de la izquierda, **Historia diaria de Instagram**.
3. **Run workflow** → en el campo que dice simular escribí `true` → **Run
   workflow**.
4. Esperá un minuto y abrí la ejecución. Si termina en verde y el último paso
   dice *todo listo: no se publicó nada*, la conexión funciona.

Después repetí el paso dejando el campo en `false`: eso publica la historia de
verdad. Mirá el Instagram de la aseguradora para confirmarlo.

## 6. Listo

A partir de ahí se publica sola de lunes a viernes a las 9:45 de Argentina.

Para cambiar el horario, editá el archivo
`.github/workflows/historia-diaria.yml`: la línea `cron: "45 12 * * 1-5"` está en
hora UTC, que son 3 horas más que la de Argentina.

## Mantenimiento

| Cada cuánto | Qué hacer |
| --- | --- |
| Cada 50 días | Renovar el token. El sistema te abre un aviso en la pestaña **Issues** con los pasos. |
| Cuando quieras | Agregar contenidos nuevos editando `contenidos.json` desde la web de GitHub. |
| Nunca | El resto. |

## Cómo agregar una historia nueva

En el repositorio, clic en `contenidos.json` → el ícono del lápiz → agregá un
bloque como este antes del `]` final, y **Commit changes**:

```json
,
{
  "id": "16-nuevo-tema",
  "volanta": "Coberturas",
  "titulo": "Un título\ncorto",
  "texto": "Una explicación breve.",
  "tema": "salvia"
}
```

Los temas disponibles son `salvia`, `crema` y `oscuro`.
