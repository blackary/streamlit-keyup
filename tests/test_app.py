"""
Thorough test app for st-keyup v2 — exercises the full API surface.
Each section is independently verifiable.
"""

import streamlit as st

from st_keyup import st_keyup

st.set_page_config(layout="wide", page_title="st_keyup v2 thorough test")

st.title("st_keyup v2 — full API surface")

# ── 1. Basic ───────────────────────────────────────────────────────────────
st.header("1. Basic")
v1 = st_keyup("Basic input", key="t_basic")
st.write("value:", repr(v1))

# ── 2. Default value ───────────────────────────────────────────────────────
st.header("2. Default value")
v2 = st_keyup("Has default", value="preset text", key="t_default")
st.write("value:", repr(v2))

# ── 3. Password type ───────────────────────────────────────────────────────
st.header("3. Password type")
v3 = st_keyup("Password", type="password", key="t_password")
st.write("value:", repr(v3))

# ── 4. max_chars ───────────────────────────────────────────────────────────
st.header("4. max_chars=5")
v4 = st_keyup("Max 5 chars", max_chars=5, key="t_maxchars")
st.write("value:", repr(v4), "len:", len(v4 or ""))

# ── 5. Placeholder ─────────────────────────────────────────────────────────
st.header("5. Placeholder")
v5 = st_keyup("Has placeholder", placeholder="type here...", key="t_placeholder")
st.write("value:", repr(v5))

# ── 6. Disabled ────────────────────────────────────────────────────────────
st.header("6. Disabled")
v6 = st_keyup("Disabled", value="cannot edit", disabled=True, key="t_disabled")
st.write("value:", repr(v6))

# ── 7. Label visibility ────────────────────────────────────────────────────
st.header("7. Label visibility")
c1, c2, c3 = st.columns(3)
with c1:
    st.caption("visible")
    st_keyup("Visible label", label_visibility="visible", key="t_vis")
with c2:
    st.caption("hidden")
    st_keyup("Hidden label", label_visibility="hidden", key="t_hidden")
with c3:
    st.caption("collapsed")
    st_keyup("Collapsed label", label_visibility="collapsed", key="t_collapsed")

# ── 8. Debounce ────────────────────────────────────────────────────────────
st.header("8. Debounce 500ms")
v8 = st_keyup("Debounced", debounce=500, key="t_debounce")
st.write("value:", repr(v8))

# ── 9. on_change callback ──────────────────────────────────────────────────
st.header("9. on_change callback")
st.session_state.setdefault("change_count", 0)


def bump():
    st.session_state.change_count += 1


v9 = st_keyup("Fires on_change", on_change=bump, key="t_onchange")
st.write("value:", repr(v9), "| change_count:", st.session_state.change_count)

# ── 10. on_change with args/kwargs ─────────────────────────────────────────
st.header("10. on_change with args/kwargs")
st.session_state.setdefault("cb_args", None)


def with_args(a, b, extra=None):
    st.session_state.cb_args = (a, b, extra)


v10 = st_keyup(
    "Callback with args",
    on_change=with_args,
    args=("first", "second"),
    kwargs={"extra": "kw"},
    key="t_args",
)
st.write("value:", repr(v10), "| cb_args:", st.session_state.cb_args)

# ── 11. on_submit (Enter key) ──────────────────────────────────────────────
st.header("11. on_submit (press Enter)")
st.session_state.setdefault("submit_count", 0)


def on_sub():
    st.session_state.submit_count += 1


v11 = st_keyup("Press Enter", on_submit=on_sub, key="t_submit")
st.write("value:", repr(v11), "| submit_count:", st.session_state.submit_count)

# ── 12. Programmatic clear via session_state ───────────────────────────────
st.header("12. Programmatic clear")
# The state must be modified BEFORE the component is instantiated this run.
if st.session_state.pop("_do_clear", False):
    st.session_state["t_clear"]["value"] = ""

v12 = st_keyup("Clear me from Python", key="t_clear")
st.write("value:", repr(v12))
if st.button("Clear the field above"):
    st.session_state["_do_clear"] = True
    st.rerun()

# ── 13. Session state shape ────────────────────────────────────────────────
st.header("13. Session state introspection")
st.write("st.session_state['t_basic'] =", st.session_state.get("t_basic"))
st.write("Type:", type(st.session_state.get("t_basic")).__name__)

# ── 14. No key (unkeyed) ───────────────────────────────────────────────────
st.header("14. Unkeyed component")
v14 = st_keyup("No key provided")
st.write("value:", repr(v14))

# ── 15. B1 regression: unrelated rerun must not stomp typed input ──────────
st.header("15. Unrelated rerun does not clear input")
st.write("Type below, then click the button. Text must survive.")
v15 = st_keyup("Survives unrelated rerun", key="t_stomp")
st.write("value:", repr(v15))
st.session_state.setdefault("unrelated", 0)
if st.button("Unrelated rerun", key="b_unrelated"):
    st.session_state.unrelated += 1
st.write("unrelated clicks:", st.session_state.unrelated)

# ── 16. B2 regression: Enter with no on_submit must not error ──────────────
st.header("16. Enter with no on_submit is safe")
v16 = st_keyup("Press Enter (no on_submit)", key="t_no_submit")
st.write("value:", repr(v16))
