"""LangChain wrappers around deterministic business functions."""
from langchain.tools import tool
from app.services import get_student, calculate_balance


@tool
def find_student(student_id: str) -> dict:
    """Find a demo academy student by their exact ID, such as ST001.

    Use for questions about student name, course, enrollment status,
    tuition, or individual payment records. Never invent an ID.
    """
    student = get_student(student_id)
    if student is None:
        return {"found": False, "error": "student_not_found"}
    return {"found": True, "student": student}


@tool
def check_tuition_balance(student_id: str) -> dict:
    """Calculate a demo student's tuition total, payments, due balance, and extra credit.

    Use whenever the user asks how much has been paid or remains due.
    """
    result = calculate_balance(student_id)
    if result is None:
        return {"found": False, "error": "student_not_found"}
    return {"found": True, "financial_summary": result}