import pytest

from app.services import calculate_balance, get_student, get_summary, list_students, _balance_for


def test_find_existing_student():
    assert get_student("ST001")["name"] == "سارا احمدی"


def test_student_ids_are_case_insensitive():
    assert get_student(" st001 ")["student_id"] == "ST001"


def test_unknown_student():
    assert get_student("ST999") is None


def test_blank_student_id():
    assert get_student(" ") is None


def test_partial_payment_balance():
    result = calculate_balance("ST001")
    assert result["paid"] == 3_500_000
    assert result["balance"] == 4_500_000
    assert result["credit"] == 0


def test_fully_paid_student():
    assert calculate_balance("ST002")["balance"] == 0


def test_overpayment_is_credit():
    result = calculate_balance("ST003")
    assert result["balance"] == 0
    assert result["credit"] == 500_000


def test_pending_registration():
    assert get_student("ST004")["enrollment_status"] == "pending"


def test_unknown_balance():
    assert calculate_balance("ST999") is None


def test_student_index_excludes_payment_details():
    students = list_students()
    assert len(students) == 5
    assert "payments" not in students[0]


def test_summary_totals():
    result = get_summary()
    assert result == {
        "student_count": 5,
        "active_count": 4,
        "total_tuition": 26_000_000,
        "total_paid": 16_500_000,
        "total_outstanding": 10_000_000,
        "total_credit": 500_000,
    }


@pytest.mark.parametrize("invalid", [-1, 2.5, True])
def test_invalid_payment_amount_is_rejected(invalid):
    student = {"student_id": "ST999", "tuition": 10, "payments": [{"amount": invalid}]}
    with pytest.raises(ValueError, match="Payment amounts"):
        _balance_for(student)