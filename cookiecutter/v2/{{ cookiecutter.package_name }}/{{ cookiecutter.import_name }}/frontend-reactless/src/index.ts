import { Component, ComponentArgs } from "@streamlit/component-v2-lib";

export type ComponentState = {
  num_clicks: number;
};

export type ComponentData = {
  name: string;
};

const Root: Component<ComponentState, ComponentData> = (args) => {
  // TODO:
};

export default Root;


