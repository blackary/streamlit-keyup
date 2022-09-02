from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

build_dir = Path(__file__).parent.absolute() / "frontend"
_component_func = components.declare_component("st_keyup", path=str(build_dir))


def st_keyup(
    label: str,
    value: str = "",
    key: Optional[str] = None,
    debounce: int = 0,
):
    """
    Generate a text input that renders on keyup, debouncing the input by the
    specified amount of milliseconds.

    Debounce means that it will wait at least the specified amount of milliseconds
    before updating the value. This is useful for preventing excessive updates
    when the user is typing. Since the input updating will cause the app to rerun,
    if you are having performance issues, you should consider setting a debounce
    value.
    """
    component_value = _component_func(
        label=label,
        value=value,
        key=key,
        debounce=debounce,
        default=value,
    )

    return component_value


def main():
    st.write("## Default keyup input")
    value = st_keyup("Enter a value")

    st.write(value)

    "## Keyup input with default value"
    value = st_keyup("Enter a second value", value="Hello World")

    st.write(value)

    "## Keyup input with 500 millesecond debounce"
    value = st_keyup("Enter a second value", debounce=500)

    st.write(value)

    "## Standard text input for comparison"
    value = st.text_input("Enter a value")

    st.write(value)


if __name__ == "__main__":
    main()
