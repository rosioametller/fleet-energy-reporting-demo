# Propuesta del primer commit — no ejecutada

Esta lista corresponde únicamente a la implementación original de este directorio.
No incluye dependencias instaladas, base local, archivos Excel, perfiles, logs ni
resultados privados de QA. Las siete capturas son propias y contienen datos ficticios.

Antes de agregar archivos, revisar README, código, capturas y LICENSE.
Definir una licencia apropiada antes de publicar; no se presume autorización bajo
una licencia de código abierto concreta. El comando siguiente es una propuesta,
no una operación realizada.

## Archivos exactos

- `.gitignore`
- `Abrir_Demo.cmd`
- `INVENTARIO_PRELIMINAR.md`
- `LICENSE`
- `README.md`
- `configuraciones/example/local.example.json`
- `datos_demo/seed.json`
- `docs/ARQUITECTURA.md`
- `docs/ENTREGA.md`
- `docs/FUENTES.md`
- `docs/PRIMER_COMMIT.md`
- `docs/VALIDACION.md`
- `fleet_lab/__init__.py`
- `fleet_lab/application.py`
- `fleet_lab/domain.py`
- `fleet_lab/providers.py`
- `fleet_lab/repository.py`
- `fleet_lab/web.py`
- `fleet_lab/web_assets/index.html`
- `fleet_lab/web_assets/screen.css`
- `fleet_lab/web_assets/screen.js`
- `fleet_lab/workbooks.py`
- `requirements.txt`
- `screenshots/crear-reporte.png`
- `screenshots/excel-simplificado.png`
- `screenshots/grupos.png`
- `screenshots/historial.png`
- `screenshots/inicio.png`
- `screenshots/sistema.png`
- `screenshots/vehiculos.png`
- `tests/__init__.py`
- `tests/browser_walkthrough.py`
- `tests/inspect_release.py`
- `tests/test_laboratory.py`

## Comando propuesto

```powershell
git add -- `
    '.gitignore' `
    'Abrir_Demo.cmd' `
    'INVENTARIO_PRELIMINAR.md' `
    'LICENSE' `
    'README.md' `
    'configuraciones/example/local.example.json' `
    'datos_demo/seed.json' `
    'docs/ARQUITECTURA.md' `
    'docs/ENTREGA.md' `
    'docs/FUENTES.md' `
    'docs/PRIMER_COMMIT.md' `
    'docs/VALIDACION.md' `
    'fleet_lab/__init__.py' `
    'fleet_lab/application.py' `
    'fleet_lab/domain.py' `
    'fleet_lab/providers.py' `
    'fleet_lab/repository.py' `
    'fleet_lab/web.py' `
    'fleet_lab/web_assets/index.html' `
    'fleet_lab/web_assets/screen.css' `
    'fleet_lab/web_assets/screen.js' `
    'fleet_lab/workbooks.py' `
    'requirements.txt' `
    'screenshots/crear-reporte.png' `
    'screenshots/excel-simplificado.png' `
    'screenshots/grupos.png' `
    'screenshots/historial.png' `
    'screenshots/inicio.png' `
    'screenshots/sistema.png' `
    'screenshots/vehiculos.png' `
    'tests/__init__.py' `
    'tests/browser_walkthrough.py' `
    'tests/inspect_release.py' `
    'tests/test_laboratory.py'
```

Mensaje de commit sugerido: `feat: crea laboratorio local de flotas con datos sintéticos`.

Estado previsto al revisar: rama main sin commits ni remotos, todos los candidatos
sin seguimiento y ningún archivo preparado en el índice. No se ha ejecutado add,
commit, remote add ni push. Los pasos posteriores requieren revisión del usuario:
selección explícita, primer commit y, en otro momento, creación del repositorio y
publicación. Esas acciones no forman parte de esta entrega.
