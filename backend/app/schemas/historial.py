from app.schemas.aci import DisenoMezclaOut
from app.schemas.prediccion import PrediccionOut


class DisenoConPredicciones(DisenoMezclaOut):
    predicciones: list[PrediccionOut] = []
