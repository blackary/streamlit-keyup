from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

import streamlit as st

# ---------------------------------------------------------------------------
# HTML skeleton
# ---------------------------------------------------------------------------

_HTML = """
<div class="stkeyup" id="root">
  <label id="label" class="stkeyup__label"></label>
  <div class="stkeyup__wrap" id="wrap">
    <input id="input" class="stkeyup__input" />
  </div>
</div>
"""

# ---------------------------------------------------------------------------
# CSS  (--st-* vars are injected automatically by Streamlit v2)
# ---------------------------------------------------------------------------

_CSS = """
*,
*::before,
*::after { box-sizing: border-box; margin: 0; padding: 0; }

.stkeyup {
  display: flex;
  flex-direction: column;
  font-family: var(--st-font, sans-serif);
  color: var(--st-text-color, inherit);
  width: 100%;
}

.stkeyup__label {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--st-text-color, inherit);
  margin-bottom: 4px;
  min-height: 1.4em;
}

.stkeyup__wrap {
  display: flex;
  align-items: center;
  border: 1px solid rgba(127, 127, 127, 0.3);
  border-radius: 6px;
  background-color: var(--st-secondary-background-color, #f0f2f6);
  transition: border-color 150ms ease;
}

.stkeyup__wrap:focus-within {
  border-color: var(--st-primary-color, #ff4b4b);
}

.stkeyup__input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  padding: 10px 14px;
  font-family: var(--st-font, sans-serif);
  font-size: 15px;
  font-weight: 400;
  color: var(--st-text-color, inherit);
  caret-color: var(--st-text-color, inherit);
  min-width: 0;
}

/* label visibility */
.stkeyup--label-hidden   .stkeyup__label,
.stkeyup--label-collapsed .stkeyup__label { display: none; }

/* disabled */
.stkeyup--disabled .stkeyup__input {
  cursor: not-allowed;
  opacity: 0.5;
}
"""

# ---------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------

_JS = r"""
export default function({ parentElement, data, setStateValue, setTriggerValue }) {
  const root  = parentElement.querySelector("#root");
  const lbl   = parentElement.querySelector("#label");
  const wrap  = parentElement.querySelector("#wrap");
  const input = parentElement.querySelector("#input");

  // ── Update label ─────────────────────────────────────────────────────────
  lbl.textContent = data.label ?? "";

  // ── Update visibility classes ─────────────────────────────────────────────
  root.classList.remove(
    "stkeyup--label-hidden",
    "stkeyup--label-collapsed",
    "stkeyup--disabled"
  );
  const vis = data.label_visibility ?? "visible";
  if (vis === "hidden")    root.classList.add("stkeyup--label-hidden");
  if (vis === "collapsed") root.classList.add("stkeyup--label-collapsed");
  if (data.disabled)       root.classList.add("stkeyup--disabled");

  // ── Update input attributes ───────────────────────────────────────────────
  input.disabled    = !!data.disabled;
  input.placeholder = data.placeholder ?? "";
  input.maxLength   = data.max_chars > 0 ? data.max_chars : 524288;

  // Only change type when needed (changing type clears value in some browsers)
  const desiredType = data.type === "password" ? "password" : "text";
  if (input.type !== desiredType) {
    const saved = input.value;
    input.type  = desiredType;
    input.value = saved;
  }

  // ── Sync value from Python (programmatic updates, e.g. clearing) ──────────
  // data.value reflects st.session_state[key]["value"], so it IS the current
  // user-typed value on normal re-runs. Only update if Python changed it.
  if ((data.value ?? "") !== input.value && !input._userTyping) {
    input.value = data.value ?? "";
  }

  // ── Store latest debounce delay for use in the handler ────────────────────
  parentElement._debounce = data.debounce ?? 0;

  // ── Attach handlers once ──────────────────────────────────────────────────
  if (!parentElement._attached) {
    let debounceTimer = null;

    input.addEventListener("input", () => {
      input._userTyping = true;
      clearTimeout(debounceTimer);
      const delay = parentElement._debounce;
      if (delay > 0) {
        debounceTimer = setTimeout(() => {
          input._userTyping = false;
          setStateValue("value", input.value);
        }, delay);
      } else {
        setStateValue("value", input.value);
        // Allow a tick for the value to flush, then clear the flag
        setTimeout(() => { input._userTyping = false; }, 0);
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        // Flush any pending debounce immediately on Enter
        clearTimeout(debounceTimer);
        input._userTyping = false;
        setStateValue("value", input.value);
        setTriggerValue("submitted", input.value);
      }
    });

    parentElement._attached = true;
  }
}
"""

# ---------------------------------------------------------------------------
# Component registration
# ---------------------------------------------------------------------------

_keyup_component = st.components.v2.component(
    "st_keyup",
    html=_HTML,
    css=_CSS,
    js=_JS,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def st_keyup(
    label: str,
    value: str = "",
    max_chars: int | None = None,
    key: str | None = None,
    type: str = "default",
    debounce: int | None = None,
    on_change: Callable | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    *,
    placeholder: str = "",
    disabled: bool = False,
    label_visibility: str = "visible",
    on_submit: Callable | None = None,
    submit_args: tuple[Any, ...] | None = None,
    submit_kwargs: dict[str, Any] | None = None,
) -> str:
    """
    A text input that returns the current value on every keystroke (or after a
    debounce delay), without requiring the user to press Enter.

    Parameters
    ----------
    label : str
        Label shown above the input.
    value : str
        Default/initial value. Ignored after first render; use
        st.session_state[key]["value"] to read or set the live value.
    max_chars : int | None
        Maximum number of characters allowed.
    key : str | None
        Streamlit widget key. Required for accessing the component's state via
        st.session_state.
    type : str
        ``"default"`` or ``"password"``.
    debounce : int | None
        Milliseconds to wait after the last keystroke before updating Python.
    on_change : callable | None
        Callback fired on every value change (after debounce if set).
    args : tuple | None
        Positional args forwarded to *on_change*.
    kwargs : dict | None
        Keyword args forwarded to *on_change*.
    placeholder : str
        Placeholder text shown when the input is empty.
    disabled : bool
        When True, the input is rendered as disabled.
    label_visibility : str
        One of ``"visible"`` (default), ``"hidden"``, or ``"collapsed"``.
    on_submit : callable | None
        Callback fired when the user presses Enter.
    submit_args : tuple | None
        Positional args forwarded to *on_submit*.
    submit_kwargs : dict | None
        Keyword args forwarded to *on_submit*.

    Returns
    -------
    str
        The current value of the input.
    """
    # Read the current live value from session state so programmatic updates
    # (e.g. clearing the field via st.session_state) are reflected back to JS.
    if key is not None:
        component_state = st.session_state.get(key, {})
        if isinstance(component_state, dict):
            current_value = component_state.get("value", value)
        else:
            current_value = value
    else:
        current_value = value

    # Build callbacks
    _on_change: Callable | None = None
    if on_change is not None:
        _on_change = functools.partial(on_change, *(args or ()), **(kwargs or {}))

    _on_submit: Callable | None = None
    if on_submit is not None:
        _on_submit = functools.partial(
            on_submit, *(submit_args or ()), **(submit_kwargs or {})
        )

    result = _keyup_component(
        data={
            "label": label,
            "value": current_value,
            "type": type,
            "debounce": debounce or 0,
            "max_chars": max_chars or 0,
            "placeholder": placeholder,
            "disabled": disabled,
            "label_visibility": label_visibility,
        },
        default={"value": current_value},
        key=key,
        # v2 requires on_{state}_change to be set (even as a no-op) for the
        # state name to be valid in `default`. Always pass at minimum a no-op.
        on_value_change=_on_change or (lambda: None),
        # on_submitted_change registers "submitted" as a trigger; only wire it
        # when a real callback is requested to avoid unnecessary re-runs.
        **({"on_submitted_change": _on_submit} if _on_submit is not None else {}),
    )

    return result.value if result.value is not None else current_value


def main() -> None:
    from datetime import datetime

    st.write("## Default keyup input")
    value = st_keyup("Enter a value")
    st.write(value)

    "## Keyup with hidden label"
    value = st_keyup("You can't see this", label_visibility="hidden")

    "## Keyup with collapsed label"
    value = st_keyup("This either", label_visibility="collapsed")

    "## Keyup with max_chars 5"
    value = st_keyup("Keyup with max chars", max_chars=5)

    "## Keyup with password type"
    value = st_keyup("Password", value="Hello World", type="password")

    "## Keyup with disabled"
    value = st_keyup("Disabled", value="Hello World", disabled=True)

    "## Keyup with default value"
    value = st_keyup("Default value", value="Hello World")

    "## Keyup with placeholder"
    value = st_keyup("Has placeholder", placeholder="A placeholder")

    "## Keyup with 500ms debounce"
    value = st_keyup("Debounced", debounce=500)
    st.write(value)

    def on_change_cb():
        st.write("Value changed!", datetime.now())

    "## Keyup with on_change callback"
    value = st_keyup("Has on_change", on_change=on_change_cb)

    "## Keyup with on_submit"
    value = st_keyup(
        "Press Enter to submit",
        on_submit=on_change_cb,
    )

    "## Standard text input for comparison"
    value = st.text_input("Enter a value")
    st.write(value)

    st.write(st.session_state)


if __name__ == "__main__":
    main()
