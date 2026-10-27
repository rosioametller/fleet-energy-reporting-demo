# Validación local de la DEMO mínima

Resultados del 26 de octubre de 2026. Implementación independiente, de usuario único,
para revisión local. No se declara validación en otro equipo ni uso productivo.

| Comprobación actual | Resultado |
|---|---|
| Dependencias | Entorno propio ya instalado; no se descargó ni instaló nada en esta revisión |
| pip check | Aprobado, con consulta de versiones remotas deshabilitada |
| py_compile | 11 archivos originales compilados fuera del árbol de fuentes |
| Pruebas descubiertas | 53 |
| Aprobadas / fallidas / errores / omitidas | 53 / 0 / 0 / 0 |
| Recorrido de navegador | 14 comprobaciones completas |
| Descargas del navegador | 2: catálogo JSON y reporte del escenario mixto |
| Excel generados y reabiertos | 2: básico y mixto |
| Excel básico | Exactamente Reporte y Resumen |
| Excel mixto | Reporte, Resumen y Advertencias por observaciones verificadas |
| JavaScript / solicitudes externas observadas | 0 errores / 0 solicitudes externas |
| Interfaz | Cinco pantallas a 390 px sin desbordamiento de página y escritorio a 1440 px |
| CMD con ventana propia | Página de la aplicación cargada, salida 0 y puerto liberado |
| Procesos propios residuales | Cero, comprobados al terminar |
| Inspección estática de candidatos | Sin hallazgos de los patrones revisados |

## Qué se verificó

La base SQLite se crea desde una carpeta inexistente y siembra seis unidades
ficticias. Las fechas, valores numéricos, tablas y hojas de Excel se comprobaron
con openpyxl. Un cero confirmado conserva su valor y no crea por sí solo una hoja
de advertencias. Las ausencias no se rellenan con cero. Conflictos impiden generar.
Cambiar el formulario descarta la vista previa anterior y obliga a recalcular.

Las pruebas también comprueban identidad independiente, vigencias, inactivos,
persistencia de historial, restauración y los límites del servidor local. Los
módulos de aplicación importados se verifican bajo fleet_lab en este directorio;
no hay importaciones de módulos de otra aplicación.

## Comprobación offline

La suite impide las conexiones Python fuera de 127.0.0.1. Una prueba genera y
reabre Excel con todas las conexiones y resoluciones DNS bloqueadas. El recorrido
Chromium utiliza un proxy sin listener en loopback, con bypass solo para la
aplicación, además del bloqueo por origen. Así se completa el flujo sin una
salida HTTP(S) operativa hacia internet. No se deshabilitaron adaptadores, firewall
ni políticas de Windows. Los paquetes y el navegador ya estaban instalados.

El servidor se verificó en escucha exclusivamente en 127.0.0.1. El CMD nuevo se
probó con Chromium propio, se consultó su estado por loopback y se cerró únicamente
su ventana. Se registraron salida 0 y puerto libre; no se cerraron procesos ajenos.

## Procedencia y privacidad

El backend, la interfaz, los datos, las pruebas y la documentación se escribieron
desde cero usando solo una descripción conceptual de funcionalidades. En este
trabajo no se abrieron ni importaron archivos empresariales. No se consultaron
fuentes de otra aplicación para realizar estos cambios.

El escaneo de candidatos no encontró patrones de secretos, rutas personales,
direcciones de correo o URLs ajenas a loopback. La revisión de referencias de
organizaciones no detectó nombres empresariales. Los identificadores de la semilla
son DEMO-901 a DEMO-906 y LAB-7001 a LAB-7006. Las imágenes se capturaron dentro de
esta DEMO y no contienen metadatos de texto. La inspección es estática y no garantiza
la ausencia de cualquier problema en futuras modificaciones.

La revisión del XLSX es con openpyxl; no se invocó Microsoft Excel en esta revisión.
Las capturas de Excel reconstruyen celdas del XLSX sintético, no son capturas de una
aplicación ofimática de escritorio.

## Evidencia y repetición

La evidencia actual está en .qa/minimum-review, excluida de Git. Los resultados
anteriores se conservan separados. Se resolvió un caso de cierre durante navegación
inicial y se agregaron pruebas para ese comportamiento. En los intentos iniciales
el controlador también cerraba una ventana provisional antes de que cargara la
aplicación: no se cuentan esos intentos como un cierre normal aprobado. La prueba
final espera el título de Fleet Energy Lab antes de cerrar y captura salida 0.

```powershell
.\.venv\Scripts\python.exe -E -B -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe -E -B tests\browser_walkthrough.py
.\.venv\Scripts\python.exe -E -B tests\inspect_release.py
```

Si Chromium está instalado en una carpeta propia, usar PLAYWRIGHT_BROWSERS_PATH
solo para el proceso de prueba. No hay instalación ni llamadas a repositorios en
estos comandos. LICENSE contiene la licencia MIT autorizada. El Git nuevo conserva
main sin commits, remotos ni archivos preparados. No se utilizó Sites para alojar,
publicar o sincronizar; no se ejecutó add, commit, remote add o push.

## Cierre documental posterior

En el cierre de documentación y privacidad no se repitió la suite ni se añadieron
pruebas. Las 53 pruebas y 14 comprobaciones anteriores se conservan como evidencia
funcional: el código, las pruebas y los recursos no cambiaron. Se revisaron a mano
las siete capturas y se repitió únicamente la inspección de privacidad y visibilidad
Git. El informe final de ese cierre se encuentra en ENTREGA.md.

## Verificación para el primer commit local — 2026-10-27

Este apartado actualiza el estado de los cierres anteriores: la autora autorizó
la licencia MIT y la creación del primer commit local. LICENSE contiene el texto
completo con Copyright (c) 2026 Rosio Ametller. Las referencias documentales se
actualizaron. El inspector admite el archivo LICENSE sin extensión.

En esta ejecución pasaron las 53 pruebas completas y las 14 comprobaciones de
navegador, con cero errores JavaScript, cero solicitudes externas y dos Excel
generados y reabiertos. Se comprobó loopback exclusivo y generación sin red.
La inspección de los 34 candidatos no encontró alertas. Git diff --check pasó.
No se instalaron programas ni se configuraron remotos; no se autoriza un push.
Las capturas del recorrido nuevo permanecen en .qa/, fuera de distribución.
