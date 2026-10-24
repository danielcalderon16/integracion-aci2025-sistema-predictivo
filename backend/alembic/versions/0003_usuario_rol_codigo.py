"""agrega nombre_completo, codigo y rol a usuarios

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("nombre_completo", sa.String(length=150), nullable=False, server_default=""))
    op.add_column("usuarios", sa.Column("codigo", sa.String(length=30), nullable=True))
    op.add_column("usuarios", sa.Column("rol", sa.String(length=20), nullable=False, server_default="estudiante"))

    # Backfill con un placeholder único por fila existente, para no violar el
    # índice único de abajo con filas previas a esta migración.
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE usuarios SET codigo = 'PENDIENTE-' || id WHERE codigo IS NULL"))

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.alter_column("codigo", existing_type=sa.String(length=30), nullable=False)
    op.create_index("ix_usuarios_codigo", "usuarios", ["codigo"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_usuarios_codigo", table_name="usuarios")
    op.drop_column("usuarios", "rol")
    op.drop_column("usuarios", "codigo")
    op.drop_column("usuarios", "nombre_completo")
