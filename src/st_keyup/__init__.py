from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

build_dir = Path(__file__).parent.absolute() / "frontend"
_component_func = components.declare_component("st_keyup", path=str(build_dir))


def st_keyup(
    label: str,
    value: str = "",
    max_chars: Optional[int] = None,
    key: Optional[str] = None,
    type: str = "text",
    debounce: Optional[int] = None,
    on_change: Optional[Callable] = None,
    args: Optional[Tuple[Any, ...]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    *,
    placeholder: str = "",
    disabled: bool = False,
    label_visibility: str = "visible",
)-> str:
        
    r"""Generate a text input that renders on keyup, debouncing the input by the
    specified amount of milliseconds.
    Debounce means that it will wait at least the specified amount of milliseconds
    before updating the value. This is useful for preventing excessive updates
    when the user is typing. Since the input updating will cause the app to rerun,
    if you are having performance issues, you should consider setting a debounce
    value.

    Parameters
    ----------
    label : str
        A short label explaining to the user what this input is for.
    value : object
        The text value of this widget when it first renders. This will be
        cast to str internally.
    max_chars : int or None
        Max number of characters allowed in text input.
    key : str or int
        An optional string or integer to use as the unique key for the widget.
        If this is omitted, a key will be generated for the widget
        based on its content. Multiple widgets of the same type may
        not share the same key.
    type : str
        The type of the text input. This can be any of these following types in the list below.
        If no value is passed, it defaults to "text".
        ["password", ("tel" or "phone"), "email", "number", "text"]
    debounce: int
        An optional int in miliseconds that will wait that amount of time before updating.
    on_change : callable
        An optional callback invoked when this text input's value changes.
    args : tuple
        An optional tuple of args to pass to the callback.
    kwargs : dict
        An optional dict of kwargs to pass to the callback.
    placeholder : str or None
        An optional string displayed when the text input is empty. If None,
        no text is displayed. This argument can only be supplied by keyword.
    disabled : bool
        An optional boolean, which disables the text input if set to True.
        The default is False. This argument can only be supplied by keyword.
    label_visibility : "visible", "hidden", or "collapsed"
        The visibility of the label. If "hidden", the label doesn't show but there
        is still empty space for it above the widget (equivalent to label="").
        If "collapsed", both the label and the space are removed. Default is
        "visible". This argument can only be supplied by keyword.

    Returns
    -------
    str
        The current keyup values of the text input widget.
"""   
    if key is None:
        key = "st_keyup_" + label

    component_value = _component_func(
        label=label,
        value=value,
        key=key,
        debounce=debounce,
        default=value,
        max_chars=max_chars,
        type=type,
        placeholder=placeholder,
        disabled=disabled,
        label_visibility=label_visibility,
    )

    if on_change is not None:
        if "__previous_values__" not in st.session_state:
            st.session_state["__previous_values__"] = {}

        if component_value != st.session_state["__previous_values__"].get(key, value):
            st.session_state["__previous_values__"][key] = component_value

            if args is None:
                args = ()
            if kwargs is None:
                kwargs = {}
            on_change(*args, **kwargs)

    return component_value


def main():
    from datetime import datetime

    st.write("## Default keyup input")
    value = st_keyup("Enter a value")

    st.write(value)

    "## Keyup input with hidden label"
    value = st_keyup("You can't see this", label_visibility="hidden")

    "## Keyup input with collapsed label"
    value = st_keyup("This either", label_visibility="collapsed")

    "## Keyup with max_chars 5"
    value = st_keyup("Keyup with max chars", max_chars=5)

    "## Keyup input with password type"
    value = st_keyup("Password", value="Hello World", type="password")

    "## Keyup input with disabled"
    value = st_keyup("Disabled", value="Hello World", disabled=True)

    "## Keyup input with default value"
    value = st_keyup("Default value", value="Hello World")

    "## Keyup input with placeholder"
    value = st_keyup("Has placeholder", placeholder="A placeholder")

    "## Keyup input with 500 millesecond debounce"
    value = st_keyup("Enter a second value debounced", debounce=500)

    st.write(value)

    def on_change():
        st.write("Value changed!", datetime.now())

    def on_change2(*args, **kwargs):
        st.write("Value changed!", args, kwargs)

    "## Keyup input with on_change callback"
    value = st_keyup("Has an on_change", on_change=on_change)

    "## Keyup input with on_change callback and debounce"
    value = st_keyup("On_change + debounce", on_change=on_change, debounce=1000)
    st.write(value)

    "## Keyup input with args"
    value = st_keyup(
        "Enter a fourth value...",
        on_change=on_change2,
        args=("Hello", "World"),
        kwargs={"foo": "bar"},
    )
    st.write(value)

    "## Standard text input for comparison"
    value = st.text_input("Enter a value")

    st.write(value)

    st.write(st.session_state)


if __name__ == "__main__":
    main()
