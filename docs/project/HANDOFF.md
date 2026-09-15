# Handoff · continuidad de brazos y equipamiento óptico

## Base y avances anteriores

Se retomó master `ac3cf5b3ef78e42f50eee173a8200b9e3d2e4286` (PR #12). #2/#3/#4 cerrados para QA portable, guardados HTTP nativos y recuperación WebGL. #5 tiene el benchmark técnico integrado por PR #11, pero no aprobación artística global. #6 conserva la corrección de pesos de mangas y puños. GitHub Pages sirve master por configuración del usuario.

## Unidad actual de #6

Recuperado y verificado el trabajo óptico que había quedado sin publicar. Binoculares usaban la referencia genérica de codo y, cerca de la cara al agacharse, su plano de flexión resultaba mal condicionado. Se añadieron referencias locales específicas para codos ópticos y una elevación/bajada visual más gradual. No cambian anclas palmares, huesos, mallas, pesos, recargas o tiempos de armas de fuego.

Leer [OPTICAL-POSTURE.md](OPTICAL-POSTURE.md) y [plan de la unidad](../../specs/003-weapon-contact/plan-optics.md). HTML actual: 8,851,747 bytes, SHA-256 `fe47dfa3ef9b2bff6d415b6f6fb0b64e0d0b0c0df7193b135c59e4fc3fe7b93b`. Asset humano sigue siendo `a4f5a6522f0012290bd2fca8d573ca5243388474f72fb026cf5766924e3c8b7d`.

Ocho regresiones nuevas: seis fallaron sobre la base y todas pasaron después. La muestra superior de chaqueta también se verifica durante el ciclo. La suite `optical` tiene catorce comprobaciones de navegador y trece capturas con tiempo controlado. Se mantiene separada del guardado nativo. La CI ordinaria exige óptica, manejo y recuperación; el workflow de personajes y el job HTTP siguen activos. No queda workflow temporal de aplicación ni parche de transporte en el árbol final.

## Evidencia y alcance

Ejecución local sobre el hash nuevo: 354 tests Node, receta de mangas, build/export y 14/51/22 checks de óptica/manejo/recuperación. La ejecución local tenía cambios sin commit; su manifiesto registra el commit base junto con el hash de HTML nuevo. No presentarla como una ejecución del commit base intacto. Los checks del PR vuelven a ejecutar sobre su HEAD exacto.

Las capturas recuperadas antes/después orientan la revisión visual, pero no sustituyen la nueva evidencia del navegador. No se afirma rendimiento físico, mocap, alineación exacta del ojo al ocular ni ausencia de toda intersección. El cambio de postura óptica no es una remodelación del hombro ni una nueva animación para todas las armas.

## Siguiente unidad

#6: medir contactos y continuidad de falanges en empuñadura/apoyo y fases de recarga por familia. Mantener el montaje único y las referencias palmares mientras se localizan penetraciones de dedos. Validar no sólo el destino de muñeca sino la superficie visible, sin alterar munición/daño para corregir la imagen. La región superior de axila/hombro todavía puede requerir correctivos anatómicos; hacerlo por separado de anclas.

#5: registrar criterios artísticos y autoría del modelo aprobado, sin convertir un benchmark verde en aprobación hiperrealista. #7: implementar y validar la vertical slice cuando sus gates de escena/mundo estén listos; no cerrar por redacción o teletransportes.

## Comandos de entrada

```sh
python3 tools/rebind_garment.py --check
python3 tests/garment_binding.test.py
python3 build.py
node --test tests/*.test.cjs
python3 -m tools.qa.run --suite optical --suite handling --suite recovery --headed
python3 -m tools.qa.run --suite characters --headed
python3 -m tools.qa.run --suite native --origin http --headed
```

Ejecutar además exportación GLB, tests del harness y contratos según QA.md. Leer HEAD remoto antes de cambiar, trabajar en rama y preservar qa histórico/SOURCE-MANIFEST. Integrar sólo tras CI/revisión y comprobar el hash servido por Pages. No cambiar origen, permisos o formato de partidas.
