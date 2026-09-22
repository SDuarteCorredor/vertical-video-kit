# Correrlo sin Claude Code, sin Codex y sin pagar nada

**La respuesta corta: este kit no necesita ninguna IA para funcionar.**

Los scripts son Python y Node normales. Lo único que hace un agente de IA es
*escribirte los textos y editar los dos archivos por ti*. Eso lo puedes hacer
tú a mano en cinco minutos, o pedírselo gratis a cualquier chat de IA y pegar
el resultado.

Este documento es para la persona que se sienta frente a un computador donde no
hay nada instalado y no va a pagar una suscripción.

> English: [`NO-AGENT.md`](NO-AGENT.md) · Prompts listos para copiar:
> [`PROMPTS.es.md`](PROMPTS.es.md)

---

## 1. Qué hay que instalar (esto sí es obligatorio)

Da igual qué IA uses o si no usas ninguna. El kit necesita tres cosas:

| | Para qué | Cuesta |
|---|---|---|
| **Node 18 o más** | renderizar el video (Remotion) | gratis |
| **FFmpeg** | medir el audio, pegar las pausas, codificar el MP4 | gratis |
| **Python 3.9 o más** | los scripts de voz, subtítulos y publicación | gratis |

Y tres paquetes de Python: `edge-tts` (la voz), `faster-whisper` (los
subtítulos) y `yt-dlp` (descargas, solo si vas a cortar un video largo).

### La forma fácil: un solo comando

Abre una terminal, ponte donde quieras guardar el proyecto y:

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
cd vertical-video-kit
```

**En Windows** (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**En macOS o Linux:**

```bash
bash setup.sh
```

El script revisa qué falta, te pregunta antes de instalar cada cosa, y al final
imprime un reporte. Si instala Node o FFmpeg en Windows, **cierra la terminal y
abre una nueva** antes de seguir — así es como Windows se entera de que existen.

> ¿No tienes `git`? Entra a la página del repositorio en GitHub, botón verde
> **Code → Download ZIP**, y descomprímelo. Es exactamente lo mismo.

### Si prefieres instalarlas tú

<details>
<summary><b>Windows</b></summary>

```powershell
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Python.Python.3.12
# cierra la terminal, abre una nueva, y:
pip install edge-tts faster-whisper yt-dlp
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# si no tienes Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install node ffmpeg python
pip3 install edge-tts faster-whisper yt-dlp
```
</details>

<details>
<summary><b>Linux (Debian / Ubuntu)</b></summary>

```bash
sudo apt update
sudo apt install -y nodejs npm ffmpeg python3 python3-pip python3-venv
# el nodejs de apt suele estar viejo; si `node -v` dice menos de 18:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 22

pip3 install edge-tts faster-whisper yt-dlp
```

Si `pip3` responde *externally-managed-environment*, usa un entorno virtual —
`setup.sh` lo hace solo:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install edge-tts faster-whisper yt-dlp
```

Ojo: hay que correr `source .venv/bin/activate` **en cada terminal nueva**.
</details>

Para verificar que quedó todo:

```bash
python skills/vertical-video/scripts/doctor.py
```

---

## 2. Hacer el video

Hay tres caminos. Todos llegan al mismo MP4.

### Camino A — el asistente (recomendado si nunca has usado una terminal)

```bash
python skills/vertical-video/scripts/wizard.py
```

Te hace cinco preguntas — cómo se llama la carpeta, qué acento quieres, y las
frases de la locución — y de ahí en adelante hace todo solo: crea el proyecto,
genera la voz, saca los subtítulos y, si le dices que sí, renderiza el video.

No participa ninguna IA. Tú escribes las frases.

### Camino B — a mano, editando dos archivos

```bash
python skills/vertical-video/scripts/new_project.py mi-video
cd mi-video
```

Ahora abre la carpeta `mi-video` en cualquier editor de texto — el Bloc de
notas sirve, [VS Code](https://code.visualstudio.com) es gratis y más cómodo.

**Solo se tocan dos archivos.** El resto es la maquinaria.

| Archivo | Qué es |
|---|---|
| `script.json` | lo que se **dice** en voz alta |
| `src/content.ts` | lo que se **ve** en pantalla |

Son textos distintos a propósito. La pantalla aguanta fragmentos sueltos; la
voz necesita frases completas. Escribir uno y copiarlo al otro es la razón
número uno por la que un video suena a máquina leyendo una diapositiva.

`script.json` se ve así — cambia `voice` por el acento que quieras y reemplaza
los textos:

```json
{
  "engine": "edge",
  "voice": "es-CO-SalomeNeural",
  "lang": "es",
  "scenes": [
    { "id": "01-hook",  "text": "Tu primera frase, la que hace que no pasen de largo." },
    { "id": "02-point", "text": "La segunda idea, en una frase completa." },
    { "id": "03-cta",   "text": "Lo que quieres que hagan después de ver esto." }
  ]
}
```

Voces gratis que suenan bien, según el país de tu audiencia:

| País | Mujer | Hombre |
|---|---|---|
| Colombia | `es-CO-SalomeNeural` | `es-CO-GonzaloNeural` |
| México | `es-MX-DaliaNeural` | `es-MX-JorgeNeural` |
| Argentina | `es-AR-ElenaNeural` | `es-AR-TomasNeural` |
| España | `es-ES-ElviraNeural` | `es-ES-AlvaroNeural` |
| Estados Unidos (inglés) | `en-US-AriaNeural` | `en-US-AndrewNeural` |

Usa el acento del país al que le hablas. Un video para Colombia narrado en
español de España suena importado y distrae más de lo que uno creería.

En `src/content.ts` los `id` tienen que ser **los mismos** que en
`script.json` — así se encuentran la locución, los tiempos y los subtítulos.

Después:

```bash
python scripts/voice.py        # genera la voz y mide cuánto dura cada escena
python scripts/captions.py     # subtítulos palabra por palabra
npm run dev                    # vista previa en vivo, se abre en el navegador
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, ya codificado para subir
```

Cambiaste una frase? Vuelve a correr `voice.py` y `captions.py`. La escena se
reajusta sola. Eso es todo lo que cuesta una corrección aquí.

### Camino C — que una IA gratis te escriba los textos

Abre [`PROMPTS.es.md`](PROMPTS.es.md), copia el prompt del guion, pégalo en
**cualquier** chat gratuito — ChatGPT, Claude, Gemini, Copilot, DeepSeek, el
que sea — contesta lo que te pregunte, y te devuelve el `script.json` y el
`content.ts` listos. Los pegas en los archivos y sigues con el Camino B.

Esto funciona sin instalar nada y sin pagar nada, porque el chat solo escribe
texto: quien hace el video es tu computador.

---

## 3. ¿Y los agentes de código? ¿Cuál es gratis?

Un agente (Claude Code, Codex CLI…) hace el Camino B por ti: edita los
archivos y corre los comandos sin que tú los escribas. Es cómodo, **no es
necesario**.

| Herramienta | ¿Gratis? | Qué hace falta |
|---|---|---|
| **Sin IA** | sí | nada. El asistente del Camino A o los dos archivos a mano |
| **Cualquier chat web** | sí | una cuenta gratis. Copias y pegas ([`PROMPTS.es.md`](PROMPTS.es.md)) |
| **Codex CLI** (OpenAI) | **sí, con límites** | cuenta gratis de ChatGPT. `npm i -g @openai/codex` |
| **Gemini CLI** (Google) | **sí** | cuenta de Google. ~1.000 peticiones al día |
| **GitHub Copilot** | plan gratuito limitado | cuenta de GitHub, dentro de VS Code |
| **Claude Code** | **no** | plan pago de Claude (Pro desde ~US$20/mes) o créditos de API |

### Respondiendo directo a tus dos preguntas

**¿Se puede instalar usando Codex?** Sí. Codex CLI lee el archivo
[`AGENTS.md`](../AGENTS.md) que está en la raíz de este repositorio, que es el
estándar abierto que también entienden Cursor, opencode, Copilot y Windsurf.
Clona el repo, entra con `codex` y pídele lo que quieras en español.

**¿Codex solo funciona pagando?** No. Codex CLI entra con una cuenta **gratuita**
de ChatGPT; el plan gratis alcanza para tareas de código cortas y locales, que
es exactamente el tamaño de lo que hay que hacer aquí. Pagar (Plus, ~US$20/mes)
sube los límites de uso y agrega las funciones en la nube, pero no hace falta
para usar este kit.

**Claude Code sí es de pago.** El plan gratuito de Claude no lo incluye: hay que
tener Pro, Max, Team o Enterprise, o cargar créditos de API. Por eso el kit
funciona igual sin él.

### Instalarlos

```bash
# Codex CLI — gratis con cuenta de ChatGPT
npm install -g @openai/codex
codex          # la primera vez te pide iniciar sesión en el navegador

# Gemini CLI — gratis con cuenta de Google
npm install -g @google/gemini-cli
gemini
```

Gemini CLI busca `GEMINI.md` por defecto. Para que lea el `AGENTS.md` de este
repo, crea `.gemini/settings.json` dentro del repositorio con:

```json
{ "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
```

Y con Claude Code, si alguien sí lo tiene pago:

```
/plugin marketplace add SDuarteCorredor/vertical-video-kit
/plugin install vertical-video-kit
```

---

## 4. Cuando algo sale mal

| Lo que ves | Qué pasó |
|---|---|
| `'python' no se reconoce` | Windows: reinstala Python marcando **Add python.exe to PATH**, o usa `py` en vez de `python` |
| `FFmpeg is missing` | No quedó en el PATH. Cierra la terminal y abre una nueva. Si sigue, reinstálalo |
| `VoiceStudio is not answering` | Estás usando el motor `voicestudio` sin tener la app abierta. Pon `"engine": "edge"` en `script.json` |
| `edge-tts is missing` | `pip install edge-tts` |
| Los subtítulos salen vacíos | Falta `faster-whisper`. `pip install faster-whisper`. La primera vez se baja el modelo y demora |
| `node -v` dice menos de v18 | Remotion necesita 18+. Instala una versión actual desde [nodejs.org](https://nodejs.org) |
| `externally-managed-environment` | Usa un entorno virtual: `python3 -m venv .venv && source .venv/bin/activate` |
| El texto queda tapado por TikTok | Pon `SHOW_SAFE_AREAS = true` en `src/theme.ts` y mira dónde cae. Ver [`design.md`](../skills/vertical-video/references/design.md) |
| El render se demora muchísimo | Es normal la primera vez: Remotion baja un Chromium. Después es más rápido |

Para revisar un video que ya existe y entender qué está mal:

```bash
python skills/vertical-video/scripts/diagnose.py mi-video.mp4
```

---

## 5. Lo mínimo que hay que saber para que no salga feo

Tres cosas, y son las que más se rompen:

**Los primeros dos segundos.** Un video de 40 segundos que arranca mal no es un
video de 40 segundos, es uno de 2. La primera frase tiene que abrir una pregunta
en la cabeza de quien mira. "En este video les voy a contar sobre..." es una
despedida.

**Nada importante abajo ni a la derecha.** TikTok y Reels tapan los ~380 px de
abajo y los ~160 px de la derecha con su propia interfaz. Texto ahí no es "un
poco apretado": es invisible.

**Los subtítulos no son un adorno.** La mayoría de la gente ve el feed sin
sonido. Si no hay subtítulos, no hay mensaje.

Lo demás está escrito en detalle en
[`skills/vertical-video/references/`](../skills/vertical-video/references/) —
ganchos, voz, subtítulos, diseño y videos corporativos.
