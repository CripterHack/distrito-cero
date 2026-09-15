# Distrito Cero v0.14 · Equilibrio cervical

## Abrir y conservar partidas

Abrir el HTML en un navegador con WebGL2, fuera de la vista previa del chat. Es autónomo y no necesita recursos de red durante la partida. Para publicarlo en hosting estático, el mismo archivo puede llamarse `index.html`.

Antes de cambiar desde v0.13, abrir **Mis partidas → Exportar respaldo**. En v0.14 utilizar **Importar JSON**. Las importaciones añaden espacios, no reemplazan otros sólo porque sus nombres coincidan. No se cambia el esquema ni la clave del catálogo. Los doce espacios están sujetos al almacenamiento disponible, no son una promesa de cuota ilimitada. No hay sincronización en nube.

## Revisar el cuello

Abrir **Crear personaje**, o **Pausa → Editar personaje** en una sesión existente. En las herramientas de revisión, seleccionar el enfoque **Cuello y hombros**. Las nuevas poses son:

* **Cuello · giro suave:** giro alternado de cabeza y cuello con inclinación lateral moderada.
* **Cuello · flexión y extensión:** revisión de la unión bajo la mandíbula al mirar ligeramente arriba y abajo.

La velocidad del estudio puede reducirse a **0.25×** o **0.5×**. No cambia la velocidad de la partida. Arrastrar permite orbitar y la rueda permite acercarse. La luz lateral hace más visibles el contorno y las transiciones. El ajuste de grosor ahora acompaña la abertura de la chaqueta y no ensancha el mentón.

El editor sigue siendo un borrador aislado. Cancelar no modifica la sesión. Comparar con el inicio no destruye los cambios. Aplicar guarda la apariencia del borrador en la partida activa si la escritura se completa. Las poses y peticiones de giro de la vista previa no se serializan.

## Qué corrige

El abultamiento lateral bajo la mandíbula, la mezcla incorrecta de influencias sobre el mentón, la discontinuidad visual entre cuello y rostro y el cambio de grosor sin acompañamiento de la prenda. Los hombros vestidos reciben una modificación moderada de su caída. Todas las familias de personajes comparten estas mejoras, con pose individual por actor.

No se añadió una nueva familia facial, pelo físico, contacto de falanges, mocap ni ropa física. Las manos y los dedos conservan su geometría y sus controles anteriores. El personaje sigue siendo estilizado y no iguala una referencia de escultura hiperrealista.

## Controles que permanecen

WASD o flechas: caminar/conducir. Shift: correr. F: iniciar o cancelar acceso al vehículo. E: interactuar. G: lanzar/empujar. X: agacharse. Q: esquivar. Espacio: salto/freno. V mantenida: reparación. R mantenida: rendición. M: atlas. P: fotografía. Esc: pausa.

La campaña, el territorio continuo, la ocupación, la extracción de conductores, la captura policial y las reparaciones mantienen sus reglas. Esta entrega no cambia el modo en que las colisiones físicas resuelven una situación.

## Límites de los archivos 3D y las pruebas

El GLB actual contiene el personaje neutral y once estudios procedurales. No es una exportación de cada avatar personalizado ni de todas las interacciones de la simulación. Un visor que utilice skinning lineal puede deformarlo de modo distinto a los cuaterniones duales del juego.

Se probaron Chromium con gráficos por software, viewports móviles y eventos táctiles emulados. No se probaron dispositivos físicos, Safari ni guardado nativo después de cerrar/reabrir archivos locales. Exportar JSON antes de cambiar de versión, navegador o equipo.
