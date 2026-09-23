# Prompts listos para copiar

Dos secciones: los prompts para un **agente de código** (Claude Code, Codex
CLI, Gemini CLI, Cursor), que edita los archivos por ti, y los prompts para
**cualquier chat gratuito** (ChatGPT, Claude, Gemini, Copilot, DeepSeek), que
solo te devuelve texto para que tú lo pegues.

> English: [`PROMPTS.md`](PROMPTS.md) · Cómo correrlo sin IA:
> [`SIN-AGENTE.md`](SIN-AGENTE.md)

Reemplaza lo que está `ASÍ` por lo tuyo. Lo demás déjalo: las restricciones
raras (los 380 px de abajo, "no inventes cifras") son las que evitan el 90% de
los problemas.

---

## Parte 1 — Con un agente de código

El agente ya leyó `AGENTS.md` y los `SKILL.md`. No hace falta explicarle el
repositorio; hace falta decirle qué video quieres.

### Empezar un video desde cero

```
Hazme un video vertical de 40 segundos para Instagram Reels sobre CÓMO
FUNCIONA NUESTRO PROCESO DE ONBOARDING.

Audiencia: GERENTES DE OPERACIONES EN EMPRESAS MEDIANAS DE COLOMBIA.
Lo que quiero que hagan después de verlo: AGENDAR UNA DEMO.
Tono: DIRECTO, SIN CORPORATIVISMO, COMO SE LE EXPLICA A UN COLEGA.
Voz: español de Colombia, mujer.

Antes de construir nada, proponme tres ganchos distintos para la primera
frase y espera a que elija uno. No inventes cifras, nombres de clientes ni
porcentajes: si necesitas un dato, pídemelo.
```

Por qué funciona: le da audiencia y objetivo (sin eso el guion sale genérico),
y lo frena antes del gancho, que es la decisión de la que cuelga todo lo demás.

### A partir de algo que ya escribiste

```
Toma ESTE ARTÍCULO / ESTE POST DE LINKEDIN / ESTA PRESENTACIÓN y conviértelo
en un video vertical de máximo 45 segundos para TikTok.

<pega aquí el texto, o dame la ruta del archivo>

No resumas todo: escoge UNA idea, la que se sostenga sola sin el resto del
artículo. Lo que no quepa, déjalo por fuera y dime qué quitaste.
```

### Video corporativo con marca

```
Video vertical de 30 segundos para LinkedIn anunciando QUÉ.

Nuestra marca:
- Colores: #0B5FFF principal, #101828 texto, fondo claro
- Tipografía: la que más se parezca a Inter
- Cómo hablamos: EJEMPLO DE UNA FRASE NUESTRA REAL
- Nunca decimos: PALABRAS PROHIBIDAS

Lee skills/vertical-video/references/corporate.md antes de escribir.
Aplica la marca con scripts/brand.py (escribe src/brand.json), no en los componentes.
Cualquier cifra o afirmación sobre el producto, me la preguntas: no la
inventes ni la redondees.
```

### Cortar un video largo en clips

```
Tengo GRABACIÓN.MP4, es un webinar de 50 minutos. Sácame los 4 mejores
momentos como clips verticales con subtítulos quemados, entre 25 y 50
segundos cada uno.

Antes de cortar, muéstrame los momentos candidatos con su transcripción y
déjame escoger. La grabación es nuestra, tenemos derecho a usarla.
```

### Estudiar una referencia

```
Analiza REFERENCIA.MP4 y dime por qué funciona: cuánto dura el gancho, cada
cuánto corta, palabras por minuto, en qué segundo llega el pago.

Después propóneme una estructura con esa misma forma para un video sobre
NUESTRO TEMA. La estructura, no el contenido — no quiero una copia.
```

### Arreglar algo que ya existe

```
El video quedó bien pero EL TEXTO DE LA ESCENA 3 SE LEE MUY RÁPIDO / EL
SUBTÍTULO SE VE ENCIMA DEL LOGO / LA VOZ SUENA ROBÓTICA EN LA SEGUNDA FRASE.

Arréglalo y muéstrame un frame de esa escena antes de renderizar todo.
```

```
Cámbiame la locución de la escena 2 por: "TEXTO NUEVO". Regenera lo que haga
falta y dime cuánto quedó durando el video.
```

### Variantes para probar

```
Del video que ya está, hazme tres versiones que cambien SOLO el gancho —
misma duración, mismo diseño, mismas escenas de la 2 en adelante. Quiero
probar cuál retiene mejor.
```

---

## Parte 2 — Con un chat gratuito (copiar y pegar)

Estos no tocan tu computador. Devuelven texto, tú lo pegas en los archivos.

### Prompt maestro — el guion completo

Pégalo tal cual. Contesta las preguntas que te haga y te devuelve los dos
archivos listos.

```
Eres un guionista de video vertical corto (TikTok, Reels, Shorts). Vas a
escribir el guion de un video de 30 a 45 segundos.

PRIMERO pregúntame, en una sola tanda:
1. De qué es el video
2. Para quién es (a quién le hablo, en concreto)
3. Qué quiero que hagan después de verlo
4. En qué plataforma va
5. El tono, y un ejemplo de una frase que suene a nosotros

Con mis respuestas, devuélveme DOS bloques de código y nada más.

BLOQUE 1 — script.json (lo que se DICE en voz alta):

{
  "engine": "edge",
  "voice": "es-CO-SalomeNeural",
  "lang": "es",
  "tailSeconds": 0.35,
  "scenes": [
    { "id": "01-hook",  "text": "..." },
    { "id": "02-point", "text": "..." },
    { "id": "03-list",  "text": "..." },
    { "id": "04-stat",  "text": "..." },
    { "id": "05-cta",   "text": "..." }
  ]
}

BLOQUE 2 — src/content.ts (lo que se VE en pantalla). Los id tienen que ser
exactamente los mismos, en el mismo orden. Los tipos disponibles son:

export const SCENES: Scene[] = [
  { id: "01-hook",  type: "hook",  kicker: "OPCIONAL", text: "..." },
  { id: "02-point", type: "point", title: "...", body: "opcional" },
  { id: "03-list",  type: "list",  title: "...", items: ["...", "...", "..."] },
  { id: "04-stat",  type: "stat",  value: "80%", label: "..." },
  { id: "05-cta",   type: "cta",   text: "...", handle: "@usuario" },
];

REGLAS, en orden de importancia:

1. NO INVENTES DATOS. Ni porcentajes, ni precios, ni fechas, ni nombres de
   clientes, ni afirmaciones sobre lo que hace un producto. Si te falta un
   dato, escribe [FALTA: qué necesitas] y listámelo aparte al final. Un
   número inventado se vuelve una promesa que nadie hizo.

2. Los dos textos son DISTINTOS. script.json son frases completas, escritas
   para ser oídas. content.ts son fragmentos cortos para ser leídos de un
   vistazo. Nunca el mismo texto en los dos.

3. La primera frase abre una pregunta en la cabeza de quien mira. Nada de
   "en este video les voy a contar sobre". Si el gancho explica antes de
   enganchar, perdiste.

4. En pantalla: máximo 6 palabras en el hook y en el cta, máximo 5 por
   item de lista, máximo 8 en un título. Es una pantalla de celular.

5. Escríbelo para el OÍDO: sin siglas que no se digan en voz alta, sin
   símbolos (%, &, #, →), sin paréntesis, sin listas con guiones. Los
   números escríbelos como se pronuncian si son raros al leer.

6. Puedes poner una pausa real con [pause:0.4] dentro de una frase de
   script.json. Úsala justo antes del giro de una idea, no en cada coma.

7. Español NEUTRO-COLOMBIANO, de usted a nadie, sin "vosotros", sin
   "chévere" ni modismos que envejezcan. Tuteo natural.

8. Total: entre 85 y 130 palabras habladas. Más que eso no cabe en 45
   segundos sin sonar atropellado.

Al final, fuera de los bloques, escribe:
- Los [FALTA: ...] que quedaron pendientes
- Dos ganchos alternativos para la escena 1, por si el primero no convence
```

### Solo los ganchos

```
Dame 10 primeras frases distintas para un video vertical sobre TEMA, dirigido
a AUDIENCIA.

Cada una: máximo 14 palabras, pensada para ser dicha en voz alta, y que abra
una pregunta en la cabeza de quien la oye. Sin "en este video", sin "hoy les
traigo", sin preguntas retóricas de las que nadie quiere la respuesta.

Usa patrones distintos entre sí: nombrar el error en voz alta, prometer un
resultado concreto, empezar por la mitad de la historia, contradecir algo que
todos dan por cierto, o un dato que incomode.

Marca cuáles necesitan un dato que yo tendría que confirmar.
```

### Arreglar una locución que suena a robot

```
Estas frases las va a leer un motor de texto a voz y suenan a máquina.
Reescríbelas para que suenen a persona, sin cambiar lo que dicen:

<pega tus frases>

Qué hacer: deletrea las siglas como se dicen, cambia los símbolos por
palabras, parte las frases largas en dos, mete puntuación que marque el
ritmo, y pon [pause:0.3] o [pause:0.5] donde una persona respiraría.

Qué no hacer: cambiar el significado, agregar información que yo no puse, o
ponerlo más largo.
```

### Adaptar lo que ya tienes escrito

```
Convierte ESTO en el guion hablado de un video vertical de 40 segundos:

<pega tu texto — el post, la nota de prensa, la sección del brochure>

Escoge UNA sola idea, la que aguante sola. Frases completas, para ser oídas,
entre 85 y 130 palabras en total. No agregues ni un dato que no esté en el
texto que te di. Al final dime qué dejaste por fuera.
```

### Video corporativo, con la marca puesta

```
Escribe el guion de un video vertical de 30 segundos para LinkedIn.

Empresa: QUIÉNES SOMOS, EN UNA FRASE
Tema: DE QUÉ ES EL VIDEO
Audiencia: A QUIÉN LE HABLAMOS
Objetivo: QUÉ QUEREMOS QUE HAGAN
Así hablamos: <pega dos o tres frases reales de la empresa>
Nunca decimos: PALABRAS QUE NO USAMOS

Reglas:
- Ninguna cifra, porcentaje, premio, certificación ni nombre de cliente que
  yo no te haya dado. Si hace falta uno, escribe [FALTA: ...].
- Nada de "líderes en", "soluciones integrales", "sinergia", "de la mano de".
- Una idea por escena. Máximo cinco escenas.
- La última escena dice qué hacer, no "síguenos para más contenido".

Formato de salida: el JSON de script.json y el arreglo de content.ts, igual
que en el prompt maestro.
```

---

## Cómo se pegan los resultados

1. El primer bloque va a `script.json` — reemplaza todo el archivo.
2. El segundo bloque reemplaza **solo** el `export const SCENES: Scene[] = [...]`
   de `src/content.ts`. Lo de arriba (los tipos y los comentarios) se queda.
3. Revisa los `[FALTA: ...]` antes de generar la voz. Ese es el momento de
   conseguir el dato o de sacar la frase.
4. Después:

```bash
python scripts/voice.py
python scripts/captions.py
npm run dev
```

---

## Lo que casi nunca funciona

**"Hazme un video sobre marketing digital".** Sin audiencia y sin objetivo, lo
que sale es un video genérico y da lo mismo quién lo haya escrito.

**Pedir el video y el gancho de una.** El gancho decide el ritmo de todo lo
demás. Apruébalo primero y después construye.

**Dejar que la IA ponga los números.** Va a escribir "un 73% de las empresas"
porque suena bien y encaja en la frase. Ese número lo vas a publicar tú.

**Pedir el mismo texto para la voz y la pantalla.** Es la razón número uno por
la que un video suena a diapositiva leída en voz alta.
