import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  explanation: string
  isFocused: boolean
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class SelectExplain extends StreamlitComponentBase<State> {
  public state = { explanation: "", isFocused: false }

  public render = (): ReactNode => {
    // Streamlit sends us a theme object via props that we can use to ensure
    // that our component has visuals that match the active theme in a
    // streamlit app.
    const { theme } = this.props
    const style: React.CSSProperties = {}

    // Maintain compatibility with older versions of Streamlit that don't send
    // a theme object.
    if (theme) {
      // Use the theme object to style our button border. Alternatively, the
      // theme style is defined in CSS vars.
      const borderStyling = `1px solid ${
        this.state.isFocused ? theme.primaryColor : "gray"
      }`
      style.border = borderStyling
      style.outline = borderStyling
    }

    return (
      <span>
        <button
          style={style}
          onClick={this.onClicked}
          disabled={this.props.disabled}
          onFocus={this._onFocus}
          onBlur={this._onBlur}
        >
          Explain highlighted text
        </button>
      </span>
    )
  }

  private onClicked = async (): Promise<void> => {
    const selectedText = window.top?.getSelection()?.toString() ?? ""
    if (selectedText === "") {
      return
    }

    const prompt = `Explain the following ML term: ${selectedText}.\n`
    const response = await fetch(
      // TODO: Use a better model
      "https://api-inference.huggingface.co/models/gpt2",
      {
        headers: {
          // TODO: Get auth token from user?
          // Authorization: `Bearer ${process.env.HF_TOKEN}`,
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify({ inputs: prompt }),
      }
    )
    const responseJson = await response.json()
    const generatedText = responseJson[0]?.generated_text ?? ""
    const explanation = generatedText.startsWith(prompt)
      ? generatedText.slice(prompt.length)
      : generatedText

    // TODO: Handle async order effects properly
    this.setState(
      () => ({ explanation }),
      () => Streamlit.setComponentValue(this.state.explanation)
    )
  }

  private _onFocus = (): void => {
    this.setState({ isFocused: true })
  }

  private _onBlur = (): void => {
    this.setState({ isFocused: false })
  }
}

export default withStreamlitConnection(SelectExplain)
