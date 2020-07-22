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

    // Show a button and some text.
    // When the button is clicked, we'll increment our "numClicks" state
    // variable, and send its new value back to Streamlit, where it'll
    // be available to the Python program.
    return (
      <div style={{ border: "solid" }}>
        <canvas ref="canvas" width={500} height={500} />
      </div>
    )
  }

  public componentDidMount() {
    console.log("Mounted: ", this.props.args)
    const url = this.props.args.url
    const prefix = this.props.args.cors_proxy
      ? "https://cors-anywhere.herokuapp.com/"
      : ""
    this.renderPdf(`${prefix}${url}`)
  }

  private async renderPdf(url: string) {
    console.log("Rendering: ", url)
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
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
