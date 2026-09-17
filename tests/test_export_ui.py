from decimal import Decimal
from pathlib import Path
import pandas as pd
from lms.export import safe_csv,display_frame
from lms.ui import bars_html,kpis_html,status_html,table_html,heading_html
from lms.config import Settings,identifier
import pytest

@pytest.mark.parametrize("value",["=1+1","+SUM(A1)","-cmd","@evil","  =2+2","\t=1","\r=1"])
def test_csv_formula_protection(value):
    csv=safe_csv(pd.DataFrame({"Name":[value]})).decode("utf-8-sig")
    assert "'"+value in csv


def test_csv_preserves_numbers_and_unicode():
    text=safe_csv(pd.DataFrame({"Amount":[-12.5],"Name":["Renée"]})).decode("utf-8-sig")
    assert "-12.5" in text and "Renée" in text


def test_dataframe_preserves_missing_grades():
    frame=display_frame([{"total":None},{"total":Decimal("0")}])
    assert pd.isna(frame.iloc[0,0]) and frame.iloc[1,0]==0


def test_html_escapes_user_text():
    bad='<script>alert("x")</script>'
    for html in (heading_html(bad,bad),bars_html([{"n":bad,"v":2}],"n","v"),table_html([{"n":bad}],{"n":"Name"})):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


def test_zero_charts_do_not_divide_by_zero():
    assert "nan" not in bars_html([{"label":"Empty","count":0}],"label","count").lower()
    assert "0%" in status_html([])
    assert "0" in kpis_html({})


def test_empty_charts_show_no_records(): assert "No records" in bars_html([],"n","v")

@pytest.mark.parametrize("name",["bad-name","bad name","1bad","db;DROP TABLE students",""])
def test_sql_identifier_validation(name):
    with pytest.raises(ValueError): identifier(name)


def test_password_not_in_repr():
    assert "supersecret" not in repr(Settings(password="supersecret"))
