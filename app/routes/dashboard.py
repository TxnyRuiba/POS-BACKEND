from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_
from database import get_db
from app.core.security import get_current_user, require_manager
from models import (
    Users, Product, SaleTicket, SaleTicketItem, 
    CashRegister, Cart
)
from datetime import datetime, timedelta
from typing import List, Dict
from decimal import Decimal

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reportes"])

# ==================== RESUMEN GENERAL ====================
@router.get("/summary", dependencies=[Depends(require_manager)])
def get_dashboard_summary(
    period: str = Query("today", regex="^(today|week|month|year)$"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Resumen ejecutivo del negocio.
    
    **Incluye:**
    - Total de ventas
    - Número de transacciones
    - Ticket promedio
    - Comparación con período anterior
    - Métodos de pago
    - Estado de inventario
    
    **Períodos:** today, week, month, year
    """
    
    # Calcular fechas
    now = datetime.now()
    start_date, end_date = _get_period_dates(period, now)
    prev_start, prev_end = _get_previous_period_dates(period, now)
    
    # VENTAS DEL PERÍODO ACTUAL
    current_sales = db.query(
        func.sum(SaleTicket.total).label('total'),
        func.count(SaleTicket.id).label('count'),
        func.avg(SaleTicket.total).label('avg_ticket')
    ).filter(
        SaleTicket.created_at.between(start_date, end_date),
        SaleTicket.status == 'completed'
    ).first()
    
    # VENTAS DEL PERÍODO ANTERIOR
    previous_sales = db.query(
        func.sum(SaleTicket.total).label('total'),
        func.count(SaleTicket.id).label('count')
    ).filter(
        SaleTicket.created_at.between(prev_start, prev_end),
        SaleTicket.status == 'completed'
    ).first()
    
    # DESGLOSE POR MÉTODO DE PAGO
    payment_methods = db.query(
        SaleTicket.payment_method,
        func.sum(SaleTicket.total).label('total'),
        func.count(SaleTicket.id).label('count')
    ).filter(
        SaleTicket.created_at.between(start_date, end_date),
        SaleTicket.status == 'completed'
    ).group_by(SaleTicket.payment_method).all()
    
    # INVENTARIO CRÍTICO
    low_stock = db.query(Product).filter(
        Product.Stock <= Product.Min_Stock,
        Product.Activo == 1
    ).count()
    
    total_products = db.query(Product).filter(Product.Activo == 1).count()
    
    # CALCULAR CAMBIOS PORCENTUALES
    current_total = float(current_sales.total or 0)
    previous_total = float(previous_sales.total or 0)
    
    sales_change = (
        ((current_total - previous_total) / previous_total * 100) 
        if previous_total > 0 else 0
    )
    
    tickets_change = (
        ((current_sales.count - previous_sales.count) / previous_sales.count * 100)
        if previous_sales.count > 0 else 0
    )
    
    return {
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "sales": {
            "total": round(current_total, 2),
            "change_percent": round(sales_change, 2),
            "previous_period": round(previous_total, 2)
        },
        "transactions": {
            "total": current_sales.count or 0,
            "change_percent": round(tickets_change, 2),
            "previous_period": previous_sales.count or 0
        },
        "average_ticket": round(float(current_sales.avg_ticket or 0), 2),
        "payment_methods": [
            {
                "method": pm.payment_method,
                "total": round(float(pm.total), 2),
                "count": pm.count,
                "percentage": round(float(pm.total) / current_total * 100, 2) if current_total > 0 else 0
            }
            for pm in payment_methods
        ],
        "inventory": {
            "total_products": total_products,
            "low_stock_items": low_stock,
            "stock_health": round((1 - low_stock / total_products) * 100, 2) if total_products > 0 else 100
        },
        "generated_at": now.isoformat()
    }


# ==================== VENTAS POR MES ====================
@router.get("/sales/by-month")
def get_sales_by_month(
    months: int = Query(12, ge=1, le=24, description="Número de meses"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Ventas totales agrupadas por mes.
    
    **Ideal para gráficos de línea/barras.**
    
    Retorna:
    - Total de ventas por mes
    - Número de tickets por mes
    - Ticket promedio
    """
    
    start_date = datetime.now() - timedelta(days=30 * months)
    
    monthly_sales = db.query(
        extract('year', SaleTicket.created_at).label('year'),
        extract('month', SaleTicket.created_at).label('month'),
        func.sum(SaleTicket.total).label('total'),
        func.count(SaleTicket.id).label('num_tickets'),
        func.avg(SaleTicket.total).label('avg_ticket')
    ).filter(
        SaleTicket.created_at >= start_date,
        SaleTicket.status == 'completed'
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return {
        "data": [
            {
                "period": f"{int(row.year)}-{int(row.month):02d}",
                "month_name": datetime(int(row.year), int(row.month), 1).strftime("%B %Y"),
                "total_sales": round(float(row.total), 2),
                "num_tickets": row.num_tickets,
                "avg_ticket": round(float(row.avg_ticket), 2)
            }
            for row in monthly_sales
        ],
        "months_analyzed": len(monthly_sales)
    }


# ==================== TOP PRODUCTOS ====================
@router.get("/products/top-selling")
def get_top_selling_products(
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Top N productos más vendidos.
    
    **Ideal para gráficos de barras horizontales o pie charts.**
    
    Retorna:
    - Productos ordenados por ingresos
    - Cantidad vendida
    - Porcentaje del total
    """
    
    start_date, end_date = _get_period_dates(period, datetime.now())
    
    top_products = (
        db.query(
            Product.Id,
            Product.Product,
            Product.Category,
            func.sum(SaleTicketItem.quantity).label('total_quantity'),
            func.sum(SaleTicketItem.subtotal).label('total_revenue'),
            func.count(func.distinct(SaleTicket.id)).label('num_orders')
        )
        .join(SaleTicketItem, Product.Id == SaleTicketItem.product_id)
        .join(SaleTicket, SaleTicketItem.ticket_id == SaleTicket.id)
        .filter(
            SaleTicket.created_at.between(start_date, end_date),
            SaleTicket.status == 'completed'
        )
        .group_by(Product.Id, Product.Product, Product.Category)
        .order_by(func.sum(SaleTicketItem.subtotal).desc())
        .limit(limit)
        .all()
    )
    
    # Calcular total para porcentajes
    total_revenue = sum(float(p.total_revenue) for p in top_products)
    
    return {
        "period": period,
        "total_revenue": round(total_revenue, 2),
        "products": [
            {
                "product_id": p.Id,
                "name": p.Product,
                "category": p.Category,
                "quantity_sold": int(p.total_quantity),
                "revenue": round(float(p.total_revenue), 2),
                "num_orders": p.num_orders,
                "percentage_of_total": round(
                    float(p.total_revenue) / total_revenue * 100, 2
                ) if total_revenue > 0 else 0
            }
            for p in top_products
        ]
    }


# ==================== VENTAS POR CATEGORÍA ====================
@router.get("/sales/by-category")
def get_sales_by_category(
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Ventas agrupadas por categoría de producto.
    
    **Ideal para pie charts o treemaps.**
    """
    
    start_date, end_date = _get_period_dates(period, datetime.now())
    
    category_sales = (
        db.query(
            Product.Category,
            func.sum(SaleTicketItem.subtotal).label('total'),
            func.sum(SaleTicketItem.quantity).label('quantity'),
            func.count(func.distinct(Product.Id)).label('num_products')
        )
        .join(SaleTicketItem, Product.Id == SaleTicketItem.product_id)
        .join(SaleTicket, SaleTicketItem.ticket_id == SaleTicket.id)
        .filter(
            SaleTicket.created_at.between(start_date, end_date),
            SaleTicket.status == 'completed'
        )
        .group_by(Product.Category)
        .order_by(func.sum(SaleTicketItem.subtotal).desc())
        .all()
    )
    
    total_revenue = sum(float(c.total) for c in category_sales)
    
    return {
        "period": period,
        "total_revenue": round(total_revenue, 2),
        "categories": [
            {
                "category": c.Category,
                "revenue": round(float(c.total), 2),
                "quantity_sold": int(c.quantity),
                "num_products": c.num_products,
                "percentage": round(
                    float(c.total) / total_revenue * 100, 2
                ) if total_revenue > 0 else 0
            }
            for c in category_sales
        ]
    }


# ==================== VENTAS POR HORA DEL DÍA ====================
@router.get("/sales/by-hour")
def get_sales_by_hour(
    date: str = Query(None, description="Fecha YYYY-MM-DD (default: hoy)"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Distribución de ventas por hora del día.
    
    **Útil para identificar horarios pico.**
    """
    
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        target_date = datetime.now().date()
    
    hourly_sales = (
        db.query(
            extract('hour', SaleTicket.created_at).label('hour'),
            func.sum(SaleTicket.total).label('total'),
            func.count(SaleTicket.id).label('count')
        )
        .filter(
            func.date(SaleTicket.created_at) == target_date,
            SaleTicket.status == 'completed'
        )
        .group_by('hour')
        .order_by('hour')
        .all()
    )
    
    # Rellenar horas sin ventas
    hours_dict = {int(h.hour): h for h in hourly_sales}
    
    return {
        "date": target_date.isoformat(),
        "hourly_distribution": [
            {
                "hour": f"{hour:02d}:00",
                "total_sales": round(float(hours_dict[hour].total), 2) if hour in hours_dict else 0,
                "num_tickets": hours_dict[hour].count if hour in hours_dict else 0
            }
            for hour in range(24)
        ]
    }


# ==================== RENDIMIENTO DE CAJEROS ====================
@router.get("/cashiers/performance", dependencies=[Depends(require_manager)])
def get_cashier_performance(
    period: str = Query("month", regex="^(week|month|quarter)$"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Rendimiento de cajeros (solo managers/admins).
    
    Métricas:
    - Total de ventas
    - Número de tickets
    - Ticket promedio
    - Tiempo promedio por transacción
    """
    
    start_date, end_date = _get_period_dates(period, datetime.now())
    
    cashier_stats = (
        db.query(
            Users.ID,
            Users.Username,
            Users.Role,
            func.sum(SaleTicket.total).label('total_sales'),
            func.count(SaleTicket.id).label('num_tickets'),
            func.avg(SaleTicket.total).label('avg_ticket')
        )
        .join(SaleTicket, Users.ID == SaleTicket.user_id)
        .filter(
            SaleTicket.created_at.between(start_date, end_date),
            SaleTicket.status == 'completed'
        )
        .group_by(Users.ID, Users.Username, Users.Role)
        .order_by(func.sum(SaleTicket.total).desc())
        .all()
    )
    
    return {
        "period": period,
        "cashiers": [
            {
                "user_id": c.ID,
                "username": c.Username,
                "role": c.Role,
                "total_sales": round(float(c.total_sales), 2),
                "num_tickets": c.num_tickets,
                "avg_ticket": round(float(c.avg_ticket), 2)
            }
            for c in cashier_stats
        ]
    }


# ==================== FUNCIONES AUXILIARES ====================
def _get_period_dates(period: str, reference_date: datetime):
    """Calcula fechas de inicio y fin según el período"""
    
    end = reference_date
    
    if period == "today":
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = end - timedelta(days=7)
    elif period == "month":
        start = end - timedelta(days=30)
    elif period == "quarter":
        start = end - timedelta(days=90)
    elif period == "year":
        start = end - timedelta(days=365)
    else:
        start = end - timedelta(days=30)
    
    return start, end

def _get_previous_period_dates(period: str, reference_date: datetime):
    """Calcula fechas del período anterior para comparación"""
    
    if period == "today":
        end = reference_date - timedelta(days=1)
        start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        end = reference_date - timedelta(days=7)
        start = end - timedelta(days=7)
    elif period == "month":
        end = reference_date - timedelta(days=30)
        start = end - timedelta(days=30)
    elif period == "year":
        end = reference_date - timedelta(days=365)
        start = end - timedelta(days=365)
    else:
        end = reference_date - timedelta(days=30)
        start = end - timedelta(days=30)
    
    return start, end