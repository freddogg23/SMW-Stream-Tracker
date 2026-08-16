SMW STREAM TRACKER - GUÍA COMPLETA DE CONFIGURACIÓN
Versión 1.1.1

IDIOMAS
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

COMPATIBILIDAD CON MACOS

SMW Stream Tracker ahora usa rutas nativas de Mac y dispone de compilaciones
para Apple Silicon (arm64) e Intel (x86_64). Descarga el DMG correspondiente y
arrastra la aplicación a Aplicaciones. Los datos del tracker se guardan en:
~/Library/Application Support/SMWStreamTracker

Configuración de conexión y emulador descarga las versiones oficiales para Mac
de SNI, QUsb2Snes y RetroArch, incluido el núcleo bsnes-mercury correcto.
LiveSplit clásico solo funciona en Windows, por lo que la versión para Mac
incluye ventanas sincronizadas para los temporizadores de juego y nivel,
además de game_timer.txt y level_timer.txt para OBS. El catálogo, los parches,
los alias de emojis para FXPAK, la base de datos, los libros y los textos de OBS
mantienen el mismo funcionamiento en Windows y Mac.

NOVEDADES DE LA VERSIÓN 1.1.1

* SMW Central dispone ahora de una página de inicio integrada con tarjetas de
  contenido en vivo, detalles ampliados de hacks, búsqueda por etiquetas,
  capturas de pantalla y herramientas de cuenta y comentarios.
* SMW Central Radio y la reproducción SPC incluyen un reproductor compacto que
  se puede mover, redimensionar, minimizar y mantener abierto con el tracker.
* El modo opcional de captura de OBS mantiene los cuadros azules del tracker en
  la ventana principal para incluirlos en una sola captura de ventana de OBS.
* La versión normal para Windows añade estados 5–11 de MiSTer con comprobación
  de compatibilidad y copia exacta restaurable. Conserva las ranuras nativas
  1–4 y F12 continúa abriendo el menú de MiSTer.
* Se reorganizan los menús de configuración, aplicación, OBS y LiveSplit sin
  interrumpir la guía inicial. Modos de juego vuelve al panel tras iniciar un hack.
* Los datos antiguos de conexión de MiSTer ya no afectan a RetroArch, y mejoran
  el redimensionamiento de ventanas y el cierre de Google Sheets.
* Cada frase nueva está traducida a los seis idiomas y se comprueba mediante una
  auditoría automática de traducción más completa.

NOVEDADES DE LA VERSIÓN 1.1.0

* MiSTer FPGA ya es una plataforma de juego completa. La configuración con un
  clic encuentra la consola en la red local, prepara el inicio remoto y el
  seguimiento en vivo, y funciona con MiSTer y MiSTer Multisystem².
* Modos de juego incluye Jugar hack aleatorio, Draft de hacks, Escalera de
  dificultad, Especial del creador, Cápsula del tiempo y Gira del Salón de la
  Fama, con ventanas azules traducidas y descripciones al pasar el cursor.
* Configuración de hojas de cálculo permite importar Excel de forma inteligente.
  Google Sheets sincroniza en ambas direcciones y se guarda una nueva copia de
  recuperación del tracker y la base de datos en cada cierre correcto.
* Mi Tracker tiene controles compactos para añadir y eliminar, eliminación de
  varias filas, renumeración automática de Hack # y submenús más ordenados.
* Los menús y ajustes ocultan las opciones que no corresponden a la plataforma
  FXPAK Pro, RetroArch o MiSTer seleccionada.
* La instalación opcional de RetroArch en Windows es más rápida y RetroArch no
  se abre hasta que el usuario inicia un juego.
* La salida de eventos de nivel para Streamer.bot y las guías traducidas permiten
  automatizar predicciones opcionales de Twitch.
* Todos los menús, botones, estados, mensajes e instrucciones nuevos están
  traducidos a los seis idiomas compatibles.

* El comportamiento nativo para Windows y macOS incluye compilaciones
  reproducibles para Apple Silicon e Intel y la configuración correcta de SNI,
  QUsb2Snes y RetroArch para cada plataforma.
* Mover la ventana y desplazar Mi Tracker es más fluido; el banner se reutiliza,
  los bordes de las tablas permanecen alineados y una ventana principal más
  baja puede desplazarse verticalmente hasta los controles inferiores.
* Un formulario azul y traducido de Añadir al tracker acepta todos los datos del
  hack y del progreso. Los hacks personalizados no moderados permanecen junto
  al catálogo y se pueden parchear y enviar al FXPAK Pro.
* Actualizar puede reiniciar de forma segura una sesión activa del FXPAK Pro
  antes de reconectarse, y Eliminar de Mi Tracker usa ahora el cuadro azul.
* Una nueva guía inicial hace parpadear en orden cada paso necesario de
  Descargas, conexión, catálogo, actualización, parcheo, FXPAK y OBS.
* Al elegir SNI o RetroArch, QUsb2Snes y la opción elegida dejan de parpadear;
  solo queda resaltada la otra opción obligatoria entre SNI y RetroArch.
* El catálogo de SMW Central y el descargador usan flechas desplegables azules,
  barras de desplazamiento amarillas, campos de tipo más anchos y bordes de
  celda azul claro.
* Las transferencias a FXPAK Pro sustituyen cada emoji por su nombre Unicode
  legible en el archivo ROM, también para hacks futuros. El catálogo, el tracker
  y la pantalla del juego conservan el título original, y la asignación guardada
  recupera la ROM renombrada al seleccionarla.
* Al activar la subida por USB, las ROM locales existentes con emojis también
  se transfieren y asignan automáticamente. Así se reparan descargas anteriores
  sin volver a descargarlas ni aplicarles el parche.
* Al iniciar un hack con emojis, el tracker encuentra su alias legible en FXPAK
  o lo sube automáticamente si falta. El vínculo permanente usa el ID de SMW
  Central, por lo que el tracker siempre recupera y muestra el título original.
* Durante una transferencia a FXPAK, la conexión activa del tracker con
  SNI/QUsb2Snes se pausa y se reconecta automáticamente después, evitando que
  bloquee la subida con el nombre seguro sin emojis.
* La página de OBS explica cómo reutilizar fuentes de texto existentes. Dos
  botones descargan y configuran copias separadas de LiveSplit para partida y
  nivel en los puertos 16834 y 16835.
* Estadísticas tiene el nuevo diseño de dos columnas, gráficos más grandes y
  una tabla compacta de Progreso por dificultad.
* Todos los mensajes, menús, controles, estados, selectores y pantallas de
  configuración están traducidos en todos los idiomas disponibles.
* Acerca de y actualizaciones incluye un botón Unirse a Discord para obtener
  ayuda o contactar con FredDOGG23: https://discord.gg/fHkTRgqjcr

ÍNDICE
1. Requisitos
2. Instalar el programa
3. Elegir software opcional
4. Configurar FXPAK Pro
5. Configurar RetroArch
6. Elegir carpetas y archivos
7. Actualizar el catálogo
8. Descargar y crear hacks
9. Copiar ROMs a una tarjeta SD
10. Jugar y seguir un hack
11. Temporizadores, Mi Tracker y estadísticas
12. LiveSplit, OBS Studio y Streamlabs Desktop
13. Actualizaciones, copias y reversión
14. Solución de problemas y privacidad

1. REQUISITOS

* Un PC de 64 bits con Windows 10/11 o un Mac Intel/Apple Silicon compatible.
* Una carpeta para las ROMs parcheadas.
* Internet para actualizar el catálogo y realizar descargas opcionales.
* Un FXPAK Pro/SD2SNES, RetroArch o un MiSTer FPGA conectado a la red local.
* Tu propia ROM limpia y obtenida legalmente de Super Mario World si deseas
  crear ROMs jugables a partir de parches moderados.

SMW Stream Tracker no incluye ni descarga una ROM base comercial.

2. INSTALAR EL PROGRAMA

1. Ejecuta SMWStreamTracker_Setup_1.1.1.exe.
2. Elige un idioma en la primera pantalla.
3. Lee el aviso sobre software opcional y ROMs.
4. Elige FXPAK Pro, RetroArch o MiSTer como plataforma inicial.
5. Marca las herramientas opcionales que quieras instalar.
6. Elige las carpetas de ROMs parcheadas y salida de OBS, o déjalas vacías para
   configurarlas más adelante.
7. Termina la instalación y abre esta guía.

Los ajustes existentes del tracker se conservan al instalar o actualizar.
Una desinstalación completa elimina los ajustes y datos del tracker, las copias
de LiveSplit y los archivos de texto de OBS creados por el tracker. Conserva
RetroArch, SNI, QUsb2Snes y todos los archivos y carpetas de ROM. Una instalación
nueva posterior vuelve a mostrar la pantalla de bienvenida y configuración.
Solo se puede instalar una copia en la cuenta actual de Windows. Al ejecutar de
nuevo el instalador completo, se pregunta si desea quitar la copia actual y
continuar con una instalación nueva, o desinstalar por completo el tracker y
salir. Ambas opciones conservan RetroArch, SNI, QUsb2Snes y todos los archivos ROM.
Puedes cambiar el idioma de la interfaz en cualquier momento desde Archivo >
Idioma. La pantalla principal se actualiza de inmediato sin conservar textos
del idioma anterior.

3. ELEGIR SOFTWARE OPCIONAL

La configuración de FXPAK Pro o SD2SNES solo requiere QUsb2Snes. SNI no es
necesario para el flujo de trabajo de FXPAK Pro. La configuración de RetroArch
requiere RetroArch y SNI; SNI proporciona la conexión de memoria en directo.
En la guía de botones intermitentes, QUsb2Snes puede avanzar por sí solo. Si se
selecciona SNI o RetroArch, el paso de conexión permanece activo hasta completar
ambos.
Al seleccionar RetroArch, el instalador azul descarga y extrae la versión
portátil oficial en su carpeta Tools, instala el núcleo bsnes-mercury
Performance, activa Comandos de red en el puerto 55355 y guarda ambas rutas.
No se abre otro asistente de instalación de RetroArch.

Si omites una herramienta durante la instalación, abre más tarde Descargas >
Configuración de conexión y emulador. La aplicación puede localizar una
instalación existente de SNI, QUsb2Snes o RetroArch, o instalarla en tu perfil
de usuario. Al configurar RetroArch, también instala el núcleo recomendado,
activa Comandos de red en el puerto 55355 y guarda ambas rutas en el tracker.
Cuando se encuentra una copia, un cuadro azul traducido permite usarla
automáticamente o elegir una descarga nueva.

4. CONFIGURAR FXPAK PRO

1. Conecta el puerto USB de FXPAK Pro al PC y enciende la consola.
2. Inicia SNI o QUsb2Snes y espera a que aparezca el dispositivo.
3. Abre SMW Stream Tracker y selecciona Archivo > FXPAK Pro.
4. Pulsa Actualizar si el estado no cambia automáticamente.
5. En Configuración, comprueba el ejecutable del servicio y la dirección
   WebSocket. La dirección habitual es ws://localhost:23074.

Si no aparece, revisa el cable USB, el firmware compatible, el controlador de
Windows y que otra aplicación no esté usando la conexión.

5. CONFIGURAR RETROARCH

1. Instala RetroArch o selecciona tu retroarch.exe en Configuración.
2. Instala Nintendo - SNES / SFC (bsnes-mercury Performance) desde Actualizador en línea >
   Descargador de núcleos.
3. Abre Configuración > Red en RetroArch.
4. Activa Comandos de red y conserva el puerto 55355.
5. En SMW Stream Tracker, selecciona Archivo > RetroArch.
6. Elige retroarch.exe y bsnes_mercury_performance_libretro.dll si no se detectaron.
7. Usa Jugar en el tracker. Al cambiar de juego, guarda el estado, cierra el
   contenido actual y abre el hack seleccionado.

6. ELEGIR CARPETAS Y ARCHIVOS

Abre Archivo > Configuración y revisa:

* Biblioteca de ROMs parcheadas.
* Carpeta de salida de texto para OBS.
* ROM base limpia para aplicar parches moderados.
* Ejecutable de SNI/QUsb2Snes para FXPAK Pro.
* Ejecutable de RetroArch y núcleo bsnes-mercury Performance.

Ejecuta la comprobación de estado después de cambiar rutas.

7. ACTUALIZAR EL CATÁLOGO

1. Abre Descargas.
2. Elige Actualizar hacks moderados desde SMW Central.
3. Espera; las solicitudes se espacian para evitar límites del sitio.
4. Abre Ver catálogo completo para buscar, filtrar y ordenar.
5. Pulsa Fecha añadida una vez para mostrar lo más reciente y otra vez para lo
   más antiguo.

Usa Restablecer catálogo en la parte inferior para quitar todas las entradas
moderadas y en espera guardadas localmente. Primero se crea una copia de
recuperación. Se conservan el progreso, las puntuaciones, las notas, los hacks
personalizados, las asignaciones de ROM y los archivos ROM.

Solo la celda Dificultad usa el color configurado para esa dificultad.

8. DESCARGAR Y CREAR HACKS

1. Abre Descargas > Descargar hacks de SMW faltantes.
2. Elige tu ROM limpia y legal de Super Mario World.
3. Elige la carpeta de la biblioteca parcheada.
4. Filtra por tipo, dificultad, puntuación o fecha si lo deseas.
5. Revisa la vista previa y pulsa Descargar hacks moderados.

La herramienta descarga parches moderados y los aplica localmente. Nunca
descarga una ROM base y omite juegos existentes.

9. COPIAR ROMS A UNA TARJETA SD

Selecciona el destino SD en Configuración y activa la copia durante la descarga.
Confirma cuidadosamente la unidad. Normalmente FXPAK Pro no presenta su tarjeta
como unidad de Windows por el USB de seguimiento; para copias masivas y
permanentes suele hacer falta un lector de tarjetas.

10. JUGAR Y SEGUIR UN HACK

Escribe en Buscar o seleccionar un hack, elige un resultado y pulsa Jugar.
Modos de juego en la pantalla principal abre una página de pantalla completa
con un botón Inicio. Elige Jugar hack aleatorio para iniciar una partida
descargada al azar según los filtros seleccionados.
Añadir a Mi Tracker crea una entrada y Completar hack registra la finalización.
Al hacer clic fuera se cierra
la lista; el texto de búsqueda permanece hasta elegir un hack.

11. TEMPORIZADORES, MI TRACKER Y ESTADÍSTICAS

Controla los temporizadores de juego y nivel desde la pantalla principal. Mi
Tracker permite búsqueda, filtros, campos editables, colores de dificultad,
barras de puntuación y progreso, y exportación CSV/XLSX. Las estadísticas
resumen progreso, puntuaciones, tiempo, actividad y dificultad.

12. LIVESPLIT, OBS STUDIO Y STREAMLABS DESKTOP

Puedes capturar las ventanas de LiveSplit, usar los archivos de texto del
tracker o combinar ambos métodos. Los archivos de texto son la opción más
sencilla y no necesitan LiveSplit.

CONFIGURACIÓN AUTOMÁTICA DE DOS COPIAS (RECOMENDADA)

1. Abre Ayuda > Configuración > Configurar temporizadores LiveSplit.
2. Selecciona LiveSplit de juego (16834). El tracker descarga la versión
   oficial actual, crea una carpeta independiente, configura el puerto 16834
   y el inicio automático del servidor TCP, y abre LiveSplit.
3. Selecciona LiveSplit de nivel (16835). El tracker crea otra copia,
   configura el puerto 16835 y el inicio automático TCP, y la abre.
4. Cuando los dos botones estén verdes, selecciona Listo y guarda.
5. Mantén ambas ventanas abiertas y sin minimizar al usar el tracker u OBS.
   Los botones volverán a abrir las copias configuradas más adelante.

CONFIGURACIÓN MANUAL (ALTERNATIVA)

CONECTAR EL TEMPORIZADOR DE JUEGO DE LIVESPLIT

1. Descarga y extrae LiveSplit desde https://livesplit.org/downloads/.
2. Abre LiveSplit.exe. El servidor ya viene integrado; no instales el antiguo
   componente LiveSplit Server por separado.
3. Haz clic derecho en LiveSplit, abre Configuración y establece Server Port
   en 16834.
4. Si solo usarás un temporizador, el inicio automático es opcional. Con dos
   ventanas, inicia cada servidor manualmente después de revisar su puerto con
   Control > Start TCP/WS Server.
5. En SMW Stream Tracker abre Archivo > Configuración, establece Game LiveSplit
   port en 16834, guarda y prueba Iniciar temporizador de juego.

CONECTAR UN TEMPORIZADOR DE NIVEL INDEPENDIENTE

1. Deja abierta la primera ventana y ejecuta LiveSplit.exe otra vez.
2. En la segunda ventana establece Server Port en 16835 e inicia su servidor
   TCP.
3. Deja Level LiveSplit port en 16835 en el tracker.
4. Prueba Iniciar temporizador de nivel, Iniciar temporizadores y Restablecer
   temporizador de nivel.

Las dos ventanas deben usar puertos diferentes. Al volver a abrirlas, confirma
16834 en la primera y 16835 en la segunda antes de iniciar cada servidor. La
conexión permanece en este equipo mediante 127.0.0.1.

MOSTRAR LIVESPLIT EN OBS STUDIO

1. Mantén abiertas y sin minimizar las ventanas de LiveSplit.
2. En Fuentes de OBS selecciona + > Captura de ventana.
3. Elige la ventana del temporizador de juego, colócala y cambia su tamaño.
4. Repite con otra Captura de ventana para el temporizador de nivel.
5. Haz una grabación corta de prueba y comprueba ambos temporizadores.

MOSTRAR LIVESPLIT EN STREAMLABS DESKTOP

1. Mantén las ventanas de LiveSplit abiertas y sin minimizar.
2. En Fuentes selecciona + > Captura de pantalla; si aparece Captura de
   ventana por separado, usa esa opción.
3. Selecciona, coloca y ajusta cada ventana de LiveSplit.
4. Haz una grabación corta de prueba antes de transmitir.

USAR LOS ARCHIVOS DE TEMPORIZADOR EN OBS O STREAMLABS

1. Elige una carpeta de salida OBS en Archivo > Configuración y guarda.
2. Selecciona o inicia un hack y usa ambos temporizadores una vez.
3. Usa Archivo > Abrir carpeta de texto OBS para abrir la carpeta correcta.
4. En OBS o Streamlabs añade una fuente Texto (GDI+).
5. Activa Leer desde archivo y selecciona game_timer.txt.
6. Añade otra fuente Texto y selecciona level_timer.txt.
7. Configura fuente, color, contorno, alineación y tamaño.
8. Si quieres, repite con hack_name.txt, author.txt, exits.txt, level_deaths.txt o total_deaths.txt.

Muertes del nivel conserva los reintentos y se reinicia al comenzar un nivel
distinto. Muertes totales se guarda por separado para cada ROM y archivo Mario
A, B o C. Puedes cambiar ambos textos en Archivo > Configuración de OBS.
death_counter.txt sigue reflejando level_deaths.txt para escenas existentes.

SMW Stream Tracker debe seguir abierto para actualizar los archivos. Si una
fuente está vacía o atrasada, confirma que usa la misma carpeta configurada en
el tracker y vuelve a operar el temporizador.

Ayuda oficial:
Servidor LiveSplit: https://github.com/LiveSplit/LiveSplit#the-livesplit-server
Texto en OBS: https://obsproject.com/kb/text-sources
Captura en Streamlabs: https://streamlabs.com/content-hub/post/how-to-capture-your-screen-in-streamlabs-desktop

IMPORTACIÓN, GOOGLE SHEETS Y COPIA PERMANENTE DE EXCEL

Estadísticas > Importar hoja de cálculo existente restaura las exportaciones
actuales de Mi Tracker con progreso, tiempo, muertes, puntuaciones, fechas y
notas. Para importar directamente, abre Mi Tracker > Sincronizar desde Google
Sheets, pega el enlace normal y selecciona Importar ahora. Comparte la hoja como
Lector con Cualquier persona que tenga el enlace; debe incluir una pestaña
Tracker o My Tracker. Apps Script sigue disponible para sincronización automática.
El archivo Documents > SMW Stream Tracker Backups >
SMW_Stream_Tracker_Automatic_Backup.xlsx no se elimina al desinstalar.

13. ACTUALIZACIONES, COPIAS Y REVERSIÓN

Usa SMWStreamTracker_Update_VERSION.exe para versiones pequeñas después de una
instalación completa. El actualizador conserva el ejecutable anterior para
revertir. Haz copia de la base de datos, configuración y biblioteca antes de
cambios importantes de Windows o almacenamiento.

14. SOLUCIÓN DE PROBLEMAS Y PRIVACIDAD

* FXPAK desconectado: revisa SNI/QUsb2Snes, USB, firmware y puerto 23074.
* Hack actual deja de detectar juegos después de una actualización dentro de
  la aplicación: abre Descargas > Configuración de conexión y emulador >
  Instalar o buscar SNI (muy recomendado). Deja que el tracker encuentre o
  reinstale SNI, reinicia SNI y selecciona Actualizar.
* RetroArch no sigue el juego: activa Comandos de red en el puerto 55355.
* El juego no abre: revisa ROM, ejecutable, núcleo y rutas.
* Catálogo lento: deja que los reintentos espaciados terminen.

Los datos del tracker y las rutas se procesan localmente. Las funciones de
catálogo, dependencias, actualización y sincronización solo se conectan cuando
se usan. Consulta PRIVACY.txt y THIRD_PARTY_NOTICE.txt para los avisos completos.

CONFIGURACIÓN RÁPIDA DE MISTER

En una instalación nueva de Windows, elige MiSTer FPGA y deja seleccionada la
opción Configurar MiSTer en el primer inicio. La guía intermitente te llevará al
botón de configuración automática.

Conecta MiSTer y este equipo al mismo router y abre Descargas > Configuración
de conexión y emulador > Configurar MiSTer y selecciona Buscar y configurar
MiSTer. El tracker encuentra y verifica la unidad, instala o repara el
seguimiento en vivo, crea las carpetas de juegos, selecciona MiSTer, configura
un acceso automático exclusivo para la aplicación y prueba la conexión. Si se
solicita, el acceso SSH de fábrica es root, puerto 22, contraseña 1; la contraseña
nunca se guarda. Los hacks se copian con nombres seguros sin cambiar sus títulos
reales en el catálogo.

La versión normal para Windows instala automáticamente los estados 5–11 de
MiSTer al ejecutar Buscar y configurar MiSTer o Instalar ranuras de estados virtuales.
Alt+F5 a Alt+F11 guardan; F5 a F11 cargan los estados 5–11; F12 sigue abriendo
el menú de MiSTer; las ranuras
nativas 1–4 permanecen intactas. Las actualizaciones del tracker conservan la función y pueden
reemplazar con seguridad una versión instalada antes por el tracker. Si MiSTer
Main se actualiza por separado, el tracker se niega a sobrescribirlo o
degradarlo. Usa Restaurar la versión anterior de MiSTer antes de actualizar
MiSTer Main y después usa un tracker preparado para ese Main más reciente.
