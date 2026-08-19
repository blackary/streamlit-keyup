from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, Literal

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

/* label visibility: "hidden" keeps the space, "collapsed" removes it */
.stkeyup--label-hidden .stkeyup__label { visibility: hidden; }
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

  // ── Sync value from Python ────────────────────────────────────────────────
  // data.value is the value Python wants shown. When it matches what we have,
  // Python has acknowledged our last send and the round-trip is done — clear
  // the typing guard. When it differs and we are NOT mid-send, Python is
  // seeding the input (e.g. the initial `value=`), so adopt it.
  const pyValue = data.value ?? "";
  if (pyValue === input.value) {
    input._userTyping = false;
  } else if (!input._userTyping) {
    input.value = pyValue;
    // Sync component state to the adopted value so it does not lag until the
    // user next types. Causes one extra rerun.
    setStateValue("value", pyValue);
  }

  // ── Store latest render values for use in the handlers ────────────────────
  parentElement._debounce = data.debounce ?? 0;
  parentElement._hasSubmit = !!data.has_submit;

  // ── Attach handlers once ──────────────────────────────────────────────────
  if (!parentElement._attached) {
    let debounceTimer = null;

    input.addEventListener("input", () => {
      input._userTyping = true;
      clearTimeout(debounceTimer);
      const delay = parentElement._debounce;
      if (delay > 0) {
        debounceTimer = setTimeout(() => {
          setStateValue("value", input.value);
        }, delay);
      } else {
        setStateValue("value", input.value);
      }
      // _userTyping is cleared in onRender once Python echoes the value back,
      // never on a timer — a timer can expire before the round-trip completes
      // and let an unrelated re-render stomp the user's input.
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        // Flush any pending debounce immediately on Enter
        clearTimeout(debounceTimer);
        setStateValue("value", input.value);
        // Only fire the trigger when Python registered on_submitted_change;
        // firing an unregistered trigger name is not a supported operation.
        if (parentElement._hasSubmit) {
          setTriggerValue("submitted", input.value);
        }
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
    isolate_styles=True,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def st_keyup(
    label: str,
    value: str = "",
    max_chars: int | None = None,
    key: str | None = None,
    type: Literal["default", "password"] = "default",
    debounce: int | None = None,
    on_change: Callable | None = None,
    args: tuple[Any, ...] | None = None,
    kwargs: dict[str, Any] | None = None,
    *,
    placeholder: str = "",
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
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
        Initial value, used on first render only. On later runs the live value
        comes from ``st.session_state[key]`` (a plain string).
    max_chars : int | None
        Maximum number of characters allowed.
    key : str | None
        Streamlit widget key. When set, ``st.session_state[key]`` contains
        the current value as a plain ``str`` — no nested dict needed::

            value = st_keyup("Label", key="my_key")
            # later:
            current = st.session_state.get("my_key", "")  # plain string

        To reset the field from Python, change the ``key`` (which creates a
        fresh widget); assigning to ``st.session_state[key]`` does not push a
        value into the input.
    type : str
        ``"default"`` or ``"password"``.
    debounce : int | None
        Milliseconds to wait after the last keystroke before updating Python.
    on_change : callable | None
        Callback fired on every value change (after debounce if set). Inside the
        callback ``st.session_state[key]`` already holds the new value, matching
        ``st.text_input`` semantics.
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
    # Use an internal component key so that the user's `key` stores a plain
    # string in session_state instead of the v2 {"value": "..."} dict. Callers
    # can then read st.session_state[key] as a raw string.
    internal_key = f"_st_keyup_{key}" if key is not None else None

    # current_value seeds data.value for this render. On a rerun we echo back the
    # component's last-reported value (what JS sent via setStateValue) so that
    # onRender sees pyValue === input.value and clears the _userTyping guard.
    # On first render there is no component state yet, so fall back to `value`.
    if internal_key is not None:
        state = st.session_state.get(internal_key, {})
        current_value = state.get("value", value) if isinstance(state, dict) else value
    else:
        current_value = value

    def _sync_user_key() -> None:
        # Streamlit runs callbacks before the script re-executes, so mirror the
        # component's latest value onto the user-facing key first — that way
        # reading st.session_state[key] inside a callback gives the NEW value,
        # matching st.text_input semantics.
        if key is None:
            return
        state = st.session_state.get(internal_key, {})
        if isinstance(state, dict) and "value" in state:
            st.session_state[key] = state["value"]

    def _run_callbacks(user_cb: Callable | None, cb_args, cb_kwargs) -> None:
        _sync_user_key()
        if user_cb is not None:
            user_cb(*(cb_args or ()), **(cb_kwargs or {}))

    _on_change: Callable = functools.partial(_run_callbacks, on_change, args, kwargs)

    _on_submit: Callable | None = None
    if on_submit is not None:
        _on_submit = functools.partial(
            _run_callbacks, on_submit, submit_args, submit_kwargs
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
            "has_submit": _on_submit is not None,
        },
        default={"value": current_value},
        key=internal_key,
        # _on_change always runs (it syncs session_state[key] before invoking the
        # user's callback, if any), which also satisfies v2's requirement that
        # on_{state}_change be set for the state name to be valid in `default`.
        on_value_change=_on_change,
        # on_submitted_change registers "submitted" as a trigger; only wire it
        # when a real callback is requested to avoid unnecessary re-runs.
        **({"on_submitted_change": _on_submit} if _on_submit is not None else {}),
    )

    live = result.value if result.value is not None else current_value

    # Mirror the value onto the user-facing key as a plain string.
    if key is not None:
        st.session_state[key] = live

    return live


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
