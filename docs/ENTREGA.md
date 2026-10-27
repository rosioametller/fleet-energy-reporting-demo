# Entrega mínima para revisión

## Implementación original

Se escribieron desde cero el dominio, la interfaz de proveedor simulado, su
implementación, el repositorio SQLite, los casos de uso, el generador XLSX, el
servidor HTTP, el HTML, el CSS, el JavaScript, el lanzador, las pruebas y los textos.
El diseño visual, las capturas y la semilla pertenecen a esta implementación.
Solo se usó la descripción conceptual de funcionalidades como referencia.

No se leyeron bloques de implementación ni se copiaron código, pruebas, textos,
recursos, configuraciones, bases o historial de otra aplicación durante este
trabajo. Todas las escrituras se realizaron en esta carpeta independiente; no se
hicieron modificaciones al proyecto de origen.

## Tecnologías

Python 3.13, SQLite, servidor HTTP estándar, openpyxl, HTML, CSS y JavaScript.
Playwright abre una ventana aislada opcional y realiza pruebas sobre loopback.
Las dependencias se instalaron en un entorno virtual nuevo, no copiado.

## Datos nuevos

Seis vehículos ficticios DEMO-901 a DEMO-906, identificadores LAB-7001 a LAB-7006 y
claves source-unit-41 a source-unit-46. Un grupo y tres circuitos inventados.
Una unidad está inactiva y otra tiene vigencia futura. Abril de 2032 sirve como
período inicial de laboratorio. Las mediciones salen de fórmulas deterministas
originales y cubren actividad, cero confirmado, ausencia, consumo elevado,
duplicado, conflicto y período incompleto. No derivan de registros reales.

## Pruebas medidas

- 53 descubiertas; 53 aprobadas; 0 fallidas; 0 errores; 0 omitidas.
- 11 archivos Python compilados y pip check aprobado.
- 14 comprobaciones completas de navegador sin salida HTTP(S) operativa hacia internet, con 0 errores JavaScript y 0 solicitudes externas.
- 2 descargas de navegador: catálogo JSON y un XLSX sintético.
- 2 XLSX reabiertos: el predeterminado contiene solo Reporte y Resumen; el mixto
  incorpora Advertencias porque tiene observaciones. Las unitarias también verifican
  el cero confirmado sin advertencias y el detalle técnico activado explícitamente.
- Lanzador CMD: página propia cargada, escucha 127.0.0.1, salida 0 y puerto libre.
- Inspección estática y revisión de fuentes: sin hallazgos de los patrones revisados.
- Consulta de procesos propia completada: cero procesos Python/Node/Chromium de esta aplicación residuales.

El archivo de ejemplo generado se conserva localmente en
`.qa/minimum-review/browser/reporte_basico.xlsx` (básico) y
`.qa/minimum-review/browser/reporte_sintetico.xlsx` (mixto), excluido del commit. No se incluye un XLSX
preexistente ni una base ya poblada entre los candidatos de distribución.

## Primer commit y decisiones pendientes

Ver [PRIMER_COMMIT.md](PRIMER_COMMIT.md) para la lista exacta de candidatos.
La licencia MIT está en LICENSE, seleccionada expresamente por la autora.
La aplicación no se declara productiva ni validada en otro equipo.

El repositorio local se inicializa nuevo en main, sin historial anterior, remotos,
staging o commits. No se ejecutan git add, git commit, git remote add ni git push.
No se creó un repositorio en GitHub ni se publicó un sitio. La siguiente acción
corresponde a la revisión del usuario y la revisión del commit local.

## Alcance mínimo actual

Se mantienen Inicio, Vehículos, Crear reporte, Historial y Sistema. No se añadieron
funciones empresariales, niveles de aprobación ni integraciones externas. La
actividad regular es el escenario inicial y el detalle técnico sigue desactivado.
La aplicación funciona offline después de su instalación; en esta revisión no se
descargaron dependencias ni se modificaron políticas. La lista completa de archivos
revisables continúa en PRIMER_COMMIT.md. No se publica ni sincroniza mediante Sites.

## Cierre documental y de privacidad

La última intervención se limita a README y documentación técnica. Se verificaron
por SHA-256 todos los candidatos que no son documentos y LICENSE:
no cambiaron código, pruebas, semilla, configuración, lanzador, requisitos ni
capturas. La licencia vigente es MIT. No se añadió funcionalidad ni pruebas.

### Capturas revisadas manualmente

Se revisaron las siete imágenes completas: inicio, vehiculos, crear-reporte,
grupos, historial, sistema y excel-simplificado. Solo muestran esta aplicación
y datos sintéticos. No muestran cuentas personales, notificaciones, rutas de
perfil, marcas empresariales ni información operacional real. La última imagen
es una representación HTML del XLSX propio, no una captura de Microsoft Excel.
La apertura verificada del archivo corresponde a openpyxl; no se afirma una
aceptación visual nueva en Microsoft Excel.

### Privacidad y archivos de distribución

La inspección estática existente recorrió los 34 candidatos sin hallazgos.
La revisión complementaria de nombres empresariales conocidos e identificadores
con aspecto de patente tampoco produjo hallazgos. Se revisaron nombres de
clientes, patentes e identificadores reales, URLs externas, credenciales, rutas
personales, correos, cookies, perfiles, datos originales y Excel/PBIX empresariales.
No hay archivos de datos empresariales entre los candidatos. La semilla contiene
únicamente DEMO-901 a DEMO-906, LAB-7001 a LAB-7006 y claves inventadas.
Los identificadores técnicos de auditoría son generados por la propia DEMO.
Los namespaces estándar de XML de Excel no representan conexiones externas.
La revisión se limita a este desarrollo independiente y no garantiza futuras
incorporaciones que no se vuelvan a revisar.

Git confirma que .local-state/ (SQLite y reportes), .qa/ (evidencias, exportaciones
y navegador) y .venv/ están ignorados. datos_demo/seed.json,
configuraciones/example/local.example.json y las siete capturas son visibles.
No se distribuye una base poblada, un perfil autenticado ni archivos XLSX/PBIX.

### Funcionamiento conservado

Se conserva la evidencia funcional anterior: 53 pruebas aprobadas, 14
comprobaciones de navegador con salida HTTP(S) externa bloqueada y cero
solicitudes externas; generación y reapertura del Excel sin conexión.
El servidor enlaza únicamente 127.0.0.1 y SQLite se crea automáticamente.
El CMD cargó la aplicación, terminó con código 0 y liberó el puerto. No se
repitió toda la suite en este cierre documental; no hubo cambios funcionales.
No se efectuaron conexiones externas ni cambios en políticas del equipo.

### Procedencia y acciones pendientes

Durante la implementación independiente y este cierre no se abrieron, leyeron,
importaron ni copiaron archivos del proyecto empresarial. El trabajo se limitó
al repositorio nuevo. No se reutilizaron código, pruebas, documentación,
configuraciones, diseños, recursos ni historial empresarial.
No se ejecutaron git add, commit, remote add ni push. No hay archivos preparados,
commits ni remotos. Se detiene la entrega para revisión del usuario.

### Árbol completo de los 34 candidatos

```text
fleet-energy-reporting-demo/
├── .gitignore
├── Abrir_Demo.cmd
├── INVENTARIO_PRELIMINAR.md
├── LICENSE
├── README.md
├── configuraciones/
│   └── example/
│       └── local.example.json
├── datos_demo/
│   └── seed.json
├── docs/
│   ├── ARQUITECTURA.md
│   ├── ENTREGA.md
│   ├── FUENTES.md
│   ├── PRIMER_COMMIT.md
│   └── VALIDACION.md
├── fleet_lab/
│   ├── __init__.py
│   ├── application.py
│   ├── domain.py
│   ├── providers.py
│   ├── repository.py
│   ├── web.py
│   ├── web_assets/
│   │   ├── index.html
│   │   ├── screen.css
│   │   └── screen.js
│   └── workbooks.py
├── requirements.txt
├── screenshots/
│   ├── crear-reporte.png
│   ├── excel-simplificado.png
│   ├── grupos.png
│   ├── historial.png
│   ├── inicio.png
│   ├── sistema.png
│   └── vehiculos.png
└── tests/
    ├── __init__.py
    ├── browser_walkthrough.py
    ├── inspect_release.py
    └── test_laboratory.py
```

Las carpetas locales ignoradas no forman parte del árbol de distribución.

### Estado Git al cierre

```text
?? .gitignore
?? Abrir_Demo.cmd
?? INVENTARIO_PRELIMINAR.md
?? LICENSE
?? README.md
?? configuraciones/
?? datos_demo/
?? docs/
?? fleet_lab/
?? requirements.txt
?? screenshots/
?? tests/
```

La lista explícita y el comando git add propuesto, sin ejecutar, se encuentran en
[PRIMER_COMMIT.md](PRIMER_COMMIT.md). Los 34 archivos del árbol son exactamente
los candidatos actuales. Mensaje propuesto:

```text
feat: crea laboratorio local de flotas con datos sintéticos
```

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
