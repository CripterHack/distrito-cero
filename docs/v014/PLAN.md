# Distrito Cero v0.14 · revisión cervical

Base exacta: v0.13 Movimiento orgánico, SHA-256 2cfc9ae5cc85087d8d21ded739a10c955cce37b831f029467e314b25acdefbc3.

Prioridad autorizada: corregir el cuello extraño y continuar el pulido corporal/animación sin reemplazar los sistemas existentes. No se anunciará fotorrealismo por contar polígonos o pruebas.

## Diagnóstico inicial
La cabeza HM08 y su extensión cervical tienen un estrechamiento medio seguido de una protuberancia lateral bajo la mandíbula (semiancho de hasta 60 mm entre y=1.545 y 1.570 m). La forma y el sombreado son discontinuos. Los pesos se asignan sólo por altura, de modo que la mandíbula baja puede girar con el cuello. La personalización ensancha también parte de la mandíbula pero no la abertura de la prenda. La normal del morph omite su derivada vertical, y el material del cuello cambia de función bruscamente a y=1.56.

## Ejecución
1. Conservar fuente y geometría iniciales. Reproducir artefactos y escribir pruebas de contorno, pesos, morfología y movimientos cervicales.
2. Reconstruir el perfil cervical sobre su topología continua, con contorno posterior y submandibular independiente. Suavizar la transición, conservar labios/orejas/ojos y usar influencias repartidas por región anatómica.
3. Corregir el ensanchamiento de cuello y abertura, incluyendo normales derivadas del morph. Unificar el sombreado bajo la mandíbula sin saltos de material.
4. Coordinar cuello y cabeza con límites de movimiento. Añadir un estudio de movilidad cervical en el creador, sin modificar simulación, partidas ni física. Conservar alcance de manos y apoyo de pies.
5. Comprobar antes/después frontal, lateral, giro, manos, carrera, conductores y reparto. Regresión Node, geometría, editor/guardados, campaña y bucle continuo WebGL.
6. Construir HTML, exportar GLB, documentar procedencia y límites, verificar manifiesto y entregar archivos existentes.

Referencias anatómicas de orientación artística, no modelo médico: OpenStax Anatomy and Physiology 2e, sección 11.3. Exportación portátil: Khronos glTF 2.0.
