from datetime import date,datetime
from decimal import Decimal
import pytest
from lms.errors import ValidationError
from lms.validation import email,phone,positive_int,decimal_number,valid_date,validate_record,like_pattern,text,status,MASTER_STATUSES

@pytest.mark.parametrize("value",["USER@example.com","first.last+course@example.co.uk","a_b@example.test"])
def test_valid_email(value):
    assert email(" "+value+" ")==value.lower()

@pytest.mark.parametrize("value",[None,"","invalid","a@b","a b@c.com",".a@example.com","a.@example.com","a..b@example.com","a@-example.com","a@example-.com","a@example..com","a"*65+"@example.com"])
def test_invalid_email(value):
    with pytest.raises(ValidationError): email(value)

@pytest.mark.parametrize("value",["","+92 300 1234567","0300-1234567","(555) 123-4567"])
def test_valid_phone(value): assert phone(value)==value

@pytest.mark.parametrize("value",["abcd","123","+1234567890123456","555++1234567","5551234567ext2"])
def test_invalid_phone(value):
    with pytest.raises(ValidationError): phone(value)

@pytest.mark.parametrize("value",[1,"4",Decimal("3.00"),99.0])
def test_valid_integer(value): assert positive_int(value,"ID")==int(value)

@pytest.mark.parametrize("value",[None,0,-1,True,1.1,"abc","nan","inf",4294967296])
def test_invalid_integer(value):
    with pytest.raises(ValidationError): positive_int(value,"ID")

@pytest.mark.parametrize("value",[0,100,"99.99",Decimal("0.01")])
def test_valid_marks(value): assert decimal_number(value,"Marks","100")==Decimal(str(value))

@pytest.mark.parametrize("value",[None,"",True,-0.01,100.01,"NaN","Infinity","-Infinity","1.234","text"])
def test_invalid_marks(value):
    with pytest.raises(ValidationError): decimal_number(value,"Marks","100")

@pytest.mark.parametrize("value",["2026-01-01",date(2026,1,1),datetime(2026,1,1,12,30)])
def test_date_conversion(value): assert valid_date(value,"Date",today=date(2026,9,16))==date(2026,1,1)

@pytest.mark.parametrize("value",[None,"2026-02-30","tomorrow","2027-01-01",date(1899,1,1)])
def test_date_validation(value):
    with pytest.raises(ValidationError): valid_date(value,"Date",today=date(2026,9,16))

@pytest.mark.parametrize("value",["active","Disabled",None,""])
def test_status_control(value):
    with pytest.raises(ValidationError): status(value,MASTER_STATUSES)


def test_grade_total_is_not_a_writable_field():
    with pytest.raises(ValidationError,match="unsupported field"):
        validate_record("grades",dict(enrollment_id=1,assignment_marks=10,quiz_marks=20,final_exam_marks=30,total_marks=999))


def test_unknown_entity():
    with pytest.raises(ValidationError): validate_record("students; DROP TABLE students",{})


def test_names_preserve_unicode_and_punctuation():
    assert text("  O'Connor  ","Name",120)=="O'Connor"
    assert text("علی","Name",120)=="علی"


def test_name_limits():
    with pytest.raises(ValidationError): text("x"*121,"Name",120)
    with pytest.raises(ValidationError): text("\x00Alice","Name",120)


def test_like_escape():
    assert like_pattern("50%_!")=="%50!%!_!!%"


def test_required_student_fields():
    with pytest.raises(ValidationError): validate_record("students",{})


def test_optional_student_phone():
    row=validate_record("students",dict(full_name="Test User",email="Test@Example.com",enrollment_date="2026-01-01",status="Active"),today=date(2026,9,16))
    assert row["phone"]==""
    assert row["email"]=="test@example.com"
