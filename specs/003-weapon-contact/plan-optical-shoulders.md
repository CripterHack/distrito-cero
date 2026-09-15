# Unidad: plano de flexión estable para observación óptica

Base: `ac3cf5b`. Refs #6. El análisis del ciclo de hombro/axila localizó una inversión del codo en binoculares, por lo que esta unidad corrige ese caso antes de modificar otra vez pesos o anatomía.

## Contrato

Mantener anclas palmares, longitudes, malla y pesos, zoom, inventario, control de armas y guardados. Permitir una referencia de flexión específica de los binoculares y un ajuste explícito de su ritmo visual de subida/bajada. No implantar otro montaje de equipo ni un rig nuevo.

## Tareas y aceptación

1. Reproducir el barrido agachado y la bajada de pie. Medir codos y superficie de la prenda además de muñecas.
2. Escribir pruebas del plano, continuidad temporal, longitudes, determinismo, otras familias e inventario. Confirmar fallos con las fuentes anteriores.
3. Definir la referencia óptica desde su perfil, sin cambiar los contactos de otras familias.
4. Acotar la velocidad de presentación óptica por separado de las armas de fuego.
5. Validar barrido uniforme (independiente de cadencia), pasos reales de 1/60 y cuadrícula de elevación/crouch. Los límites miden continuidad, no contacto físico de tejidos.
6. Ejecutar la nueva suite WebGL, manejo, recuperación, personajes y persistencia nativa separada. Conservar imágenes comparables.
7. Registrar resultado y límites en docs/issue. Integrar sólo después de CI, revisar el HTML servido por Pages.

## Estado de la unidad

La implementación está vinculada a sus pruebas y documentación en [OPTICAL-SHOULDERS.md](../../docs/project/OPTICAL-SHOULDERS.md). Consultar el PR para el commit y los runs de aceptación. Las pruebas numéricas no aprueban por sí mismas la calidad artística de #5. Esta unidad tampoco termina todo #6 ni crea la vertical slice #7.
