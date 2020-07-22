import React, { ReactNode } from "react"
import {
  withStreamlitConnection,
  StreamlitComponentBase,
  Streamlit,
} from "./streamlit"
import PDFJS from "pdfjs-dist"

interface State {
  numClicks: number
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class MyComponent extends StreamlitComponentBase<State> {
  public state = { numClicks: 0 }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const name = this.props.args["name"]

    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
    // be available to the Python program.
    return (
      <span>
        Hello, {name}! &nbsp;
        <button onClick={this.onClicked} disabled={this.props.disabled}>
          Click Me!
        </button>
        <canvas ref="canvas" width={500} height={500} />
      </span>
    )
  }

  private async renderPdf(url: string) {
    const workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS.version}/pdf.worker.js`
    PDFJS.GlobalWorkerOptions.workerSrc = workerSrc

    const pdf = await PDFJS.getDocument(url).promise
    // Assumes each pdf is one page, for now
    const page = await pdf.getPage(1)

    const scale = 1.3
    const viewport = page.getViewport({ scale })

    const canvas = this.refs.canvas as HTMLCanvasElement
    const ctx = canvas.getContext("2d")
    // Resize canvas to fit the pdf page
    canvas.height = viewport.height
    canvas.width = viewport.width

    const renderContext = {
      canvasContext: ctx!,
      viewport: viewport,
    }
    page.render(renderContext)
  }

  /** Click handler for our "Click Me!" button. */
  private onClicked = async () => {
    // Increment state.numClicks, and pass the new value back to
    // Streamlit via `Streamlit.setComponentValue`.
    this.setState(
      (prevState) => ({ numClicks: prevState.numClicks + 1 }),
      () => Streamlit.setComponentValue(this.state.numClicks)
    )
    await this.renderPdf(
      "https://cors-anywhere.herokuapp.com/" +
        "http://puzzledpint.com/files/8315/3168/9544/05-science-v6.pdf"
    )
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
