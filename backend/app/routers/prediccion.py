"""
Endpoint de predicción de resistencia (núcleo del mecanismo de integración).

Recibe solo el id de un diseño ya calculado por /aci/calcular y, sin que el
usuario tenga que reingresar ningún parámetro, toma el cemento, el agua y
los agregados ya guardados en ese diseño y los pasa al modelo de IA
(services/ml_service.py) para generar la curva de resistencia a las edades
de curado solicitadas (por defecto 3, 7, 14 y 28 días).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user
from app.models.diseno import DisenoMezcla
from app.models.prediccion import Prediccion
from app.models.usuario import Usuario
from app.schemas.prediccion import PrediccionInput, PrediccionOut
from app.services.ml_service import predecir_resistencia

router = APIRouter(prefix="/prediccion", tags=["prediccion"])


@router.post("", response_model=list[PrediccionOut], status_code=201)
def generar_predicciones(
    datos: PrediccionInput,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Genera y guarda una predicción por cada edad de curado solicitada."""
    diseno = (
        db.query(DisenoMezcla)
        .filter(DisenoMezcla.id == datos.diseno_id, DisenoMezcla.usuario_id == usuario.id)
        .first()
    )
    if diseno is None:
        raise HTTPException(status_code=404, detail="Diseño de mezcla no encontrado")

    predicciones = []
    for edad in datos.edades_dias:
        resultado = predecir_resistencia(
            cemento_kgm3=diseno.factor_cemento,
            agua_kgm3=diseno.agua_mezclado,
            agregado_grueso_kgm3=diseno.peso_real_grueso,
            agregado_fino_kgm3=diseno.peso_real_fino,
            edad_dias=edad,
            escoria=datos.escoria,
            cenizas=datos.cenizas,
            superplastificante=datos.superplastificante,
        )
        prediccion = Prediccion(
            diseno_id=diseno.id,
            escoria=datos.escoria,
            cenizas=datos.cenizas,
            superplastificante=datos.superplastificante,
            edad_dias=edad,
            resistencia_predicha_mpa=resultado["resistencia_mpa"],
            extrapolado=resultado["extrapolado"],
        )
        db.add(prediccion)
        predicciones.append(prediccion)

    db.commit()
    for p in predicciones:
        db.refresh(p)
    return predicciones
