import {
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { Button } from "baseui/button";

interface State {
    numClicks: number
    isFocused: boolean
}

class BaseWebButton extends StreamlitComponentBase<State> {
    public render = (): ReactNode => {
        return (
            <Button onClick={() => alert("click")}>Hello</Button>
        );
    }
}

export default withStreamlitConnection(BaseWebButton)