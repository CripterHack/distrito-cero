# Recursos de v0.14 · Equilibrio cervical

La cabeza sigue derivando de MakeHuman HM08 y el target adulto, y conserva el atlas de Aksel Skin de Mindfront, según la procedencia y licencias conservadas en `ATTRIBUTION-v09.md`. Las atribuciones de v0.10, v0.12 y v0.13 continúan aplicándose. No se descarga ni importa un escaneo nuevo y no se atribuye esta entrega a una nueva operación en Higgsfield.

`hero-v013-baseline.js` conserva los bytes de la geometría original de v0.13. `refine_cervical_v014.py` modifica el perfil de la región cervical sobre esa topología, pondera por separado la mandíbula, el cuello y la inserción torácica, recalcula normales y baja moderadamente el borde del hombro vestido. Son correcciones originales de dirección artística, no anatomía clínica ni fotogrametría corporal.

Las otras once partes permanecen idénticas a la geometría base, incluidas manos, uñas, cabello y prendas inferiores. No se presenta una nueva anatomía de manos. El nuevo comportamiento de cabeza/cuello y las normales del ajuste personalizable son código original.

`dc014-human-cervical.glb` es la exportación actual: personaje neutral, 49 huesos, 13 mallas, tres mapas PNG y once estudios procedurales. Los GLB con prefijos anteriores son históricos. El shader DQ, el material cervical procedural, los ajustes de apariencia, parpadeo y secuencias de acceso no se replican íntegramente en un visor glTF convencional.

No se incorporan archivos tipográficos. Las tipografías utilizadas para los rótulos de capturas no se redistribuyen.
