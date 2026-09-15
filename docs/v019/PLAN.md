# Distrito Cero v0.19 · Contacto articulado

Continuación autorizada del manejo v0.18. Modificación acotada del sistema de contactos existente.

## Diagnóstico
Los objetivos actuales son muñecas estimadas. La palma izquierda del arma larga queda desplazada respecto de la cara inferior del guardamanos. El índice se cierra sólo por apuntar. Culata y postura del tórax no comparten referencia. La misma flexión de soporte persiste mientras la mano viaja a la recarga.

## Diseño a implementar
1. Anclas de superficie por familia y marco de orientación ortonormal. Derivar el objetivo de muñeca desde una referencia palmar canónica, no usar el mismo punto para palma y muñeca.
2. Postura de apoyo torácico y montaje al hombro para largas, con alcance conservador de brazos. Polos de codos consistentes. Ajuste del antebrazo opcional, preservando contactos anteriores.
3. Perfiles de flexión por rol y separación del índice de apuntado/disparo. Apertura en trayectos libres y cierre durante contacto con la recarga.
4. Desplazamiento y rotación del cargador/celda desde la misma trayectoria que su ancla palmar. Una sola pieza visible. Recarga por fases sin cambiar tiempos o inventario.
5. Inercia de orientación pequeña y amortiguada, recuperación por familia, respeto a pausas. Entrada y salida de apuntado sin mover manos y arma por separado.
6. Geometría del agarre de armería suavizada donde mejora la superficie de contacto. Recursos nativos compartidos, sin dependencias ni ingeniería de armas reales.

## Condiciones
Conservar catálogo, inventario, perfiles, pelo, guardados, campañas, policía y territorio. No confundir herramienta cinemática con colisión completa por falange. No añadir combate autónomo de NPCs. La transparencia y bloqueo de controles del selector siguen vigentes. Entrega: HTML, fuentes, evidencias del renderer y guía de límites.

## Verificación
Pruebas previas fallidas sobre contactos palmares y su alineación real en rig. Muestreo de todos los equipos y fases, orientación, continuidad, alcance, pureza y persistencia. Regresión completa de Node, suites actuales de manejo/arsenal/catálogo/campaña y bucle real. Capturas con idéntico encuadre antes/después, vídeo corto con tiempo controlado. No afirmar fotorrealismo ni FPS de GPU real.

## Ajustes encontrados al implementar

Se añadieron al alcance dos correcciones de continuidad del sistema existente: empezar la elevación del arma al equipar/restaurar antes del primer render, y retener sólo la mezcla visual al cerrar el selector. Se mantuvo la cancelación estricta de disparos. También se corrigió la rotación completa de una referencia local del hombro. Los registros fallidos y posteriores están en `qa/v019`.
