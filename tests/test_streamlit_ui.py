"""Real Streamlit AppTest smoke tests, enabled with the dedicated MySQL fixture."""
import pytest

pytestmark=pytest.mark.ui


def configure(monkeypatch,settings):
    for name,value in {"DB_HOST":settings.host,"DB_PORT":settings.port,"DB_NAME":settings.database,"DB_USER":settings.user,"DB_PASSWORD":settings.password,"APP_DATA_MODE":"sample"}.items():
        monkeypatch.setenv(name,str(value))

@pytest.mark.parametrize("module,function",[("dashboard","render"),("records","students"),("records","instructors"),("records","courses"),("records","enrollments"),("records","grades"),("reports_page","render"),("legal","terms"),("legal","privacy")])
def test_streamlit_page_renders(mysql_repo,mysql_settings,monkeypatch,module,function):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    configure(monkeypatch,mysql_settings)
    code=f"import streamlit as st\nfrom lms.views.{module} import {function}\nst.set_page_config(layout='wide')\n{function}()\n"
    app=AppTest.from_string(code).run(timeout=30)
    assert not app.exception


def test_streamlit_student_form_persists(mysql_repo,mysql_settings,monkeypatch):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest
    configure(monkeypatch,mysql_settings)
    app=AppTest.from_string("from lms.views.records import students\nstudents()\n").run(timeout=30)
    app.text_input(key="add_students_0_name").set_value("UI Test Student")
    app.text_input(key="add_students_0_email").set_value("uitest@example.test")
    next(button for button in app.button if button.label=="Add student").click().run(timeout=30)
    assert not app.exception
    assert len(mysql_repo.list_records("students","uitest@example.test"))==1
