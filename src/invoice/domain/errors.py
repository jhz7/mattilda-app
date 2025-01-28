from src.shared.errors.business import BusinessError


def InvoiceInvalidStatusError(invoice_id: str) -> BusinessError:
    return BusinessError(
        code="InvoiceInvalidStatusError",
        message=f"Invalid status for invoice",
        attributes={"invoice_id": invoice_id},
    )


def PaymentInvalidStatusError(invoice_id: str, payment_id: str) -> BusinessError:
    return BusinessError(
        code="PaymentInvalidStatusError",
        message=f"Invalid status for payment",
        attributes={"invoice_id": invoice_id, "payment_id": payment_id},
    )


def PaymentNotFoundError(invoice_id: str, payment_id: str) -> BusinessError:
    return BusinessError(
        code="PaymentNotFoundError",
        message=f"Payment not found in invoice",
        attributes={"invoice_id": invoice_id, "payment_id": payment_id},
    )


def InvalidPaymentAmountError(invoice_id: str, payment_id: str) -> BusinessError:
    return BusinessError(
        code="InvalidPaymentAmountError",
        message=f"Payment amount surpasses invoice amount",
        attributes={"invoice_id": invoice_id, "payment_id": payment_id},
    )
