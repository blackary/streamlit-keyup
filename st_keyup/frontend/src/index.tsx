import { Streamlit, RenderData } from "streamlit-component-lib"

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
  const data = (event as CustomEvent<RenderData>).detail

  const label: string = data.args["label"]
  //const value: string = data.args["value"]
  //const key: string = data.args["key"]

  const input = document.getElementsByTagName("input")[0] as HTMLInputElement

  const label_el = document.getElementsByTagName("label")[0] as HTMLLabelElement

  if (label_el) {
    label_el.innerText = label
  }

  input.onkeyup = onKeyUp
}

// Attach our `onRender` handler to Streamlit's render event.
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

// Tell Streamlit we're ready to start receiving data. We won't get our
// first RENDER_EVENT until we call this function.
Streamlit.setComponentReady()

// Finally, tell Streamlit to update our initial height. We omit the
// `height` parameter here to have it default to our scrollHeight.
Streamlit.setFrameHeight(93)
