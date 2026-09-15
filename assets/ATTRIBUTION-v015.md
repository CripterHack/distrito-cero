# Procedencia · Integración cervical v0.15

Esta entrega deriva de v0.14, sin nuevos recursos remotos. La cabeza y el atlas de piel conservan los orígenes y las licencias descritos en ATTRIBUTION-v09.md y las revisiones posteriores: MakeHuman HM08 y target adulto CC0, Aksel Skin por Mindfront CC0. No es un escaneo nuevo. La ropa, manos, ojos, cabello, esqueleto y animación conservan su autoría nativa y documentada.

Cambios originales de v0.15: perfil cervical con volumen lateral, garganta/nuca diferenciadas, inserción inferior ensanchada, abertura de prenda y cierre adaptados; distribución oblicua de influencias bajo mandíbula; vinculación acotada de complexión y grosor cervical; normales del morph de complexión mediante su Jacobiano. Las medidas son una decisión artística para esta familia de malla, no promedios antropométricos poblacionales.

El constructor offline `tools/integrate_cervical_v015.py` parte de `assets/hero-v014-baseline.js`. No sobrescribe ese insumo. No requiere nuevas descargas o servicios. No se realizó una nueva operación de autoría en Higgsfield ni se atribuye la geometría nueva a dicho servicio.

`assets/dc015-human-integrated.glb` contiene el avatar neutral con la malla real nueva y once estudios procedurales. Conserva mapa de color, normales y rugosidad facial. El DQ del runtime, los parámetros de apariencia, el material cervical específico, la mirada, el parpadeo y el acceso a vehículos no se exportan como funciones completas del GLB. El visor externo puede usar skinning lineal. No se redistribuyen tipografías.
