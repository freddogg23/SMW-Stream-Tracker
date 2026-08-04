SMW STREAM TRACKER - GUÍA COMPLETA DE CONFIGURACIÓN
Versión 1.0.0

IDIOMAS
English: README.en.txt
Australian: README.au.txt
Español: README.es.txt
Français: README.fr.txt
Deutsch: README.de.txt
Português (Brasil): README.pt-BR.txt

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
12. Salida de texto para OBS
13. Actualizaciones, copias y reversión
14. Solución de problemas y privacidad

1. REQUISITOS

* Un PC de 64 bits con Windows 10 u 11.
* Una carpeta para las ROMs parcheadas.
* Internet para actualizar el catálogo y realizar descargas opcionales.
* Un FXPAK Pro/SD2SNES o RetroArch para Windows.
* Tu propia ROM limpia y obtenida legalmente de Super Mario World si deseas
  crear ROMs jugables a partir de parches moderados.

SMW Stream Tracker no incluye ni descarga una ROM base comercial.

2. INSTALAR EL PROGRAMA

1. Ejecuta SMWStreamTracker_Setup_1.0.0.exe.
2. Elige un idioma en la primera pantalla.
3. Lee el aviso sobre software opcional y ROMs.
4. Elige FXPAK Pro o RetroArch como plataforma inicial.
5. Marca las herramientas opcionales que quieras instalar.
6. Elige las carpetas de ROMs parcheadas y salida de OBS, o déjalas vacías para
   configurarlas más adelante.
7. Termina la instalación y abre esta guía.

Los ajustes existentes del tracker se conservan al instalar o actualizar.

3. ELEGIR SOFTWARE OPCIONAL

SNI es muy recomendable y proporciona la conexión en directo que utiliza el
tracker. QUsb2Snes es un puente opcional, avanzado y heredado, principalmente
para usuarios de FXPAK Pro y SD2SNES. RetroArch es opcional: omítelo si ya está
instalado o si solo usarás FXPAK Pro. Al seleccionarlo, el asistente también
descarga el núcleo bsnes-mercury Performance de Libretro.

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
Jugar hack aleatorio elige de la biblioteca. Añadir a Mi Tracker crea una
entrada y Completar hack registra la finalización. Al hacer clic fuera se cierra
la lista; el texto de búsqueda permanece hasta elegir un hack.

11. TEMPORIZADORES, MI TRACKER Y ESTADÍSTICAS

Controla los temporizadores de juego y nivel desde la pantalla principal. Mi
Tracker permite búsqueda, filtros, campos editables, colores de dificultad,
barras de puntuación y progreso, y exportación CSV/XLSX. Las estadísticas
resumen progreso, puntuaciones, tiempo, actividad y dificultad.

12. SALIDA DE TEXTO PARA OBS

Elige una carpeta de salida en Configuración. En OBS añade una fuente Texto,
activa Leer desde archivo y selecciona el archivo deseado de esa carpeta.
Repite para título, autor, salidas, temporizadores y otros datos.

13. ACTUALIZACIONES, COPIAS Y REVERSIÓN

Usa SMWStreamTracker_Update_VERSION.exe para versiones pequeñas después de una
instalación completa. El actualizador conserva el ejecutable anterior para
revertir. Haz copia de la base de datos, configuración y biblioteca antes de
cambios importantes de Windows o almacenamiento.

14. SOLUCIÓN DE PROBLEMAS Y PRIVACIDAD

* FXPAK desconectado: revisa SNI/QUsb2Snes, USB, firmware y puerto 23074.
* RetroArch no sigue el juego: activa Comandos de red en el puerto 55355.
* El juego no abre: revisa ROM, ejecutable, núcleo y rutas.
* Catálogo lento: deja que los reintentos espaciados terminen.

Los datos del tracker y las rutas se procesan localmente. Las funciones de
catálogo, dependencias, actualización y sincronización solo se conectan cuando
se usan. Consulta PRIVACY.txt y THIRD_PARTY_NOTICE.txt para los avisos completos.
