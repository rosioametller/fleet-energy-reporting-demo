# Providers receive an explicit scope and return independent synthetic measurements.
from abc import ABC, abstractmethod
from .domain import InputFault

SCENARIOS = {'steady', 'zero', 'missing', 'warning', 'duplicate', 'conflict', 'mixed'}

class MeasurementSource(ABC):
    @abstractmethod
    def fetch(self, units, days, scenario):
        raise NotImplementedError

class LaboratorySource(MeasurementSource):
    def fetch(self, units, days, scenario):
        if scenario not in SCENARIOS:
            raise InputFault('Escenario sintético desconocido.')
        rows = []
        for index, unit in enumerate(units):
            for step, day in enumerate(days):
                if scenario in {'missing', 'mixed'} and step == 2:
                    continue
                distance = float(64 + index*11 + step*3)
                energy = round(distance*0.48, 2)
                zero = scenario in {'zero', 'mixed'} and step == 1
                if zero: distance = energy = 0.0
                if scenario in {'warning', 'mixed'} and step == 3: energy = distance*1.8
                rows.append(dict(unit_id=unit['id'], day=day, distance=distance,
                    energy=energy, zero_confirmed=zero))
        if rows and scenario in {'duplicate', 'mixed'}: rows.append(dict(rows[0]))
        if rows and scenario == 'conflict': rows.append(dict(rows[0], distance=rows[0]['distance']+7))
        return rows
