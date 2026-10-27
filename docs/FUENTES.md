# Contrato de fuentes simuladas

La interfaz abstracta `MeasurementSource.fetch(units, days, scenario)` recibe el
alcance previamente validado. Devuelve observaciones independientes con:

- `unit_id`: identidad existente de una unidad seleccionada.
- `day`: date dentro del intervalo solicitado.
- `distance` y `energy`: números finitos no negativos.
- `zero_confirmed`: evidencia explícita de que la actividad cero fue observada.

`LaboratorySource` implementa el contrato mediante fórmulas propias y deterministas.
No lee un archivo operacional, una sesión del navegador ni un servicio de red.
No importa clientes de proveedores externos ni conserva selectores de páginas.

| Escenario | Construcción sintética |
|---|---|
| steady | Distancia base 64 km más variaciones por posición y día; energía proporcional |
| zero | Segundo día con distancia y energía cero, explícitamente confirmados |
| missing | Omisión deliberada del tercer día |
| warning | Cuarto día con energía elevada |
| duplicate | Repetición idéntica de la primera observación |
| conflict | Dos distancias distintas para la primera identidad/fecha |
| mixed | Combina ausencia, cero, advertencia y duplicado idéntico |

Los números son inventados, no valores calibrados contra una flota real. No tienen
valor predictivo y no se deben interpretar como desempeño de un vehículo comercial.
El período inicial usa abril de 2032 para hacer visible su carácter ficticio.

Otro proveedor de laboratorio puede implementar la misma interfaz y entregarse a
`FleetWorkspace(database, source=...)`. Las reglas se mantienen fuera del proveedor.
Cualquier integración real requeriría un desarrollo separado y autorización expresa;
no forma parte de este código ni está habilitada mediante configuración.

Los efectos se aplican únicamente si el período incluye los días indicados. El
nombre de un escenario no fuerza por sí solo una advertencia: esta depende de las
observaciones recibidas y de la cobertura real del alcance sintético solicitado.
