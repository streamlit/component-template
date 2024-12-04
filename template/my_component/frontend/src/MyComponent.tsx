import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useCallback, useEffect, useMemo, useState, ReactElement } from "react"

/**
 * This is a React-based component template. The passed props are coming from the 
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const { name } = args

  const [isFocused, setIsFocused] = useState(false)
  const [numClicks, setNumClicks] = useState(0)

  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {}

    // Use the theme object to style our button border. Alternatively, the
    // theme style is defined in CSS vars.
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    return { border: borderStyling, outline: borderStyling }
  }, [theme, isFocused])

  useEffect(() => {
    Streamlit.setComponentValue(numClicks)
  }, [numClicks])

  // setFrameHeight should be called on first render and evertime the size might change (e.g. due to a DOM update).
  // Adding the style and theme here since they might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [style, theme])

  /** Click handler for our "Click Me!" button. */
  const onClicked = useCallback((): void => {
    setNumClicks((prevNumClicks) => prevNumClicks + 1)
  }, [])

  /** Focus handler for our "Click Me!" button. */
  const onFocus = useCallback((): void => {
    setIsFocused(true)
  }, [])

  /** Blur handler for our "Click Me!" button. */
  const onBlur = useCallback((): void => {
    setIsFocused(false)
  }, [])

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
