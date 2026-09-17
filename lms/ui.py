"""Reusable, escaped HTML for the visual layer. No remote images or fonts."""
from datetime import datetime
from html import escape
import math
from .config import ROOT


def icon(name: str, size: int = 20) -> str:
    paths = {
        "students": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "instructors": '<circle cx="12" cy="7" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2M9 17l3 3 3-3"/>',
        "courses": '<path d="M12 6c-3-2-6-2-10-1v15c4-1 7-1 10 1 3-2 6-2 10-1V5c-4-1-7-1-10 1Zm0 0v15"/>',
        "enrollments": '<rect x="4" y="4" width="16" height="18" rx="2"/><path d="M8 2v4m8-4v4M4 10h16m-12 6 3 3 5-5"/>',
        "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    }
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths.get(name, paths["courses"])}</svg>'


def brand_html() -> str:
    mark = (ROOT / "assets/logo.svg").read_text()
    return f'<div class="cb-brand">{mark}<div><strong>Coursebook</strong><span>ACADEMIC WORKSPACE</span></div></div>'


def heading_html(title: str, description: str, section: str = "Workspace") -> str:
    return f'<div class="cb-page-heading"><div class="cb-eyebrow">{escape(section)} / {escape(title)}</div><h1>{escape(title)}</h1><p>{escape(description)}</p></div>'


def kpis_html(summary: dict) -> str:
    specs = (
        ("students", "Students", "active_students", "active students"),
        ("instructors", "Instructors", "active_instructors", "active instructors"),
        ("courses", "Courses", "active_courses", "active courses"),
        ("enrollments", "Enrollments", "current_enrollments", "currently enrolled"),
    )
    parts = []
    for field, label, detail, suffix in specs:
        count, subcount = int(summary.get(field, 0)), int(summary.get(detail, 0))
        parts.append(f'<section class="cb-kpi"><div class="cb-kpi-top"><span>{label}</span>{icon(field)}</div><strong class="cb-kpi-number">{count:,}</strong><div class="cb-kpi-detail">{subcount:,} {suffix}</div></section>')
    return '<div class="cb-kpis">' + ''.join(parts) + '</div>'


def bars_html(rows: list[dict], label: str, value: str, *, limit: int | None = None) -> str:
    rows = rows[:limit] if limit else rows
    if not rows:
        return '<p class="cb-empty">No records to chart yet.</p>'
    maximum = max(float(row.get(value) or 0) for row in rows) or 1
    result = []
    for row in rows:
        name, count = str(row.get(label, "")), float(row.get(value) or 0)
        width = min(100, max(0, count / maximum * 100)) if math.isfinite(count) else 0
        number = f"{count:,.0f}" if count.is_integer() else f"{count:,.2f}"
        result.append(f'<div class="cb-chart-row"><div class="cb-chart-label"><span>{escape(name)}</span><strong>{number}</strong></div><div class="cb-bar-track" role="img" aria-label="{escape(name)}: {number}"><span style="width:{width:.3f}%"></span></div></div>')
    return '<div class="cb-bars">' + ''.join(result) + '</div>'


def status_html(rows: list[dict]) -> str:
    counts = {str(row["status"]): int(row["enrollment_count"]) for row in rows}
    total = sum(counts.values())
    segments, legend = [], []
    for status, style in (("Enrolled", "current"), ("Completed", "complete"), ("Dropped", "dropped")):
        count = counts.get(status, 0)
        percentage = count / total * 100 if total else 0
        segments.append(f'<span class="cb-segment {style}" style="width:{percentage:.4f}%" title="{status}: {count}"></span>')
        legend.append(f'<div class="cb-status-row"><span><i class="cb-dot {style}"></i>{status}</span><strong>{count:,}</strong><small>{percentage:.0f}%</small></div>')
    return f'<div class="cb-status-total"><strong>{total:,}</strong><span>total enrollments</span></div><div class="cb-stack" role="img" aria-label="Enrollment status distribution">{"".join(segments)}</div><div class="cb-status-legend">{"".join(legend)}</div>'


def table_html(rows: list[dict], columns: dict[str, str]) -> str:
    def cell(field, value):
        if value is None:
            return '<span class="cb-muted">Not recorded</span>'
        if field == "status" and value in {"Active", "Inactive", "Enrolled", "Completed", "Dropped"}:
            return f'<span class="cb-status-tag {str(value).lower()}">{escape(str(value))}</span>'
        return escape(str(value))
    headers = ''.join(f'<th scope="col">{escape(name)}</th>' for name in columns.values())
    body = ''.join('<tr>' + ''.join(f'<td>{cell(field,row.get(field))}</td>' for field in columns) + '</tr>' for row in rows)
    if not rows:
        body = f'<tr><td colspan="{len(columns)}" class="cb-empty">No records yet.</td></tr>'
    return f'<div class="cb-table-wrap"><table class="cb-table"><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table></div>'


def heading(title: str, description: str, section: str = "Workspace") -> None:
    import streamlit as st
    st.html(heading_html(title, description, section))


def flash() -> None:
    import streamlit as st
    message = st.session_state.pop("_flash", None)
    if message:
        st.success(message)


def saved(message: str, entity: str) -> None:
    import streamlit as st
    st.session_state["_flash"] = message
    for key in list(st.session_state):
        if key.startswith(f"_snapshot_{entity}_"):
            del st.session_state[key]
    st.session_state[f"_form_generation_{entity}"] = st.session_state.get(f"_form_generation_{entity}", 0) + 1
    st.rerun()


def updated_caption() -> None:
    import streamlit as st
    st.caption("Read from MySQL at " + datetime.now().astimezone().strftime("%H:%M:%S %Z") + ". Refresh to retrieve the latest records.")
