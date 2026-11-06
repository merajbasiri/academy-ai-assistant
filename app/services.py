"""Student and tuition lookups for the read-only sample dataset."""

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "students.json"


def load_students() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8") as source:
        records = json.load(source)
    if not isinstance(records, list):
        raise ValueError("The student dataset must be a JSON array")
    return records


def list_students() -> list[dict[str, str]]:
    """Return the fields needed to populate the demo's student picker."""
    return [
        {
            "student_id": student["student_id"],
            "name": student["name"],
            "course": student["course"],
            "enrollment_status": student["enrollment_status"],
        }
        for student in load_students()
    ]


def get_student(student_id: str) -> dict[str, Any] | None:
    if not student_id or not student_id.strip():
        return None
    target = student_id.strip().upper()
    return next(
        (item for item in load_students() if item["student_id"] == target),
        None,
    )


def _balance_for(student: dict[str, Any]) -> dict[str, Any]:
    tuition = student["tuition"]
    amounts = [payment["amount"] for payment in student["payments"]]

    if type(tuition) is not int or tuition < 0:
        raise ValueError("Tuition must be a non-negative integer")
    if any(type(amount) is not int or amount < 0 for amount in amounts):
        raise ValueError("Payment amounts must be non-negative integers")

    paid = sum(amounts)
    return {
        "student_id": student["student_id"],
        "tuition": tuition,
        "paid": paid,
        "balance": max(tuition - paid, 0),
        "credit": max(paid - tuition, 0),
        "currency": "TOMAN",
    }


def calculate_balance(student_id: str) -> dict[str, Any] | None:
    student = get_student(student_id)
    return _balance_for(student) if student is not None else None


def get_summary() -> dict[str, int]:
    records = load_students()
    balances = [_balance_for(student) for student in records]
    return {
        "student_count": len(records),
        "active_count": sum(
            student["enrollment_status"] == "active" for student in records
        ),
        "total_tuition": sum(item["tuition"] for item in balances),
        "total_paid": sum(item["paid"] for item in balances),
        "total_outstanding": sum(item["balance"] for item in balances),
        "total_credit": sum(item["credit"] for item in balances),
    }