import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import {
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
    ModalButton,
} from "baseui/modal";
import { KIND as ButtonKind } from "baseui/button";


interface Props {
    title: string,
    body: string,
    isOpen: boolean,
    role: string,
    size: string
}


class BaseWebModal extends StreamlitComponentBase<Props> {
    constructor(props: any) {
        super(props);
        this.state = {
            title: this.props.args["title"],
            body: this.props.args["body"],
            isOpen: this.props.args["is_open"],
            role: this.props.args["role"],
            size: this.props.args["size"]
        }
    };
    public componentDidMount() { Streamlit.setFrameHeight(250) }
    public render = (): ReactNode => {
        return (
            <Modal
                isOpen={this.state.isOpen}
                size={this.state.size}
                role={this.state.role}
                onClose={this.onClose}
            >
                {console.log(this.state)}
                <ModalHeader>{this.state.title}</ModalHeader>
                <ModalBody>
                    {this.state.body}
                </ModalBody>
                <ModalFooter>
                    <ModalButton
                        onClick={this.onClose}
                        kind={ButtonKind.tertiary}>
                        Cancel
                    </ModalButton>
                    <ModalButton onClick={this.onClose}>Okay</ModalButton>
                </ModalFooter>
            </Modal>
        )
    };

    private onClose = () => {
        this.setState({ isOpen: false });
        Streamlit.setComponentValue(null)
    }
}

export default withStreamlitConnection(BaseWebModal)