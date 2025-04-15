import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
  ReactElement,
} from "react"

/**
 * This is a React-based component template. The props are passed from the
 * Streamlit library, and your custom arguments can be accessed via the `args` prop.
 */
function MyComponent({ args, disabled, theme }: ComponentProps): ReactElement {
  const { name } = args

  const [isFocused, setIsFocused] = useState(false)
  const [numClicks, setNumClicks] = useState(0)

  const style: React.CSSProperties = useMemo(() => {
    if (!theme) return {}

    // Use the theme object to style the button border. Alternatively, the
    // theme style is defined in CSS variables.
    const borderStyling = `1px solid ${isFocused ? theme.primaryColor : "gray"}`
    return { border: borderStyling, outline: borderStyling }
  }, [theme, isFocused])

  // `setFrameHeight` should be called on the first render and whenever the size
  // might change (e.g., due to a DOM update).
  useEffect(() => {
    Streamlit.setFrameHeight()
    // Adding the style and theme as dependencies since they might
    // affect the visual size of the component.
  }, [style, theme])

  /** Click handler for our "Click Me!" button. */
  const onClicked = useCallback((): void => {
    const newNumClicks = numClicks + 1
    setNumClicks(newNumClicks)
    Streamlit.setComponentValue(newNumClicks)
  }, [numClicks])

  /** Focus handler for our "Click Me!" button. */
  const onFocus = useCallback((): void => {
    setIsFocused(true)
  }, [])

  /** Blur handler for our "Click Me!" button. */
  const onBlur = useCallback((): void => {
    setIsFocused(false)
  }, [])

  // Display a button and some text. When the button is clicked, the `numClicks`
  // state variable is incremented, and its new value is sent back to Streamlit,
  // where it will be available to the Python program.
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
// You don't need to edit `withStreamlitConnection` (but you're welcome to!).
export default withStreamlitConnection(MyComponent)
