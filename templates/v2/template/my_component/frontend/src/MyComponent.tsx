import { ComponentArgs } from "@streamlit/component-v2-lib";
import {
  CSSProperties,
  FC,
  ReactElement,
  useCallback,
  useMemo,
  useState,
} from "react";

export type MyComponentStateShape = {
  num_clicks: number;
};

export type MyComponentDataShape = {
  // disabled: boolean;
  name: string;
};

export type MyComponentProps = Pick<
  ComponentArgs<MyComponentStateShape, MyComponentDataShape>,
  "setStateValue"
> &
  MyComponentDataShape;

/**
 * A template for creating Streamlit components with React
 *
 * This component demonstrates the essential structure and patterns for
 * creating interactive Streamlit components, including:
 * - Accessing data sent from Python
 * - Managing component state with React hooks
 * - Communicating back to Streamlit via setStateValue()
 * - Using the Streamlit CSS Custom Properties for styling
 *
 * @param props.name - Name passed from the Python side to display in the component
 * @param props.setStateValue - Function to send state updates back to Streamlit
 * @returns The rendered component
 */
const MyComponent: FC<MyComponentProps> = ({
  name,
  setStateValue,
}): ReactElement => {
  // Frontend component state
  const [isFocused, setIsFocused] = useState(false);
  const [numClicks, setNumClicks] = useState(0);

  /**
   * Dynamic styling based on Streamlit theme and component state
   * This demonstrates how to use the Streamlit theme for consistent styling
   */
  const style = useMemo<CSSProperties>(() => {
    // Access theme values via CSS Custom Properties that are set by Streamlit.
    const colorToUse = isFocused
      ? "var(--st-primary-color)"
      : "var(--st-gray-color)";

    const borderStyling = `1px solid ${colorToUse}`;

    return {
      border: borderStyling,
      outline: borderStyling,
    };
  }, [isFocused]);

  /**
   * Click handler for the button
   * Demonstrates how to update component state and send data back to Streamlit
   */
  const onClicked = useCallback((): void => {
    const newNumClicks = numClicks + 1;
    // Update local state
    setNumClicks(newNumClicks);

    // Send state value back to Streamlit (will be available in Python)
    setStateValue("num_clicks", newNumClicks);
  }, [numClicks, setStateValue]);

  /**
   * Focus handler for the button
   * Updates visual state when the button receives focus
   */
  const onFocus = useCallback((): void => {
    setIsFocused(true);
  }, []);

  /**
   * Blur handler for the button
   * Updates visual state when the button loses focus
   */
  const onBlur = useCallback((): void => {
    setIsFocused(false);
  }, []);

  return (
    <span>
      <h1>Hello, {name}!</h1>
      <button
        style={style}
        onClick={onClicked}
        // disabled={disabled}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        Click Me!
      </button>
    </span>
  );
};

export default MyComponent;
