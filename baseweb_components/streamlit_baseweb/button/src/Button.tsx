import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { useEffect, ReactNode, useState } from "react"
import { Button } from "baseui/button";


let state = "idle";

class BaseWebButton extends StreamlitComponentBase {
    public componentDidMount() {
        Streamlit.setFrameHeight(70);
    }
    public componentDidUpdate(): void {
        if (state === "clicked") {
            state = "reset"
        }
        else if (state === "reset") {
            Streamlit.setComponentValue(false);
            state = "idle"
        }
    }

    public render = (): ReactNode => {
        return (
            <Button
                disabled={this.props.args["disabled"]}
                size={this.props.args["size"]}
                shape={this.props.args["shape"]}
                kind={this.props.args["kind"]}
                onClick={this.onClicked}>
                {this.props.args["label"]}
            </Button>
        );
    }

    public onClicked = () => {
        Streamlit.setComponentValue(true);
        state = "clicked"
    }

}

export default withStreamlitConnection(BaseWebButton)