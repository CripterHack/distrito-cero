# Recursos de v0.13

Las atribuciones de v0.9, v0.10 y v0.12 siguen vigentes. MakeHuman HM08 y el target adulto suministran la cabeza, Aksel Skin (Mindfront) los mapas faciales, con las transformaciones documentadas en sus archivos anteriores. Prendas, manos, ojos, cabello y animación son recursos procedurales originales del proyecto. No se incorporan recursos descargados nuevos ni se atribuye este trabajo a una operación nueva de Higgsfield.

`hero-v012-baseline.js` es la geometría exacta de la entrega anterior. `polish_surface_v013.py` conserva topología, posiciones de manos y sus pesos, cara y mapas; sólo modifica posiciones/normales de zonas de prendas y las normales de piel de manos compartidas. El GLB actual exporta estas mallas y la pose del nuevo controlador nativo.

No es mocap ni fotogrametría corporal. `organic-export.json` describe el GLB actual. Los GLB dc09, dc010 y dc012, si presentes, son históricos y no contienen este movimiento.
