from __future__ import annotations

from typing import Callable

import streamlit as st


def handle_input_change():
    st.toast("Input changed")


my_component = st.components.v2.component(
    "interactive_button",
    html="""
    <label id="label" for="text_input">This is a label</label>
    <div class="input">
        <input name="text_input" id="input_box" class="stTextInput"/>
    </div>
    """,
    js="""
    export default function(component) {
      const { data, setStateValue, setTriggerValue, parentElement } = component;

        let input = parentElement.querySelector('.input input.stTextInput');

        let label = parentElement.querySelector('#label');

        label.textContent = data.label;

        if (data.placeholder) {
            input.placeholder = data.placeholder;
        }

        if (data.disabled) {
            input.disabled = data.disabled;
        }

        if (data.max_chars) {
            input.maxLength = data.max_chars;
        }

        if (data.type) {
            input.type = data.type;
        }

        if (data.label_visibility == "hidden" || data.label_visibility == "collapsed") {
            label.style.display = "none";
        }
        else {
            label.style.display = "block";
        }

        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        if (data.debounce) {
            input.onkeyup = debounce((event) => {
                console.log(event.target.value);
                setStateValue('input_value', event.target.value);
            }, data.debounce);
        } else {
            input.onkeyup = (event) => {
                console.log(event.target.value);
                setStateValue('input_value', event.target.value);
            };
        }
    }
    """,
)


def component_wrapper(
    label: str,
    value: str = "",
    max_chars: int | None = None,
    key: str | None = None,
    type: str = "default",
    debounce: int | None = None,
    on_change: Callable | None = None,
    args: tuple | None = None,
    kwargs: dict | None = None,
    *,
    placeholder: str = "",
    disabled: bool = False,
    label_visibility: str = "visible",
):
    _on_change: Callable | None = None

    if on_change:
        args = args or ()
        kwargs = kwargs or {}

        def _on_change():
            on_change(*args, **kwargs)

    component = my_component(
        on_input_value_change=_on_change,
        isolate_styles=False,
        default={"input_value": value},
        data={
            "label": label,
            "max_chars": max_chars,
            "type": type,
            "debounce": debounce,
            "placeholder": placeholder,
            "disabled": disabled,
            "label_visibility": label_visibility,
        },
        key=key,
    )

    return component.input_value


result = component_wrapper(
    "With on_change", on_change=handle_input_change, key="my_input"
)

st.write(result)

# Test all the different parameters

component_wrapper("With label", on_change=handle_input_change, key="my_input_1")
component_wrapper(
    "With value", value="Hello", on_change=handle_input_change, key="my_input_2"
)
component_wrapper(
    "With max_chars", max_chars=10, on_change=handle_input_change, key="my_input_3"
)
component_wrapper(
    "With type", type="password", on_change=handle_input_change, key="my_input_4"
)
result = component_wrapper(
    "With debounce", debounce=500, on_change=handle_input_change, key="my_input_5"
)
st.write(result)

component_wrapper(
    "With disabled",
    disabled=True,
    on_change=handle_input_change,
    key="my_input_6",
)
component_wrapper(
    "With placeholder",
    placeholder="Enter your name",
    on_change=handle_input_change,
    key="my_input_7",
)
component_wrapper(
    "With label_visibility",
    label_visibility="hidden",
    on_change=handle_input_change,
    key="my_input_8",
)

# Test args and kwargs


def handle_input_change_with_args(*args, **kwargs):
    st.toast(f"Args: {args}")
    st.toast(f"Kwargs: {kwargs}")


component_wrapper(
    "With args",
    on_change=handle_input_change_with_args,
    args=("Hello", "World"),
    kwargs={"arg3": "Hello", "arg4": "World"},
    key="my_input_9",
)
