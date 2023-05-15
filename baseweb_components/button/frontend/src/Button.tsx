import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { useEffect, ReactNode } from "react"
import { Button } from "baseui/button";


class BaseWebButton extends StreamlitComponentBase {
    public componentDidMount() { Streamlit.setFrameHeight() }
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

    private onClicked = () => {
        Streamlit.setComponentValue(null)
    }

}

export default withStreamlitConnection(BaseWebButton)