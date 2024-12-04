import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, useState, ReactElement } from "react"

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const { name } = args

  const [isFocused, setIsFocused] = useState(false)
  const [style, setStyle] = useState<React.CSSProperties>({})
  const [numClicks, setNumClicks] = useState(0)

  useEffect(() => {
    if (!theme) return

    // Use the theme object to style our button border. Alternatively, the
    // theme style is defined in CSS vars.
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    setStyle({ border: borderStyling, outline: borderStyling })
  }, [theme, isFocused])

  useEffect(() => {
    Streamlit.setComponentValue(numClicks)
  }, [numClicks])

  /** Click handler for our "Click Me!" button. */
  const onClicked = (): void => {
    setNumClicks((prevNumClicks) => prevNumClicks + 1)
  }

  /** Focus handler for our "Click Me!" button. */
  const onFocus = (): void => {
    setIsFocused(true)
  }

  /** Blur handler for our "Click Me!" button. */
  const onBlur = (): void => {
    setIsFocused(false)
  }

  // Show a button and some text.
  // When the button is clicked, we'll increment our "numClicks" state
  // variable, and send its new value back to Streamlit, where it'll
  // be available to the Python program.
  return (
    <span>
      Hello, {name}! &nbsp;
      <button
        style={style}
        onClick={onClicked}
        disabled={disabled}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        Click Me!
      </button>
    </span>
  )
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
