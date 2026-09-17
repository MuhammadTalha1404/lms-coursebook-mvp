"""Validation shared by every form and every database write.

The brief does not define an assessment scale. This implementation explicitly
uses three equally sized, unweighted components, each 0-100, total 0-300.
"""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any
from .errors import ValidationError

MASTER_STATUSES = ("Active", "Inactive")
ENROLLMENT_STATUSES = ("Enrolled", "Completed", "Dropped")
FIELDS = {
    "students": ("full_name", "email", "phone", "enrollment_date", "status"),
    "instructors": ("full_name", "specialization", "email", "status"),
    "courses": ("course_name", "description", "instructor_id", "duration_hours", "fee", "status"),
    "enrollments": ("student_id", "course_id", "enrollment_date", "status"),
    "grades": ("enrollment_id", "assignment_marks", "quiz_marks", "final_exam_marks"),
}


def text(value: Any, label: str, maximum: int, *, minimum: int = 1) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValidationError(f"{label} must be text.")
    result = value.strip()
    if len(result) < minimum:
        raise ValidationError(f"{label} must contain at least {minimum} characters.")
    if len(result) > maximum:
        raise ValidationError(f"{label} must be {maximum} characters or fewer.")
    if any(ord(c) < 32 and c not in "\n\t" for c in result):
        raise ValidationError(f"{label} contains an unsupported control character.")
    return result


def email(value: Any) -> str:
    result = text(value, "Email", 254).lower()
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", result):
        raise ValidationError("Enter an email address such as name@example.com.")
    local, domain = result.rsplit("@", 1)
    if len(local) > 64 or local.startswith(".") or local.endswith(".") or ".." in result:
        raise ValidationError("Enter a valid email address without consecutive or misplaced dots.")
    if any(not label or len(label) > 63 or label.startswith("-") or label.endswith("-") for label in domain.split(".")):
        raise ValidationError("Enter a valid email domain.")
    return result


def phone(value: Any) -> str:
    result = text(value, "Phone", 32, minimum=0)
    if result and (not re.fullmatch(r"\+?[0-9 ()-]+", result) or not 7 <= len(re.sub(r"\D", "", result)) <= 15):
        raise ValidationError("Phone must contain 7-15 digits. Spaces, brackets and a leading + are allowed.")
    return result


def positive_int(value: Any, label: str, maximum: int = 4294967295) -> int:
    if isinstance(value, bool) or value is None:
        raise ValidationError(f"Select or enter a valid {label.lower()}.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{label} must be a whole number.") from None
    if not number.is_finite() or number != number.to_integral_value() or not 1 <= number <= maximum:
        raise ValidationError(f"{label} must be a whole number from 1 to {maximum:,}.")
    return int(number)


def decimal_number(value: Any, label: str, maximum: str) -> Decimal:
    if value is None or isinstance(value, bool) or str(value).strip() == "":
        raise ValidationError(f"Enter {label.lower()}; zero is a valid value.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"{label} must be a number.") from None
    if not result.is_finite() or not Decimal("0") <= result <= Decimal(maximum):
        raise ValidationError(f"{label} must be between 0 and {maximum}.")
    rounded = result.quantize(Decimal("0.01"))
    if rounded != result:
        raise ValidationError(f"{label} may have at most two decimal places.")
    return rounded


def valid_date(value: Any, label: str, *, today: date | None = None) -> date:
    if isinstance(value, datetime):
        value = value.date()
    elif isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError:
            raise ValidationError(f"{label} must be a valid date in YYYY-MM-DD format.") from None
    if not isinstance(value, date):
        raise ValidationError(f"Select a valid {label.lower()}.")
    if not date(1900, 1, 1) <= value <= (today or date.today()):
        raise ValidationError(f"{label} must be between 1 January 1900 and today.")
    return value


def status(value: Any, choices: tuple[str, ...]) -> str:
    if value not in choices:
        raise ValidationError("Status must be one of: " + ", ".join(choices) + ".")
    return value


def validate_record(entity: str, values: dict, *, today: date | None = None) -> dict:
    if entity not in FIELDS:
        raise ValidationError("Unknown record type.")
    if set(values) - set(FIELDS[entity]):
        raise ValidationError("The request contains an unsupported field.")
    v = values.get
    if entity == "students":
        return dict(full_name=text(v("full_name"), "Full name", 120, minimum=2),
                    email=email(v("email")), phone=phone(v("phone", "")),
                    enrollment_date=valid_date(v("enrollment_date"), "Enrollment date", today=today),
                    status=status(v("status"), MASTER_STATUSES))
    if entity == "instructors":
        return dict(full_name=text(v("full_name"), "Full name", 120, minimum=2),
                    specialization=text(v("specialization"), "Specialization", 120, minimum=2),
                    email=email(v("email")), status=status(v("status"), MASTER_STATUSES))
    if entity == "courses":
        return dict(course_name=text(v("course_name"), "Course name", 150, minimum=2),
                    description=text(v("description", ""), "Description", 5000, minimum=0),
                    instructor_id=positive_int(v("instructor_id"), "Instructor"),
                    duration_hours=positive_int(v("duration_hours"), "Duration in hours", 10000),
                    fee=decimal_number(v("fee"), "Fee", "99999999.99"),
                    status=status(v("status"), MASTER_STATUSES))
    if entity == "enrollments":
        return dict(student_id=positive_int(v("student_id"), "Student"),
                    course_id=positive_int(v("course_id"), "Course"),
                    enrollment_date=valid_date(v("enrollment_date"), "Enrollment date", today=today),
                    status=status(v("status"), ENROLLMENT_STATUSES))
    return dict(enrollment_id=positive_int(v("enrollment_id"), "Enrollment"),
                assignment_marks=decimal_number(v("assignment_marks"), "Assignment marks", "100"),
                quiz_marks=decimal_number(v("quiz_marks"), "Quiz marks", "100"),
                final_exam_marks=decimal_number(v("final_exam_marks"), "Final-exam marks", "100"))


def like_pattern(value: str) -> str:
    """Escape literal LIKE metacharacters; the query declares ESCAPE '!'."""
    query = text(value, "Search", 160, minimum=0)
    return "%" + query.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
