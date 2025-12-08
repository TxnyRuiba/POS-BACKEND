from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from app.core.security import get_current_user, require_admin
from models import Users
from schemas import (
    CreateTicketRequest, 
    SaleTicketSchema, 
    SaleTicketItemSchema,
    CancelTicketRequest
)
import crud_tickets
import crud_cash_register
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["Tickets de Venta"])

# ==================== CREAR TICKET ====================
@router.post("/", response_model=SaleTicketSchema, status_code=201)
def create_ticket(
    data: CreateTicketRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Crea un ticket de venta a partir de un carrito.
    
    - Valida stock disponible
    - Reduce el inventario automáticamente
    - Calcula cambio para pagos en efectivo
    - Asocia el ticket a la caja registradora abierta del usuario
    """
    # Obtener caja abierta del usuario
    caja_abierta = crud_cash_register.obtener_caja_abierta(db, current_user.ID)
    cash_register_id = caja_abierta.id if caja_abierta else None
    
    # Crear ticket
    ticket = crud_tickets.crear_ticket(
        db, 
        data, 
        current_user.ID,
        cash_register_id
    )
    
    # Preparar respuesta
    items_schema = [
        SaleTicketItemSchema(
            product_code=item.product_code,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        for item in ticket.items
    ]
    
    return SaleTicketSchema(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        subtotal=ticket.subtotal,
        tax=ticket.tax,
        discount=ticket.discount,
        total=ticket.total,
        payment_method=ticket.payment_method,
        payment_reference=ticket.payment_reference,
        amount_paid=ticket.amount_paid,
        change_given=ticket.change_given,
        status=ticket.status,
        created_at=ticket.created_at,
        cashier_name=ticket.cashier.Username,
        items=items_schema
    )

# ==================== OBTENER TICKET ====================
@router.get("/{ticket_id}", response_model=SaleTicketSchema)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Obtiene un ticket por ID (para impresión/visualización)"""
    ticket = crud_tickets.obtener_ticket(db, ticket_id)
    
    items_schema = [
        SaleTicketItemSchema(
            product_code=item.product_code,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        for item in ticket.items
    ]
    
    return SaleTicketSchema(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        subtotal=ticket.subtotal,
        tax=ticket.tax,
        discount=ticket.discount,
        total=ticket.total,
        payment_method=ticket.payment_method,
        payment_reference=ticket.payment_reference,
        amount_paid=ticket.amount_paid,
        change_given=ticket.change_given,
        status=ticket.status,
        created_at=ticket.created_at,
        cashier_name=ticket.cashier.Username,
        items=items_schema
    )

# ==================== OBTENER POR NÚMERO ====================
@router.get("/number/{ticket_number}", response_model=SaleTicketSchema)
def get_ticket_by_number(
    ticket_number: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Obtiene un ticket por número (ej: TKT-20231207-0001)"""
    ticket = crud_tickets.obtener_ticket_por_numero(db, ticket_number)
    
    items_schema = [
        SaleTicketItemSchema(
            product_code=item.product_code,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            subtotal=item.subtotal
        )
        for item in ticket.items
    ]
    
    return SaleTicketSchema(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        subtotal=ticket.subtotal,
        tax=ticket.tax,
        discount=ticket.discount,
        total=ticket.total,
        payment_method=ticket.payment_method,
        payment_reference=ticket.payment_reference,
        amount_paid=ticket.amount_paid,
        change_given=ticket.change_given,
        status=ticket.status,
        created_at=ticket.created_at,
        cashier_name=ticket.cashier.Username,
        items=items_schema
    )

# ==================== CANCELAR TICKET ====================
@router.patch("/{ticket_id}/cancel", dependencies=[Depends(require_admin)])
def cancel_ticket(
    ticket_id: int,
    data: CancelTicketRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Cancela un ticket (solo admin).
    
    - Devuelve el stock al inventario
    - Actualiza la caja registradora
    - Mantiene registro histórico
    """
    ticket = crud_tickets.cancelar_ticket(db, ticket_id, data.reason, current_user.ID)
    
    return {
        "message": "Ticket cancelado exitosamente",
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "cancelled_by": current_user.Username,
        "cancelled_at": ticket.cancelled_at,
        "reason": ticket.cancellation_reason
    }

# ==================== LISTAR TICKETS ====================
@router.get("/")
def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str | None = Query(None, regex="^(completed|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Lista tickets con filtros opcionales.
    
    - **status**: completed, cancelled
    - **skip**: número de registros a saltar
    - **limit**: máximo de registros a retornar
    """
    tickets = crud_tickets.listar_tickets(
        db,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return [
        {
            "id": t.id,
            "ticket_number": t.ticket_number,
            "total": float(t.total),
            "payment_method": t.payment_method,
            "status": t.status,
            "created_at": t.created_at,
            "cashier": t.cashier.Username
        }
        for t in tickets
    ]

# ==================== TICKETS DEL DÍA ====================
@router.get("/reports/today")
def tickets_today(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Resumen de tickets del día actual"""
    tickets = crud_tickets.listar_tickets(
        db,
        fecha_desde=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    completed = [t for t in tickets if t.status == "completed"]
    cancelled = [t for t in tickets if t.status == "cancelled"]
    
    total_ventas = sum(float(t.total) for t in completed)
    
    return {
        "fecha": datetime.utcnow().date().isoformat(),
        "total_tickets": len(tickets),
        "completados": len(completed),
        "cancelados": len(cancelled),
        "total_ventas": total_ventas,
        "tickets": [
            {
                "id": t.id,
                "ticket_number": t.ticket_number,
                "total": float(t.total),
                "status": t.status,
                "created_at": t.created_at
            }
            for t in tickets
        ]
    }