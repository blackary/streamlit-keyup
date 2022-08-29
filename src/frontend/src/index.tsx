import { Streamlit, RenderData } from "streamlit-component-lib"
import { debounce } from "underscore"

declare global {
  interface Window {
    rendered: boolean
  }
}

function onKeyUp(event: any): void {
  Streamlit.setComponentValue(event.target.value)
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event: Event): void {
  // Get the RenderData from the event
  if (!window.rendered) {
    const data = (event as CustomEvent<RenderData>).detail

    const label: string = data.args["label"]
    const value: string = data.args["value"]
    const debounce_time: number = data.args["debounce"]

    const input = document.getElementsByTagName("input")[0] as HTMLInputElement

    const label_el = document.getElementsByTagName(
      "label"
    )[0] as HTMLLabelElement

    if (label_el) {
      label_el.innerText = label
    }

    if (value && !input.value) {
      input.value = value
    }

    if (debounce_time > 0) {
      input.onkeyup = debounce(onKeyUp, debounce_time)
    }
    else {
      input.onkeyup = onKeyUp
    }

    window.rendered = true
  }
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight(93)
