import streamlit as st
from ..config import ROOT
from ..runtime import settings
from ..ui import heading


def _render(filename,title,subtitle):
    heading(title,subtitle,"Workspace information")
    cfg=settings()
    body=(ROOT/"docs"/filename).read_text(encoding="utf-8")
    body=body.replace("{{INSTITUTE_NAME}}",cfg.institute).replace("{{PRIVACY_CONTACT}}",cfg.privacy_contact or "Contact your institute administrator through your existing institute communication channel.")
    st.markdown(body)


def terms():
    _render("TERMS.md","Terms & Conditions","How this academic records workspace should be used.")


def privacy():
    _render("PRIVACY.md","Privacy policy","What this application stores and how its default configuration handles data.")
