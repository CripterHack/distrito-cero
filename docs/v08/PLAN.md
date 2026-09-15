# Presencia v0.8 · Integración sobre Horizonte

## Objetivo
Unificar el reparto humano, los ocupantes y las acciones de acceso al coche sobre la fuente exacta Horizonte v0.7. Mantener semilla, streaming, atlas, campaña, interacciones y respuesta policial. Esta entrega no se rotula AAA: esa es la meta artística, no un resultado certificado.

## Unidades y aceptación
1. **Ocupación autoritativa**. Nuevo `occupancy.js` después de FrontierSimulation. Reservar asiento y puerta, acercamiento con camino validado, abrir, tirar del ocupante (cuando exista), entrar, sentarse y cerrar. Transferir control sólo al final. Cancelación no duplica ocupantes, guarda una posición segura, no concede inmunidad policial y bloquea viaje rápido. Mantener IDs de flota al importar. Validación de guardado antes de mutar estado.
2. **Reparto compartido**. `cast-renderer.js` reutiliza geometría humana con dos LOD adicionales y paletas por instancia en una textura GPU. No crear un conjunto de draw calls por cada peatón. Conductores civiles/policiales visibles y cristales en pasada transparente. La sombra usa la misma pose.
3. **Anatomía y lectura**. Afinar proporciones faciales, párpados, pupilas, nariz, cabello, pliegues y material cutáneo con recursos originales. No disfrazar shaders procedurales de escaneo fotográfico. Evitar ojos esféricos sobresalientes y el brillo uniforme de maniquí.
4. **Respuesta**. NPC desalojado reacciona y se aleja, manos con objetivos de contacto durante acceso, fase cancelable visible. Cámara mantiene al jugador y el coche en cuadro sin impedir control manual.
5. **Pruebas y entrega**. Pruebas de estado primero, luego lógica, teclado real, secuencia ocupada/vacía, viaje lejano, cancelación y guardado. Capturas de cada fase, vídeo corto real si el entorno permite grabación. No usar resultados históricos como verificación actual.

## Límites
La ciudad mantiene geografía y presupuesto de v0.7. Sin nuevos paquetes, servicios obligatorios ni runtime externo. Animaciones por curvas y objetivos, no mocap ni ragdoll físico. No hay agresiones detalladas ni sangre. Los NPC comparten familia de modelos con variaciones, no rostros escaneados únicos. No se promete rendimiento de GPU real a partir de SwiftShader.
