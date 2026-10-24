"""esquema inicial: usuarios, disenos_mezcla, predicciones

Revision ID: 0001
Revises:
Create Date: 2026-09-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_usuarios_username", "usuarios", ["username"], unique=True)
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "disenos_mezcla",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("folio", sa.String(length=64), nullable=False),
        sa.Column("tipo_construccion", sa.String(length=100)),
        sa.Column("condiciones_agresivas", sa.String(length=50)),
        sa.Column("resistencia_teorica_kgcm2", sa.Float(), nullable=False),
        sa.Column("resistencia_teorica_mpa", sa.Float(), nullable=False),
        sa.Column("resistencia_teorica_psi", sa.Float(), nullable=False),
        sa.Column("densidad_cemento", sa.Float()),
        sa.Column("tipo_cemento", sa.String(length=20)),
        sa.Column("tamano_nominal_in", sa.Float()),
        sa.Column("tamano_nominal_mm", sa.Float()),
        sa.Column("masa_unitaria_grueso", sa.Float()),
        sa.Column("densidad_aparente_grueso", sa.Float()),
        sa.Column("absorcion_grueso", sa.Float()),
        sa.Column("humedad_grueso", sa.Float()),
        sa.Column("modulo_finura", sa.Float()),
        sa.Column("masa_unitaria_fino", sa.Float()),
        sa.Column("densidad_aparente_fino", sa.Float()),
        sa.Column("absorcion_fino", sa.Float()),
        sa.Column("humedad_fino", sa.Float()),
        sa.Column("asentamiento_in", sa.Float()),
        sa.Column("contenido_aire", sa.Float()),
        sa.Column("altura_cilindro", sa.Float()),
        sa.Column("diametro_cilindro", sa.Float()),
        sa.Column("num_cilindros", sa.Integer()),
        sa.Column("porcentaje_lodo", sa.Float()),
        sa.Column("volumen_unitario_agua", sa.Float()),
        sa.Column("relacion_agua_cemento", sa.Float()),
        sa.Column("contenido_agregado_grueso", sa.Float()),
        sa.Column("factor_cemento", sa.Float()),
        sa.Column("peso_agregado_grueso", sa.Float()),
        sa.Column("peso_agregado_fino", sa.Float()),
        sa.Column("peso_real_grueso", sa.Float()),
        sa.Column("peso_real_fino", sa.Float()),
        sa.Column("agua_mezclado", sa.Float()),
        sa.Column("cemento_cant", sa.Float()),
        sa.Column("lodo_cant", sa.Float()),
        sa.Column("arena_cant", sa.Float()),
        sa.Column("grava_cant", sa.Float()),
        sa.Column("agua_cant", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_disenos_mezcla_folio", "disenos_mezcla", ["folio"], unique=True)

    op.create_table(
        "predicciones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("diseno_id", sa.Integer(), sa.ForeignKey("disenos_mezcla.id", ondelete="CASCADE"), nullable=False),
        sa.Column("escoria", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cenizas", sa.Float(), nullable=False, server_default="0"),
        sa.Column("superplastificante", sa.Float(), nullable=False, server_default="0"),
        sa.Column("edad_dias", sa.Integer(), nullable=False),
        sa.Column("resistencia_predicha_mpa", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("predicciones")
    op.drop_index("ix_disenos_mezcla_folio", table_name="disenos_mezcla")
    op.drop_table("disenos_mezcla")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_username", table_name="usuarios")
    op.drop_table("usuarios")
