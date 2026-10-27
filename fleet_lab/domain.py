# Original domain rules for a synthetic fleet laboratory.
from datetime import date, timedelta
import math
import re

class InputFault(ValueError):
    pass

def clean_text(value, field, limit=100):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise InputFault(f'{field}: se requiere un texto de hasta {limit} caracteres.')
    if any(ord(c) < 32 for c in value):
        raise InputFault(f'{field}: contiene caracteres de control.')
    return value.strip()

def parse_day(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise InputFault('Fecha inválida. Utiliza AAAA-MM-DD.') from None

def shape_unit(payload):
    allowed = {'id', 'plate', 'internal_key', 'lookup_key', 'label', 'active'}
    if not isinstance(payload, dict) or set(payload) - allowed:
        raise InputFault('Campos de vehículo no reconocidos.')
    plate = clean_text(payload.get('plate'), 'Patente ficticia', 30).upper()
    if not re.fullmatch(r'DEMO-[0-9]{3,6}', plate):
        raise InputFault('La patente debe ser ficticia: DEMO- seguido de 3 a 6 dígitos.')
    active = payload.get('active', True)
    if not isinstance(active, bool):
        raise InputFault('El estado debe ser verdadero o falso.')
    return dict(plate=plate, internal_key=clean_text(payload.get('internal_key'), 'Identificador interno', 40),
        lookup_key=clean_text(payload.get('lookup_key'), 'Clave de consulta', 60),
        label=clean_text(payload.get('label'), 'Nombre ficticio', 100), active=active)

def inclusive_days(start, end):
    a, b = parse_day(start), parse_day(end)
    if b < a or (b-a).days > 61:
        raise InputFault('El período debe contener entre 1 y 62 días consecutivos.')
    return [a+timedelta(days=n) for n in range((b-a).days+1)]

def normalize_observations(observations, selected, days):
    keys = {u['id'] for u in selected}; window = set(days)
    warnings = []; unique = {}
    for row in observations:
        if row.get('unit_id') not in keys or row.get('day') not in window:
            raise InputFault('La fuente simulada devolvió un vehículo o fecha fuera del alcance.')
        for key in ('distance', 'energy'):
            v = row.get(key)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise InputFault('Las métricas deben ser números finitos no negativos.')
        pair = (row['unit_id'], row['day'])
        if pair in unique:
            if unique[pair] != row:
                raise InputFault('Conflicto: dos valores distintos para el mismo vehículo y día.')
            warnings.append('Se descartó un duplicado idéntico de la fuente simulada.')
            continue
        if row['distance'] == 0 and not row.get('zero_confirmed'):
            raise InputFault('Un cero requiere confirmación explícita de la fuente simulada.')
        unique[pair] = row
        if row['energy'] > max(row['distance'], 1)*1.4:
            warnings.append('Consumo elevado en una observación sintética; revisar su contexto.')
    missing = len(selected)*len(days)-len(unique)
    if missing:
        label = 'observación' if missing == 1 else 'observaciones'
        warnings.append(f'Período incompleto: {missing} {label} sin información. No se rellenaron con cero.')
    return sorted(unique.values(), key=lambda r: (r['day'], r['unit_id'])), list(dict.fromkeys(warnings))
