import hashlib
import json
import os
from uuid import uuid4
from .domain import InputFault, inclusive_days, normalize_observations
from .providers import LaboratorySource
from .workbooks import build_workbook

class FleetWorkspace:
    def __init__(self, database, source=None):
        self.db=database; self.source=source or LaboratorySource()

    def stage_run(self, payload):
        expected={'series_id','unit_ids','start','end','scenario','advanced'}
        if not isinstance(payload,dict) or set(payload)!=expected:raise InputFault('Solicitud de reporte inválida.')
        days=inclusive_days(payload['start'],payload['end'])
        selected=payload['unit_ids']
        if not isinstance(selected,list) or not selected or len(selected)>100 or any(not isinstance(i,str) for i in selected) or len(set(selected))!=len(selected):
            raise InputFault('Selecciona uno o más vehículos sin duplicados.')
        if not isinstance(payload['advanced'],bool):raise InputFault('La opción técnica debe ser verdadera o falsa.')
        eligible={u['id']:u for u in self.db.eligible(payload['series_id'],payload['start'],payload['end'])}
        if not set(selected)<=set(eligible):raise InputFault('Hay vehículos inactivos, ajenos al reporte o fuera de vigencia.')
        units=[eligible[key] for key in selected]
        series=next((s for s in self.db.catalog()['series'] if s['id']==payload['series_id']),None)
        if not series:raise InputFault('El reporte no existe.')
        snapshot=dict(series_id=series['id'],series_name=series['name'],units=units,start=payload['start'],end=payload['end'],scenario=payload['scenario'])
        rows,notes=normalize_observations(self.source.fetch(units,days,payload['scenario']),units,days)
        return snapshot,rows,notes

    def preview_run(self, payload):
        snapshot,rows,notes=self.stage_run(payload)
        by_id={u['id']:u for u in snapshot['units']}
        return dict(count=len(rows),warnings=notes,rows=[dict(plate=by_id[r['unit_id']]['plate'],day=str(r['day']),distance=r['distance'],energy=r['energy'],zero=r['zero_confirmed']) for r in rows[:25]])

    def produce_run(self, payload):
        with self.db.lock:
            snapshot,rows,notes=self.stage_run(payload)
            content=build_workbook(snapshot,rows,notes,payload['advanced'])
            identity=uuid4().hex;fingerprint=hashlib.sha256(content).hexdigest()
            partial=self.db.outputs/(identity+'.pending');destination=self.db.outputs/(identity+'.xlsx')
            partial.write_bytes(content);os.replace(partial,destination)
            from .repository import moment
            try:
                with self.db.transaction() as conn:
                    conn.execute('INSERT INTO runs(id,created,snapshot,notes,row_count,fingerprint) VALUES(?,?,?,?,?,?)',
                        (identity,moment(),json.dumps(snapshot,ensure_ascii=False),json.dumps(notes,ensure_ascii=False),len(rows),fingerprint))
                    self.db._event(conn,'report_generated',identity,{'sha256':fingerprint,'rows':len(rows)})
            except Exception:
                destination.unlink(missing_ok=True);raise
            return dict(id=identity,sha256=fingerprint,rows=len(rows),warnings=notes)

    def timeline(self):
        with self.db.transaction() as conn:
            return [dict(id=r['id'],created=r['created'],title=json.loads(r['snapshot'])['series_name'],
                units=[u['plate'] for u in json.loads(r['snapshot'])['units']],start=json.loads(r['snapshot'])['start'],
                end=json.loads(r['snapshot'])['end'],rows=r['row_count'],warnings=json.loads(r['notes']),sha256=r['fingerprint'],decision=r['decision'])
                for r in conn.execute('SELECT * FROM runs ORDER BY created DESC,id DESC')]

    def obtain_file(self, identity):
        if not isinstance(identity,str) or not __import__('re').fullmatch('[a-f0-9]{32}',identity):raise InputFault('Identidad de reporte inválida.')
        with self.db.transaction() as conn:r=conn.execute('SELECT fingerprint FROM runs WHERE id=?',(identity,)).fetchone()
        path=self.db.outputs/(identity+'.xlsx')
        if not r or not path.is_file():raise InputFault('El reporte no est? disponible.')
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=r['fingerprint']:raise InputFault('El archivo cambi?; la descarga est? bloqueada.')
        return content

    def record_decision(self, payload):
        if not isinstance(payload,dict) or set(payload)!={'id','sha256','decision'} or payload['decision'] not in {'accepted','rejected'}:
            raise InputFault('Decisión inválida.')
        content=self.obtain_file(payload['id']);digest=hashlib.sha256(content).hexdigest()
        if digest!=payload['sha256']:raise InputFault('La decisión no corresponde al hash del archivo.')
        with self.db.transaction() as conn:
            conn.execute('UPDATE runs SET decision=? WHERE id=?',(payload['decision'],payload['id']))
            self.db._event(conn,'report_decided',payload['id'],{'sha256':digest,'decision':payload['decision']})
        return dict(recorded=True)
