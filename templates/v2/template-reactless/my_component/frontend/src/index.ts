import { Component, ComponentArgs } from "@streamlit/component-v2-lib";

export type ComponentState = {
  num_clicks: number;
};

export type ComponentData = {
  name: string;
};

// Handle the possibility of multiple instances of the component to keep track
// of any long-running state for each component instance.
const instances: WeakMap<ComponentArgs["parentElement"], { numClicks: number }> = new WeakMap();

const MyComponent: Component<ComponentState, ComponentData> = (args) => {
  const { parentElement, data, setStateValue } = args;

  const rootElement = parentElement.querySelector(".component-root");
  if (!rootElement) {
    throw new Error("Unexpected: root element not found");
  }

  // Set dynamic content
  const heading = rootElement.querySelector("h1");
  if (heading) {
    heading.textContent = `Hello, ${data.name}!`;
  }

  // Wire up interactions on existing DOM from Python-provided HTML
  const button = rootElement.querySelector<HTMLButtonElement>("button");
  if (!button) {
    throw new Error("Unexpected: button element not found");
  }

  const handleClick = () => {
    const numClicks = (instances.get(parentElement)?.numClicks || 0) + 1;
    instances.set(parentElement, { numClicks });
    setStateValue("num_clicks", numClicks);
  };

  // Set up event listener for the button when the component is first
  // initialized
  if (!instances.has(parentElement)) {
    button.addEventListener("click", handleClick);
    instances.set(parentElement, { numClicks: 0 });
  }

  // Cleanup
  return () => {
    button.removeEventListener("click", handleClick);
    instances.delete(parentElement);
  };
};

export default MyComponent;
