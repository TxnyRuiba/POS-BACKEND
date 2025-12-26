"""
Excepciones personalizadas para el sistema POS.
Centraliza el manejo de errores de negocio.
"""

from fastapi import HTTPException, status


class AppException(Exception):
    """Excepción base de la aplicación"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """Recurso no encontrado"""
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            f"{resource} con ID {identifier} no encontrado",
            status_code=404
        )


class DuplicateError(AppException):
    """Recurso duplicado"""
    def __init__(self, resource: str, field: str, value: str | int):
        super().__init__(
            f"{resource} con {field}='{value}' ya existe",
            status_code=409
        )


class InsufficientStockError(AppException):
    """Stock insuficiente"""
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            f"Stock insuficiente para {product_name}. "
            f"Disponible: {available}, Solicitado: {requested}",
            status_code=400
        )


class InvalidOperationError(AppException):
    """Operación no válida"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class UnauthorizedError(AppException):
    """No autorizado"""
    def __init__(self, message: str = "No autorizado para esta operación"):
        super().__init__(message, status_code=403)


class ValidationError(AppException):
    """Error de validación"""
    def __init__(self, field: str, message: str):
        super().__init__(
            f"Error en campo '{field}': {message}",
            status_code=422
        )


# Función helper para convertir a HTTPException
def to_http_exception(exc: AppException) -> HTTPException:
    """Convierte AppException a HTTPException de FastAPI"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )