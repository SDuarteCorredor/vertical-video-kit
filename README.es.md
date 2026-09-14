# vertical-video-kit

Haz TikToks, Reels y Shorts con código — locución que no suena a robot,
subtítulos palabra por palabra y un render real de 1080×1920.

Pensado para agentes de código (Claude Code, Cursor y cualquiera que lea
skills), pero todos los scripts funcionan solos desde la terminal.

<p align="center">
  <img src="docs/preview-hook.png" width="240" alt="Escena de gancho">
  <img src="docs/preview-list.png" width="240" alt="Escena de lista">
  <img src="docs/preview-stat.png" width="240" alt="Escena de dato">
</p>

## Por qué

Editar un video en una línea de tiempo hace que cada corrección sea rehacer
todo a mano. Por eso las correcciones no se hacen, y los videos salen con
errores que nadie quiso arreglar.

Aquí el contenido vive separado del diseño. Cambiar una frase de la locución
es editar una línea y volver a correr un script: la voz se regenera, la escena
cambia de duración sola, la animación se re-sincroniza y los subtítulos siguen.

Tres problemas que resuelve de verdad:

- **TTS que suena a TTS.** Casi siempre es el texto, no el motor. Cada línea
  se normaliza para el oído antes de llegar a la voz — siglas deletreadas,
  símbolos expandidos, puntuación que marca el ritmo — y puedes poner pausas
  reales con `[pause:0.4]`. El motor por defecto corre local y gratis.
- **Subtítulos puestos al final.** Se generan del audio que realmente se
  renderizó, así que el resaltado cae sobre la palabra que se está diciendo.
  El layout les reserva su franja desde el principio.
- **Texto debajo de la interfaz de la plataforma.** TikTok e Instagram tapan
  los ~380px de abajo y los ~160px de la derecha. La plantilla lo sabe, y
  puedes encender una capa para verlo.

## Instalación

**Como skills de agente** — funciona con 75+ agentes vía
[skills.sh](https://skills.sh):

```bash
npx skills add SDuarteCorredor/vertical-video-kit
```

**Como plugin de Claude Code:**

```
/plugin marketplace add SDuarteCorredor/vertical-video-kit
/plugin install vertical-video-kit
```

**O simplemente clónalo** y corre los scripts a mano:

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
cd vertical-video-kit
python skills/vertical-video/scripts/doctor.py --install
```

## Para empezar

```bash
python skills/vertical-video/scripts/new_project.py mi-video
cd mi-video

# escribe script.json (lo que se dice) y src/content.ts (lo que se ve)

python scripts/voice.py        # locución + duración de cada escena
python scripts/captions.py     # subtítulos palabra por palabra
npm run dev                    # vista previa en vivo
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, codificado para las plataformas
```

## Qué trae

| | |
|---|---|
| `skills/vertical-video` | Guion → voz → subtítulos → render. La principal. |
| `skills/clip-cutter` | Video horizontal largo → clips verticales con subtítulos quemados |
| `skills/reference-research` | Desarma un video que funciona y reutiliza su estructura |
| `template/remotion-vertical` | El proyecto Remotion 9:16 que copia `new_project.py` |

Los `SKILL.md` están escritos para que también los lea una persona. Las reglas
de diseño, los patrones de gancho y el oficio de la voz están en
`skills/vertical-video/references/` (en inglés).

## Motores de voz

Se elige con `"engine"` en `script.json`. Intercambiables, misma interfaz.

| Motor | Costo | Calidad | Necesita |
|---|---|---|---|
| `voicestudio` | gratis | la mejor, y clona voces | [VoiceStudio](https://github.com/debpalash/VoiceStudio) corriendo local |
| `edge` | gratis | decente, se nota sintética | `pip install edge-tts` |
| `openai` | pago | muy natural | `OPENAI_API_KEY` |
| `elevenlabs` | pago | la mejor comercial | `ELEVENLABS_API_KEY` |

El de por defecto es local y gratis, y nada sale de la máquina.

**Para español:** usa el acento del país de la audiencia. Un video para
Colombia narrado en español de España suena importado y distrae más de lo que
uno esperaría.

## Requisitos

- **Node 18+** y **FFmpeg** — obligatorios
- **Python 3.9+** — para los scripts
- `pip install edge-tts faster-whisper yt-dlp` — voz de respaldo, subtítulos,
  descargas

`python skills/vertical-video/scripts/doctor.py --install` revisa todo e
instala lo que puede.

## Construido sobre

[Remotion](https://github.com/remotion-dev/remotion) para renderizar ·
[VoiceStudio](https://github.com/debpalash/VoiceStudio) para la voz local ·
[Whisper](https://github.com/openai/whisper) vía
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) para subtítulos ·
[FFmpeg](https://ffmpeg.org) ·
[yt-dlp](https://github.com/yt-dlp/yt-dlp)

Remotion es gratis para personas y equipos pequeños, pero
[pide licencia de empresa](https://remotion.dev/license) por encima de ese
umbral. Lo demás es gratis.

## Úsalo con cabeza

Descarga solo lo que tengas derecho a usar. Clona solo tu propia voz, o una
para la que tengas permiso explícito. No pongas cifras, promesas ni
afirmaciones que nadie verificó.

## Licencia

MIT. Ver [LICENSE](LICENSE).
