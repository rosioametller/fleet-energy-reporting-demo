import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import urlsplit, parse_qs
from . import VERSION
from .application import FleetWorkspace
from .repository import LabDatabase
from .domain import InputFault

ASSETS=Path(__file__).resolve().parent/'web_assets'
STATIC={'/':('index.html','text/html'),'/screen.css':('screen.css','text/css'),'/screen.js':('screen.js','text/javascript')}
MAX_BODY=1024*1024

class ConsoleGateway(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    @property
    def origin(self):return f'http://127.0.0.1:{self.server.server_port}'

    def emit(self, status, content, mime='application/json', attachment=None):
        if isinstance(content,(dict,list)):content=json.dumps(content,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',mime+('; charset=utf-8' if mime.startswith('text/') or mime=='application/json' else ''))
        self.send_header('Content-Length',str(len(content)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if attachment:self.send_header('Content-Disposition',f'attachment; filename="{attachment}"')
        self.end_headers();self.wfile.write(content)

    def permitted_host(self):
        if self.headers.get('Host')!=self.origin.removeprefix('http://'):
            self.emit(403,{'error':'Host local no permitido.'});return False
        return True

    def do_GET(self):
        if not self.permitted_host():return
        parsed=urlsplit(self.path); path=parsed.path; app=self.server.workspace
        try:
            if path in STATIC:
                name,mime=STATIC[path];return self.emit(200,(ASSETS/name).read_bytes(),mime)
            if path=='/api/catalog':return self.emit(200,app.db.catalog())
            if path=='/api/available':
                q=parse_qs(parsed.query)
                return self.emit(200,{'units':app.db.eligible(q.get('series',[''])[0],q.get('start',[''])[0],q.get('end',[''])[0])})
            if path=='/api/history':return self.emit(200,{'runs':app.timeline()})
            if path=='/api/audit':return self.emit(200,{'events':app.db.events()})
            if path=='/api/catalog-export':
                return self.emit(200,app.db.catalog(),attachment='catalogo_ficticio.json')
            if path=='/api/state':
                with app.db.transaction() as db:
                    schema=db.execute('PRAGMA user_version').fetchone()[0]
                return self.emit(200,dict(version=VERSION,mode='Laboratorio sintético',schema=schema,
                    units=len(app.db.catalog()['units']),reports=len(app.timeline()),source='Proveedor local simulado',network='Solo loopback',storage='Carpeta local de esta instalación'))
            if path.startswith('/download/'):
                data=app.obtain_file(path[len('/download/'):])
                return self.emit(200,data,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','reporte_demo.xlsx')
            self.emit(404,{'error':'Recurso no disponible.'})
        except (InputFault,KeyError,ValueError):self.emit(422,{'error':'Consulta inválida o archivo no verificable.'})
        except Exception:self.emit(500,{'error':'No se completó la consulta local.'})

    def do_POST(self):
        if not self.permitted_host():return
        if self.headers.get('Origin')!=self.origin:
            return self.emit(403,{'error':'Se requiere el origen de esta aplicación local.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            return self.emit(415,{'error':'Se requiere contenido JSON.'})
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.emit(400,{'error':'Longitud inválida.'})
        if not 0<length<=MAX_BODY:return self.emit(413,{'error':'Solicitud fuera de límites.'})
        try:
            data=json.loads(self.rfile.read(length));app=self.server.workspace
            if self.path=='/api/unit':result={'id':app.db.save_unit(data)}
            elif self.path=='/api/assignment':result=(app.db.link_unit(data) or {'saved':True})
            elif self.path=='/api/preview':result=app.preview_run(data)
            elif self.path=='/api/generate':result=app.produce_run(data)
            elif self.path=='/api/decision':result=app.record_decision(data)
            elif self.path=='/api/import-preview':
                validated=app.db.validate_catalog(data);result=dict(units=len(validated['units']),assignments=len(validated['assignments']))
            elif self.path=='/api/import':result=app.db.import_catalog(data)
            elif self.path=='/api/backup':
                if data!={}:raise InputFault('Solicitud de respaldo inválida.')
                result=app.db.archive_catalog()
            elif self.path=='/api/restore':
                if not isinstance(data,dict) or set(data)!={'name','sha256'}:raise InputFault('Solicitud de restauración inválida.')
                result=app.db.restore_catalog(data['name'],data['sha256'])
            else:return self.emit(404,{'error':'Acción no disponible.'})
            self.emit(200,result)
        except (InputFault,ValueError,KeyError,TypeError) as error:
            self.emit(422,{'error':str(error) if isinstance(error,InputFault) else 'Contenido JSON inválido.'})
        except Exception:self.emit(500,{'error':'La operación local no se completó.'})

class LocalOnlyServer(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=False

def create_lab_server(directory, port=0):
    if isinstance(port,bool) or not isinstance(port,int) or not 0<=port<=65535:raise InputFault('Puerto inválido.')
    workspace=FleetWorkspace(LabDatabase(directory))
    listener=LocalOnlyServer(('127.0.0.1',port),ConsoleGateway);listener.workspace=workspace
    return listener

def open_ephemeral_window(origin):
    from playwright.sync_api import sync_playwright, Error
    with sync_playwright() as engine:
        browser=engine.chromium.launch(headless=False,args=['--disable-background-networking','--disable-component-update'])
        page=None
        try:
            context=browser.new_context(accept_downloads=True)
            context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else route.abort())
            page=context.new_page();page.goto(origin)
            while not page.is_closed():page.wait_for_timeout(300)
        except Error:
            # Closing the owned window can interrupt its initial navigation too.
            if browser.is_connected() and (page is None or not page.is_closed()):raise
        finally:
            if browser.is_connected():browser.close()

def launch():
    parser=argparse.ArgumentParser(description='Fleet Energy Lab: laboratorio local de datos sintéticos.')
    parser.add_argument('--data',type=Path,default=Path(__file__).resolve().parent.parent/'.local-state')
    parser.add_argument('--port',type=int,default=0)
    parser.add_argument('--window',action='store_true')
    args=parser.parse_args()
    listener=create_lab_server(args.data,args.port)
    origin=f'http://127.0.0.1:{listener.server_port}'
    print('Fleet Energy Lab — '+origin,flush=True)
    print('Datos ficticios. Cerrar la ventana o usar Ctrl+C detiene la instancia.',flush=True)
    try:
        if args.window:
            worker=threading.Thread(target=listener.serve_forever,daemon=True);worker.start()
            try:open_ephemeral_window(origin)
            finally:listener.shutdown();worker.join(5)
        else:listener.serve_forever()
    except KeyboardInterrupt:pass
    finally:listener.server_close()

if __name__=='__main__':
    try:launch()
    except Exception:
        print('No se pudo iniciar la DEMO. Comprueba las dependencias, Chromium y el puerto indicado.',flush=True)
        raise SystemExit(1) from None
