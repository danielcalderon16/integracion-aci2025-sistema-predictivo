from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.deps import get_current_user
from app.models.diseno import DisenoMezcla
from app.models.usuario import Usuario
from app.schemas.historial import DisenoConPredicciones
from app.services.reportes import exportar_excel, exportar_pdf

router = APIRouter(prefix="/historial", tags=["historial"])


def _puede_ver_todo(usuario: Usuario) -> bool:
    """Profesores y administradores pueden revisar el trabajo de cualquier estudiante."""
    return usuario.is_admin or usuario.rol == "profesor"


def _obtener_diseno(diseno_id: int, usuario: Usuario, db: Session, solo_propio: bool = False) -> DisenoMezcla:
    query = (
        db.query(DisenoMezcla)
        .options(joinedload(DisenoMezcla.predicciones), joinedload(DisenoMezcla.usuario))
        .filter(DisenoMezcla.id == diseno_id)
    )
    if solo_propio or not _puede_ver_todo(usuario):
        query = query.filter(DisenoMezcla.usuario_id == usuario.id)
    diseno = query.first()
    if diseno is None:
        raise HTTPException(status_code=404, detail="Diseño de mezcla no encontrado")
    return diseno


@router.get("", response_model=list[DisenoConPredicciones])
def listar_historial(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    query = (
        db.query(DisenoMezcla)
        .options(joinedload(DisenoMezcla.predicciones), joinedload(DisenoMezcla.usuario))
    )
    if not _puede_ver_todo(usuario):
        query = query.filter(DisenoMezcla.usuario_id == usuario.id)
    return query.order_by(DisenoMezcla.created_at.desc()).all()


@router.get("/{diseno_id}", response_model=DisenoConPredicciones)
def obtener_diseno(diseno_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return _obtener_diseno(diseno_id, usuario, db)


@router.delete("/{diseno_id}", status_code=204)
def eliminar_diseno(diseno_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    # Borrar queda restringido al dueño del diseño o a un administrador, aunque
    # un profesor pueda verlo: evita que una revisión termine borrando sin querer
    # el trabajo de un estudiante.
    query = db.query(DisenoMezcla).filter(DisenoMezcla.id == diseno_id)
    if not usuario.is_admin:
        query = query.filter(DisenoMezcla.usuario_id == usuario.id)
    diseno = query.first()
    if diseno is None:
        raise HTTPException(status_code=404, detail="Diseño de mezcla no encontrado")
    db.delete(diseno)
    db.commit()


@router.get("/{diseno_id}/export/excel")
def exportar_excel_endpoint(diseno_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    diseno = _obtener_diseno(diseno_id, usuario, db)
    buffer = exportar_excel(diseno)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={diseno.folio}.xlsx"},
    )


@router.get("/{diseno_id}/export/pdf")
def exportar_pdf_endpoint(diseno_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    diseno = _obtener_diseno(diseno_id, usuario, db)
    buffer = exportar_pdf(diseno)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={diseno.folio}.pdf"},
    )
