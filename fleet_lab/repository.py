import hashlib
import json
from pathlib import Path
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4
from .domain import InputFault, shape_unit, inclusive_days, parse_day

DDL = '''
CREATE TABLE IF NOT EXISTS lab_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS units (id TEXT PRIMARY KEY, plate TEXT UNIQUE NOT NULL,
 internal_key TEXT NOT NULL, lookup_key TEXT NOT NULL, label TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)));
CREATE TABLE IF NOT EXISTS bundles (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS series (id TEXT PRIMARY KEY, bundle_id TEXT REFERENCES bundles(id), name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS assignments (unit_id TEXT REFERENCES units(id), series_id TEXT REFERENCES series(id),
 valid_from TEXT NOT NULL, valid_to TEXT NOT NULL, PRIMARY KEY(unit_id,series_id));
CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created TEXT NOT NULL, snapshot TEXT NOT NULL,
 notes TEXT NOT NULL, row_count INTEGER NOT NULL, fingerprint TEXT NOT NULL, decision TEXT NOT NULL DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT NOT NULL,
 kind TEXT NOT NULL, subject TEXT NOT NULL, detail TEXT NOT NULL);
'''

def moment(): return datetime.now(timezone.utc).isoformat(timespec='seconds')

class LabDatabase:
    def __init__(self, directory, seed_file=None):
        self.folder = Path(directory).resolve(); self.folder.mkdir(parents=True, exist_ok=True)
        self.outputs = self.folder/'exports'; self.outputs.mkdir(exist_ok=True)
        self.archives = self.folder/'backups'; self.archives.mkdir(exist_ok=True)
        self.lock = threading.RLock(); self.path = self.folder/'laboratory.sqlite3'
        with self.transaction() as db:
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0,1): raise InputFault('La base tiene una versión de esquema no compatible.')
            db.executescript(DDL); db.execute('PRAGMA user_version=1')
            if not db.execute("SELECT 1 FROM lab_meta WHERE key='seeded'").fetchone():
                seed_file = seed_file or Path(__file__).resolve().parent.parent/'datos_demo/seed.json'
                source = json.loads(Path(seed_file).read_text(encoding='utf-8'))
                self._load_catalog(db, self.validate_catalog(source))
                db.execute("INSERT INTO lab_meta VALUES('seeded','yes')")
                self._event(db, 'seed_created', 'catalog', {'synthetic': True})

    @contextmanager
    def transaction(self):
        with self.lock:
            db = sqlite3.connect(self.path, timeout=15); db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            try:
                with db: yield db
            finally: db.close()

    def _event(self, db, kind, subject, detail):
        db.execute('INSERT INTO events(created,kind,subject,detail) VALUES(?,?,?,?)',
            (moment(), kind, subject, json.dumps(detail, ensure_ascii=False)))

    def catalog(self):
        with self.transaction() as db:
            result = {'format':1}
            for table in ('units','bundles','series','assignments'):
                result[table] = [dict(r) for r in db.execute(f'SELECT * FROM {table} ORDER BY 1')]
            for u in result['units']: u['active'] = bool(u['active'])
            return result

    def save_unit(self, payload):
        fields = shape_unit(payload); identity = payload.get('id') or uuid4().hex
        if not isinstance(identity,str) or len(identity)>40: raise InputFault('Identidad de vehículo inválida.')
        with self.transaction() as db:
            if payload.get('id') and not db.execute('SELECT 1 FROM units WHERE id=?',(identity,)).fetchone():
                raise InputFault('El vehículo no existe.')
            try:
                db.execute('INSERT INTO units VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET plate=excluded.plate,internal_key=excluded.internal_key,lookup_key=excluded.lookup_key,label=excluded.label,active=excluded.active',
                    (identity,fields['plate'],fields['internal_key'],fields['lookup_key'],fields['label'],int(fields['active'])))
            except sqlite3.IntegrityError: raise InputFault('La patente ficticia ya está registrada.') from None
            self._event(db,'unit_saved',identity,fields)
        return identity

    def link_unit(self, data):
        required = {'unit_id','series_id','valid_from','valid_to'}
        if not isinstance(data,dict) or set(data)!=required: raise InputFault('Asociación inválida.')
        a,b=parse_day(data['valid_from']),parse_day(data['valid_to'])
        if b<a: raise InputFault('Vigencia inválida.')
        with self.transaction() as db:
            try: db.execute('INSERT INTO assignments VALUES(?,?,?,?) ON CONFLICT(unit_id,series_id) DO UPDATE SET valid_from=excluded.valid_from,valid_to=excluded.valid_to',
                (data['unit_id'],data['series_id'],str(a),str(b)))
            except sqlite3.IntegrityError: raise InputFault('Vehículo o reporte inexistente.') from None
            self._event(db,'assignment_saved',data['unit_id'],data)

    def eligible(self, series_id, start, end):
        inclusive_days(start,end)
        with self.transaction() as db:
            return [dict(r,active=True) for r in db.execute('''SELECT u.* FROM units u JOIN assignments a ON u.id=a.unit_id
             WHERE a.series_id=? AND u.active=1 AND a.valid_from<=? AND a.valid_to>=? ORDER BY u.plate''',(series_id,start,end))]

    def events(self):
        with self.transaction() as db:
            return [dict(r, detail=json.loads(r['detail'])) for r in db.execute('SELECT * FROM events ORDER BY seq DESC LIMIT 150')]

    @staticmethod
    def validate_catalog(data):
        if not isinstance(data,dict) or set(data)!={'format','units','bundles','series','assignments'} or type(data['format']) is not int or data['format']!=1:
            raise InputFault('Formato de catálogo no reconocido.')
        if not all(isinstance(data[k],list) and len(data[k])<=1000 for k in ('units','bundles','series','assignments')):
            raise InputFault('El catálogo supera los límites de esta DEMO.')
        if not data['bundles'] or not data['series']:raise InputFault('Debe existir al menos un grupo y un reporte ficticio.')
        units=[]; ids=set(); plates=set()
        for u in data['units']:
            if not isinstance(u,dict) or set(u)!={'id','plate','internal_key','lookup_key','label','active'}: raise InputFault('Vehículo importado inválido.')
            fields=shape_unit(u); identity=u['id']
            if not isinstance(identity,str) or not identity or len(identity)>40 or identity in ids or fields['plate'] in plates:
                raise InputFault('Identidades o patentes duplicadas.')
            ids.add(identity); plates.add(fields['plate']); units.append(dict(id=identity,**fields))
        bundles=[]; bundle_ids=set()
        from .domain import clean_text
        for item in data['bundles']:
            if not isinstance(item,dict) or set(item)!={'id','name'}: raise InputFault('Grupo inválido.')
            key=clean_text(item['id'],'ID de grupo',40)
            if key in bundle_ids: raise InputFault('Grupo duplicado.')
            bundle_ids.add(key); bundles.append(dict(id=key,name=clean_text(item['name'],'Nombre de grupo')))
        series=[]; series_ids=set()
        for item in data['series']:
            if not isinstance(item,dict) or set(item)!={'id','bundle_id','name'}: raise InputFault('Reporte inválido.')
            key=clean_text(item['id'],'ID de reporte',40)
            if key in series_ids or item['bundle_id'] not in bundle_ids: raise InputFault('Reporte duplicado o grupo inexistente.')
            series_ids.add(key);series.append(dict(id=key,bundle_id=item['bundle_id'],name=clean_text(item['name'],'Nombre de reporte')))
        assignments=[]; pairs=set()
        for item in data['assignments']:
            if not isinstance(item,dict) or set(item)!={'unit_id','series_id','valid_from','valid_to'}: raise InputFault('Asociación importada inválida.')
            pair=(item['unit_id'],item['series_id'])
            if pair in pairs or pair[0] not in ids or pair[1] not in series_ids or parse_day(item['valid_to'])<parse_day(item['valid_from']):
                raise InputFault('Asociación duplicada, fuera de catálogo o con vigencia inválida.')
            pairs.add(pair);assignments.append(dict(item))
        return dict(format=1,units=units,bundles=bundles,series=series,assignments=assignments)

    def _load_catalog(self, db, data):
        for table in ('assignments','series','bundles','units'): db.execute(f'DELETE FROM {table}')
        for u in data['units']: db.execute('INSERT INTO units VALUES(?,?,?,?,?,?)',(u['id'],u['plate'],u['internal_key'],u['lookup_key'],u['label'],int(u['active'])))
        for b in data['bundles']: db.execute('INSERT INTO bundles VALUES(?,?)',(b['id'],b['name']))
        for s in data['series']: db.execute('INSERT INTO series VALUES(?,?,?)',(s['id'],s['bundle_id'],s['name']))
        for a in data['assignments']: db.execute('INSERT INTO assignments VALUES(?,?,?,?)',(a['unit_id'],a['series_id'],a['valid_from'],a['valid_to']))

    def archive_catalog(self):
        with self.lock:
            content=json.dumps(self.catalog(),ensure_ascii=False,sort_keys=True,indent=2).encode()
            name=uuid4().hex+'.json'; (self.archives/name).write_bytes(content)
            digest=hashlib.sha256(content).hexdigest()
            with self.transaction() as db:self._event(db,'backup_created',name,{'sha256':digest})
            return dict(name=name,sha256=digest)

    def import_catalog(self, data):
        with self.lock:
            valid=self.validate_catalog(data); backup=self.archive_catalog()
            with self.transaction() as db:
                self._load_catalog(db,valid);self._event(db,'catalog_imported','catalog',{'units':len(valid['units'])})
            return dict(units=len(valid['units']),backup=backup)

    def restore_catalog(self, name, digest):
        with self.lock:
            if not isinstance(name,str) or not __import__('re').fullmatch(r'[a-f0-9]{32}\.json',name): raise InputFault('Respaldo inválido.')
            p=self.archives/name
            if not p.is_file():raise InputFault('El respaldo no existe.')
            content=p.read_bytes()
            if hashlib.sha256(content).hexdigest()!=digest:raise InputFault('El hash del respaldo no coincide.')
            data=self.validate_catalog(json.loads(content))
            with self.transaction() as db:
                self._load_catalog(db,data);self._event(db,'catalog_restored',name,{'sha256':digest})
            return dict(restored=True)
