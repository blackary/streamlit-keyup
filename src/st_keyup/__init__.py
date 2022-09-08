from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

build_dir = Path(__file__).parent.absolute() / "frontend"
_component_func = components.declare_component("st_keyup", path=str(build_dir))


def st_keyup(
    label: str,
    value: str = "",
    key: Optional[str] = None,
    debounce: Optional[int] = None,
    on_change: Optional[Callable] = None,
    args: Optional[Tuple[Any, ...]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
):
    """
    Generate a text input that renders on keyup, debouncing the input by the
    specified amount of milliseconds.

    Debounce means that it will wait at least the specified amount of milliseconds
    before updating the value. This is useful for preventing excessive updates
    when the user is typing. Since the input updating will cause the app to rerun,
    if you are having performance issues, you should consider setting a debounce
    value.

    on_change is a callback function that will be called when the value changes.

    args and kwargs are optional arguments which are passed to the on_change callback
    function
    """

    if key is None:
        key = "st_keyup_" + label

    component_value = _component_func(
        label=label,
        value=value,
        key=key,
        debounce=debounce,
        default=value,
    )

    if on_change is not None:
        if "__previous_values__" not in st.session_state:
            st.session_state["__previous_values__"] = {}

        if component_value != st.session_state["__previous_values__"].get(key, value):
            st.session_state["__previous_values__"][key] = component_value

            if on_change:
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

    "## Keyup input with default value"
    value = st_keyup("Enter a second value", value="Hello World")

    st.write(value)

    "## Keyup input with 500 millesecond debounce"
    value = st_keyup("Enter a second value debounced", debounce=500)

    st.write(value)

    def on_change():
        st.write("Value changed!", datetime.now())

    def on_change2(*args, **kwargs):
        st.write("Value changed!", args, kwargs)

    "## Keyup input with on_change callback"
    value = st_keyup("Enter a third value", on_change=on_change)

    "## Keyup input with on_change callback and debounce"
    value = st_keyup("Enter a third value...", on_change=on_change, debounce=1000)
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
