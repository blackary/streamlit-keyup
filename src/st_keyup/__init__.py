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
  // data.value reflects st.session_state[key]["value"]. When it matches what
  // we have, Python has acknowledged our last send and the round-trip is done —
  // clear the typing guard. When it differs and we are NOT mid-send, Python
  // changed the value externally (e.g. a programmatic reset), so adopt it.
  const pyValue = data.value ?? "";
  if (pyValue === input.value) {
    input._userTyping = false;
  } else if (!input._userTyping) {
    input.value = pyValue;
    // Fire setStateValue so the component state immediately reflects the
    // Python-driven change (e.g. a programmatic clear). Without this the
    // component state lags until the user next types. Causes one extra rerun.
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

        To update the field programmatically, assign the string *before* this
        component is rendered in the current script run::

            # At the top of the script (before st_keyup is called):
            if st.session_state.pop("_clear_it", False):
                st.session_state["my_key"] = ""

            value = st_keyup("Label", key="my_key")

            if st.button("Clear"):
                st.session_state["_clear_it"] = True
                st.rerun()
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
    # Use an internal component key so that the user's `key` stores a plain
    # string in session_state instead of the v2 {"value": "..."} dict.
    # This lets callers do:
    #   current = st.session_state.get(key, "")   # raw string
    #   st.session_state[key] = ""               # programmatic clear
    internal_key = f"_st_keyup_{key}" if key is not None else None

    # Determine current_value with three priorities:
    #  1. Programmatic override: caller wrote a new string to session_state[key]
    #     (detected by comparison with the sentinel = what WE last wrote).
    #  2. Normal rerun: use the component's internal state (what JS last reported
    #     via setStateValue).  This ensures data.value echoes back the user's
    #     typing so onRender can clear the _userTyping guard.
    #  3. First render: fall back to the `value` parameter.
    if key is not None:
        sentinel_key = f"_st_keyup_prev_{key}"
        ss_val = st.session_state.get(key)
        our_prev = st.session_state.get(sentinel_key)
        internal_state = st.session_state.get(internal_key, {})
        internal_value = (
            internal_state.get("value") if isinstance(internal_state, dict) else None
        )

        if isinstance(ss_val, str) and ss_val != our_prev:
            # Caller changed session_state[key] — programmatic override
            current_value = ss_val
            programmatic_override = True
        elif internal_value is not None:
            # Normal rerun — echo back the last JS-reported value so JS can
            # clear the _userTyping guard when the round-trip completes.
            current_value = internal_value
            programmatic_override = False
        else:
            current_value = value
            programmatic_override = False
    else:
        current_value = value
        programmatic_override = False

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
            "has_submit": _on_submit is not None,
        },
        default={"value": current_value},
        key=internal_key,
        # v2 requires on_{state}_change to be set (even as a no-op) for the
        # state name to be valid in `default`. Always pass at minimum a no-op.
        on_value_change=_on_change or (lambda: None),
        # on_submitted_change registers "submitted" as a trigger; only wire it
        # when a real callback is requested to avoid unnecessary re-runs.
        **({"on_submitted_change": _on_submit} if _on_submit is not None else {}),
    )

    live = (
        current_value  # trust programmatic override, not stale result.value
        if programmatic_override
        else (result.value if result.value is not None else current_value)
    )

    # Write the raw string back under the user-visible key and our sentinel.
    if key is not None:
        st.session_state[key] = live
        st.session_state[sentinel_key] = live

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
