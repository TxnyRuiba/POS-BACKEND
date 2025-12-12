"""corregir precision decimal

Revision ID: 231449849d5e
Revises: 9e277a5c957f
Create Date: 2025-12-12 13:09:33.918564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '231449849d5e'
down_revision: Union[str, Sequence[str], None] = '9e277a5c957f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------ Punto 2: Agregar cancelled_at al Cart ------------------
    op.add_column('cart', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
    
    # ------------------ Puntos 3 y 4: Aumentar precisión decimal ------------------
    
    # Tabla 'Master_Data' (Product)
    # Cambio Stock: Integer -> NUMERIC(10, 4)
    op.alter_column('Master_Data', 'Stock',
               existing_type=sa.Integer(),
               type_=sa.NUMERIC(precision=10, scale=4),
               nullable=False,
               postgresql_using='Stock::numeric(10, 4)') # Uso de casting si la BD lo requiere
    
    # Cambio Min_Stock: Integer -> NUMERIC(10, 4)
    op.alter_column('Master_Data', 'Min_Stock',
               existing_type=sa.Integer(),
               type_=sa.NUMERIC(precision=10, scale=4),
               nullable=False,
               postgresql_using='Min_Stock::numeric(10, 4)')

    # Tabla 'cart_items'
    # Cambio Quantity: NUMERIC(10, 3) -> NUMERIC(10, 4)
    op.alter_column('cart_items', 'quantity',
               existing_type=sa.NUMERIC(precision=10, scale=3),
               type_=sa.NUMERIC(precision=10, scale=4),
               nullable=False)

    # Tabla 'sale_ticket_items'
    # Cambio Quantity: NUMERIC(10, 3) -> NUMERIC(10, 4)
    op.alter_column('sale_ticket_items', 'quantity',
               existing_type=sa.NUMERIC(precision=10, scale=3),
               type_=sa.NUMERIC(precision=10, scale=4),
               nullable=False)


def downgrade() -> None:
    # ------------------ Revertir Puntos 3 y 4: Bajar precisión decimal ------------------
    
    # Tabla 'sale_ticket_items'
    op.alter_column('sale_ticket_items', 'quantity',
               existing_type=sa.NUMERIC(precision=10, scale=4),
               type_=sa.NUMERIC(precision=10, scale=3),
               nullable=False)
               
    # Tabla 'cart_items'
    op.alter_column('cart_items', 'quantity',
               existing_type=sa.NUMERIC(precision=10, scale=4),
               type_=sa.NUMERIC(precision=10, scale=3),
               nullable=False)
               
    # Tabla 'Master_Data' (Product)
    # Revertir Min_Stock: NUMERIC(10, 4) -> Integer
    op.alter_column('Master_Data', 'Min_Stock',
               existing_type=sa.NUMERIC(precision=10, scale=4),
               type_=sa.Integer(),
               nullable=False,
               postgresql_using='Min_Stock::integer')

    # Revertir Stock: NUMERIC(10, 4) -> Integer
    op.alter_column('Master_Data', 'Stock',
               existing_type=sa.NUMERIC(precision=10, scale=4),
               type_=sa.Integer(),
               nullable=False,
               postgresql_using='Stock::integer')
    
    # ------------------ Revertir Punto 2: Quitar cancelled_at ------------------
    op.drop_column('cart', 'cancelled_at')