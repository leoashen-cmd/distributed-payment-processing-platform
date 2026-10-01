from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

app = FastAPI(
    title="Distributed Payment Processing Platform",
    version="1.0.0"
)

payments = {}


class PaymentRequest(BaseModel):
    customer_id: str
    amount: float
    currency: str = "USD"
    description: str = ""


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "payment-processing-platform",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/payments")
def create_payment(payment: PaymentRequest):

    if payment.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than zero"
        )

    payment_id = str(uuid4())

    transaction = {
        "payment_id": payment_id,
        "customer_id": payment.customer_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

    payments[payment_id] = transaction

    return transaction


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):

    if payment_id not in payments:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payments[payment_id]


@app.get("/transactions")
def get_transactions():
    return {
        "count": len(payments),
        "transactions": list(payments.values())
    }


@app.post("/payments/{payment_id}/refund")
def refund_payment(payment_id: str):

    if payment_id not in payments:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    payment = payments[payment_id]

    if payment["status"] == "refunded":
        raise HTTPException(
            status_code=400,
            detail="Payment has already been refunded"
        )

    payment["status"] = "refunded"
    payment["refunded_at"] = datetime.utcnow().isoformat()

    return payment
