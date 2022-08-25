import os
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "st_keyup", url="http://localhost:3001"
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("st_keyup", path=build_dir)


def st_keyup(
    label: str,
    value: str = "",
    key: Optional[str] = None,
):
    component_value = _component_func(
        label=label,
        value=value,
        key=key,
        default="",
    )

    return component_value


def main():
    value = st_keyup("Enter a value")

    st.write(value)

    value = st_keyup("Enter a second value", value="Hello World")

    st.write(value)

    value = st.text_input("Enter a value")

    st.write(value)


if __name__ == "__main__":
    if not _RELEASE:
        main()
