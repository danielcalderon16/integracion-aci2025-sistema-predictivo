"""
Endpoint de la calculadora de diseño de mezclas ACI 2025.

Recibe los parámetros del formulario, aplica la dosificación ACI 211.1
(services/aci_calculator.py) y guarda el resultado con un folio único.
Ese folio es la referencia que después usa /prediccion para alimentar
automáticamente al modelo de IA sin que el usuario vuelva a escribir
ningún valor (ver el mecanismo de integración en el README).
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.diseno import DisenoMezcla
from app.models.usuario import Usuario
from app.schemas.aci import DisenoMezclaInput, DisenoMezclaOut
from app.services.aci_calculator import calcular_diseno

router = APIRouter(prefix="/aci", tags=["aci"])


def _generar_folio() -> str:
    """Identificador legible y único por cálculo, ej. ACI-20261024220858-979241."""
    return f"ACI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"


@router.post("/calcular", response_model=DisenoMezclaOut, status_code=201)
def calcular(
    datos: DisenoMezclaInput,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Calcula el diseño de mezcla y lo deja guardado para el usuario autenticado."""
    resultado = calcular_diseno(datos)

    diseno = DisenoMezcla(
        usuario_id=usuario.id,
        folio=_generar_folio(),
        tipo_construccion=datos.tipo_construccion,
        condiciones_agresivas=datos.condiciones_agresivas,
        densidad_cemento=datos.densidad_cemento,
        tipo_cemento=datos.tipo_cemento,
        tamano_nominal_in=datos.tamano_nominal_in,
        masa_unitaria_grueso=datos.masa_unitaria_grueso,
        densidad_aparente_grueso=datos.densidad_aparente_grueso,
        absorcion_grueso=datos.absorcion_grueso,
        humedad_grueso=datos.humedad_grueso,
        modulo_finura=datos.modulo_finura,
        masa_unitaria_fino=datos.masa_unitaria_fino,
        densidad_aparente_fino=datos.densidad_aparente_fino,
        absorcion_fino=datos.absorcion_fino,
        humedad_fino=datos.humedad_fino,
        asentamiento_in=datos.asentamiento_in,
        contenido_aire=datos.contenido_aire,
        altura_cilindro=datos.altura_cilindro,
        diametro_cilindro=datos.diametro_cilindro,
        num_cilindros=datos.num_cilindros,
        porcentaje_lodo=datos.porcentaje_lodo,
        **resultado,
    )
    db.add(diseno)
    db.commit()
    db.refresh(diseno)
    return diseno
