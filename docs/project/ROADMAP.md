# Plan de desarrollo hacia una calidad visual y jugable superior

## Estrategia

La base v0.19 tiene amplitud funcional. La siguiente etapa debe aumentar **consistencia, fiabilidad y calidad por escena**, no volver a expandir el catálogo antes de estabilizar lo existente. La meta es acercar la presentación y el comportamiento a una producción de alta calidad dentro de las restricciones del navegador. «AAA» expresa una aspiración, no un estado alcanzado, una certificación ni una promesa de presupuesto o plazo.

Se propone construir una **vertical slice de 10 a 15 minutos** con un personaje personalizable, una calle, un interior pequeño, dos vehículos y un recorrido que incluya observación, interacción, conducción y consecuencias. Esa muestra fija la calidad mínima que después se replica en regiones. Ninguno de estos contenidos nuevos se declara implementado por estar en este plan.

No hay fechas comprometidas. Cada hito termina al cumplir su puerta de aceptación. Estimaciones y hardware se fijan tras medir la primera ejecución reproducible.

## Orden y dependencias

| Hito | Prioridad y dependencia | Resultado concreto | Puerta para avanzar |
| :--- | :--- | :--- | :--- |
| M0 · Base en repositorio | P0, realizado en la publicación | Fuentes completas, activos, build, documentación y CI inicial | Clon recuperable, hashes del juego iguales y comprobaciones de CI |
| M1 · Fiabilidad del laboratorio y datos | P0, M0 | Pruebas portables, almacenamiento nativo y fallos gráficos controlados | Recarga real sin pérdida de partida, informes no obsoletos y fallo verificable |
| M2 · Personaje patrón | P1, medición inicial de M1 | Anatomía aprobada, materiales, cabello y conjunto de poses | Revisión frontal/perfil/3⁄4 en luz neutra, deformación y presupuesto |
| M3 · Contactos y animación | P1, M2 rig estable | Palmas/dedos, equipo, apoyos, asientos y transiciones | Sin saltos ni penetraciones visibles en la matriz acordada |
| M4 · Dirección visual de entorno | P1, M1/M2 | Calle patrón, materiales e iluminación coherentes | Personaje, vehículo y entorno se perciben del mismo mundo |
| M5 · Sistemas de mundo fiables | P1, M1 y benchmark | Streaming acotado, topografía y vías por contratos | Sin agujeros ni cambios por orden de carga; coste medido |
| M6 · Vehículos, peatones y policía | P1, M3/M5 | Navegación, percepción y respuestas legibles | Situaciones reproducibles, escapes posibles y recuperación de bloqueo |
| M7 · Vertical slice | P1, M2–M6 | Recorrido completo con misión, audio y opciones de resolución | Inicio a fin con guardado/reanudación y playtest externo |
| M8 · Optimización y accesibilidad | P1, transversal, cierre tras M7 | Perfiles de calidad, inputs y dispositivos objetivo | Presupuestos medidos, controles operables, datos protegidos |
| M9 · Beta y lanzamiento controlado | P2, todos los gates | Paquete, licencia decidida, QA prolongada y soporte | Cero bloqueadores conocidos del alcance anunciado y rollback probado |

## M0. Publicación y continuidad

Conservar la v0.19 como base recuperable, sin volver a etiquetar una misma entrega como dos versiones. El repositorio ya contiene los archivos del ZIP original. La documentación vigente queda separada de `docs/v*`. Retirar el importador de una sola vez y dejar CI con permisos mínimos. La rama principal continúa siendo master.

No confundir la CI básica con una validación integral de producto. Este hito asegura que el siguiente agente puede construir, comprobar y entender lo entregado.

## M1. Fiabilidad antes de otra revisión visual

Crear un lanzador de QA con navegador y directorio de salida configurables. Conservar el modo de fixtures existente, pero añadir origen HTTP local real, almacenamiento persistente y cierre/reapertura del contexto. Probar importación inválida, cuota, conflicto entre pestañas y recuperación de una partida, sin escribir datos de usuarios.

Definir lifecycle de WebGL: detener el dibujo durante pérdida de contexto, conservar simulación/partida, reconstruir recursos cuando vuelva y mostrar un estado claro si falla. No esconder errores de shader tras un bucle infinito. Añadir un ensayo de crecimiento de recursos al viajar entre sectores.

**Salida:** especificación 001, harness portable, casos de datos y pruebas de recuperación. Las pruebas de imágenes siguen siendo evidencia separada del almacenamiento nativo.

## M2. Personaje patrón y aprobación anatómica estable

Antes de retocar nuevamente cuello, fijar referencias métricas y artísticas del personaje vestido y de su inserción cervical. Revisar cabeza, mandíbula, cuello, clavículas, deltoides, tórax, muñecas, palmas, dedos y pies en un conjunto fijo de cámaras. Mantener variantes de complexión válidas como conjunto, no corregir sólo el preset neutral.

La receta de autoría debe permitir editar superficies y pesos, no obligar a manipular buffers empaquetados. Incorporar piel con tratamiento consistente de color/normal/rugosidad, ojos y párpados coherentes, cabello de mejor silueta con presupuesto de transparencia y prendas con costuras apoyadas. Evaluar correctivos locales para hombro/codo/agarre antes de introducir física completa.

Definir una base aprobada y un registro de decisiones visuales. Un cambio de proporción posterior necesita el mismo panel de comparación, no una sola captura favorecedora. Assets nuevos requieren licencia y autorización si implican gasto.

**Salida:** especificación 002, matriz de 12 poses, cuatro proporciones y tres luces, evidencia antes/después y coste por LOD.

## M3. Animación y contactos integrados

Mantener una única referencia para el montaje de equipo y el actor. Ampliar contactos desde palma a zonas de falanges cuando aporte visibilidad real. Añadir correcciones de codo, clavícula y muñeca sin estirar huesos. La alineación ojo/mira es una restricción visual adicional, no motivo para deformar la cara.

Separar las fases de cada interacción: anticipación, contacto, acción, liberación y recuperación. Las cancelaciones deben poder entrar desde todas las fases sin munición doble, salto de pose o duplicación de actores. Aplicar la misma lógica a manos libres, herramientas, binoculares, coche y carga de props.

Para locomoción, estabilizar apoyos, arranque, frenada, giro en el sitio y paso lateral. Las transiciones deben seguir velocidad y trayectoria reales. Captura de movimiento sólo si existe un recurso autorizado y se verifica el retarget, no como etiqueta para oscilaciones procedurales.

**Salida:** especificación 003, matriz de familias/poses/cancelaciones y vídeo temporal continuo del motor.

## M4. Escena patrón de materiales e iluminación

Construir una calle compacta que reúna piel, pelo, tela, pintura, vidrio, metal, asfalto y vegetación. Revisar escala, roughness, exposición, tonos y sombras con referencias compartidas. Corregir mezcla de espacios de color, aliasing, sobreexposición y sombras de contacto antes de añadir más efectos.

Añadir decoración que explique el uso del lugar: accesos, señalización, iluminación funcional, desgaste coherente y zonas peatonales. El futurismo debe tener una lógica de infraestructura, no ser sólo neón aleatorio. La variante rural debe cambiar densidad, materiales y equipamiento, no sólo la altura de edificios.

**Salida:** escena patrón reproducible, lista de materiales y presupuestos. Ningún renderer nuevo se introduce sin comparar coste y compatibilidad.

## M5. Mundo continuo con reglas espaciales

Desacoplar generación y subida a GPU del ritmo de juego mediante trabajos acotados o Worker. Mantener generación determinista e identificadores persistentes. Medir tamaño del vecindario, tiempo por sector y descargas de buffers antes de modificar el radio activo.

Diseñar altura de terreno, carreteras, parcelas y edificios sobre un mismo contrato de muestreo. Las vías deben resolver pendientes y conexiones en bordes. Ríos, puentes y túneles son fases posteriores, no añadidos superficiales encima de una malla sin navegación. La ruta y colisión deben consultar la misma superficie.

**Salida:** tests de vecindad/orden de carga, 30 minutos de recorrido automatizado y medición de recursos. Continuar usando el centro de campaña sin cambiar sus posiciones silenciosamente.

## M6. Ciudad reactiva y comportamiento legible

Peatones: rutas transitables, evitación, cruces y reacciones a tráfico/ruido/amenaza. Policía: percepción y última posición conocida coherentes, comunicación de búsqueda y oportunidades de escape. Vehículos: frenada, esquiva, contactos, atasco y recuperación sin empujar al jugador indefinidamente.

Destrucción: material, masa visual, umbral, caída, sonido y persistencia deben corresponder. Evitar explosiones o derribos meramente decorativos que dejan un colisionador invisible. No convertir todo edificio en destruible hasta disponer de presupuestos y navegación posteriores al daño.

**Salida:** escenarios reproducibles de cruce, persecución, incidente, cancelación de acceso y bloqueo con solución. Combate armado de NPCs requiere su propia especificación de percepción/justicia y no se da por hecho.

## M7. Muestra jugable completa

Crear un encargo original que lleve de un barrio urbano a una periferia y ofrezca observación con binoculares, interacción con NPC, elección de vehículo, obstáculo y resolución. Se propone una alternativa de sigilo/tecnología además de confrontación, sin imponer una solución única. El cierre comunica consecuencias y permite guardar/reanudar.

Añadir audio situacional, mezcla, pasos por superficie, motores, UI y señales de estado. No se añade música o voz ajena sin permiso. Un playtest inicial de cinco personas es un objetivo de investigación: registrar problemas y repetir tras correcciones, no convertir ese tamaño en evidencia estadística general.

**Salida:** especificación 004 y recorrido completo sin teletransportar a objetivos. El objetivo de 10–15 minutos es de diseño y se valida observando a jugadores.

## M8 y M9. Pulido, beta y publicación responsable

Revisar teclado/ratón/táctil, remapeo, tamaño de objetivos, contraste, subtítulos, movimiento reducido, sensibilidad y conflictos entre cámara y UI. Medir perfiles de calidad en hardware identificado. Separar fallo de GPU, error de código y saturación de generación.

Congelar alcance de beta, probar guardados anteriores y recuperación, completar documentación y decidir licencia y canal de distribución. La monetización sólo se evalúa después de una muestra confiable, sin prometer ingresos. Donaciones opcionales, distribución estática o licencia comercial son propuestas que requieren aprobación.

No planificar multijugador, tráfico masivo o más ciudades como condición para esta beta. Son líneas posteriores y necesitarían arquitectura y especificaciones propias.

## Regla de priorización

Primero pérdida de datos/crashes, luego acciones bloqueadas, después incoherencias visibles y coste, al final variedad. Una revisión anatómica de alta visibilidad puede avanzar en paralelo con QA si no altera contratos compartidos. No abrir más de dos grandes frentes que modifiquen rig/renderer simultáneamente.
