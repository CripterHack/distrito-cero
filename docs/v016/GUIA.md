# Rasgos v0.16 · Guía

## Abrir y migrar

Abrir `index.html` en un navegador con WebGL2, fuera de la vista previa del chat. Todo el runtime y los mapas de piel están dentro del HTML. No se requiere el ZIP de código, el GLB ni una instalación de dependencias para jugar.

Antes de cambiar de versión, respaldar las partidas en la anterior mediante **Mis partidas → Respaldar todas**. Importar ese JSON en v0.16. Los nombres, progreso y opciones anteriores se conservan. Los estilos anteriores 0–3 siguen correspondiendo a corto, rapado, hacia atrás y sin cabello, aunque su geometría se ha mejorado. Los perfiles sin longitud cervical, volumen y vinculación de cejas reciben valores neutros.

El guardado continúa siendo local, con hasta doce espacios sujetos a cuota/permisos del navegador. No es sincronización en nube. Cambiar de ruta del HTML, navegador o dispositivo puede separar el almacenamiento, y borrar datos puede eliminarlo. Conservar respaldos JSON. No se anuncia persistencia nativa entre reaperturas de `file://` como comprobada en este laboratorio.

## Personalizar

Desde el menú inicial elegir **Crear personaje**, o desde Pausa elegir **Editar personaje**. El editor conserva un borrador: cancelar no aplica cambios, y comparar no destruye el borrador. Aplicar actualiza sólo la identidad de la partida activa.

**Longitud del cuello** acerca o separa ligeramente la cabeza respecto de la nueva base más corta. Incluso el extremo extendido es más corto que v0.15. Los ojos, orejas, labios y cráneo se trasladan juntos, no se escalan verticalmente. **Grosor del cuello** y **Complexión** siguen disponibles y controlan volumen. Estos ajustes no modifican fuerza, velocidad o cápsula de colisión.

### Cabello

Once opciones seleccionables: corto clásico, rapado, peinado hacia atrás, sin cabello, corto texturizado, degradado alto, media melena, flequillo lateral, undercut asimétrico, recogido corto y melena recta.

El selector **Volumen del peinado** hace cambios acotados en las piezas de cabello, sin modificar la cabeza. Se desactiva en rapado y sin cabello. Se mantienen los seis colores existentes. **Vincular cejas al color del cabello** permite acompañar el tinte; al desactivarlo, las cejas son castañas. Elegir sin cabello no elimina las cejas.

Cada estilo ya resuelve su combinación de laterales, coronilla y flequillo. Esta versión no añade un editor libre de hebras, longitud continua del cabello, simulación física ni prendas nuevas. El recogido está en la nuca: girar la vista para apreciarlo.

### Revisar movimiento

Usar **Revisar en movimiento → Inspección → Cuello y hombros**, y los estudios de giro/flexión. Hay reproducción 0.25×, 0.5× y 1×, además de luz neutra, lateral y exterior suave. Probar también carrera, conducción, manos y alcance. Los cambios de cámara/estudio no se guardan como atributos del personaje ni alteran el mundo activo.

## Partidas y controles conservados

**Mis partidas** permite cargar, renombrar, duplicar, guardar copia, buscar, ordenar, exportar e importar. La importación añade espacios, no reemplaza por coincidencia de nombre. El catálogo conserva la validación íntegra, las protecciones frente a fallos de escritura y los avisos de conflicto. Una sesión voluntaria sin guardado debe exportarse para conservarla.

WASD/flechas: desplazarse. Shift: correr. F: entrar, salir o cancelar acceso. E: interactuar. G: lanzar/empujar. X: agacharse. Q: esquivar/bocina. Espacio: salto/freno. V mantenida: reparar. R mantenida: rendirse. M: atlas. P: foto. Esc: Pausa. Los mandos táctiles existentes se conservan.

Los modelos y las animaciones siguen siendo estilizados. El cabello largo puede cruzar ropa o carrocería en poses extremas. No hay contacto físico individual de falanges, tela física, rig facial completo ni captura de movimiento. Cambiar el peinado no cambia el comportamiento del personaje.
