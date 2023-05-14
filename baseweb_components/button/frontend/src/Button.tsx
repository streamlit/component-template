import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { Button, SIZE, SHAPE, KIND } from "baseui/button";

interface State {
    label: string,
    size: string,
    shape: string,
    isLoading: boolean,
    isSelected: boolean,
    disabled: boolean,
    kind: string
}


class BaseWebButton extends StreamlitComponentBase<State> {
    public state = { label: 'Button', size: SIZE.default, shape: SHAPE.default, isLoading: false, isSelected: false, disabled: false, kind: KIND.primary }


    public render = (): ReactNode => {
        const label = this.props.args["label"]
        const disabled = this.state.disabled
        const { theme } = this.props

        return (
            <Button
                disabled
                onClick={this.onClicked}>
                {label}
            </Button>
        );
    }

    private onClicked = (): void => {
        Streamlit.events.dispatchEvent();
        console.log('you clicked')
    }

}



export default withStreamlitConnection(BaseWebButton)