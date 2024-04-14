import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib";
import React, { ReactNode } from "react";
import {
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalButton,
} from "baseui/modal";
import { KIND as ButtonKind } from "baseui/button";

interface Props {
  title: string;
  body: string;
  isOpen: boolean;
  role: string;
  size: string;
  validationButtonLabel: string;
}

class BaseWebModal extends StreamlitComponentBase<Props> {
  constructor(props: any) {
    super(props);
    this.state = {
      title: this.props.args["title"],
      body: this.props.args["body"],
      isOpen: this.props.args["is_open"],
      role: this.props.args["role"],
      size: this.props.args["size"],
      validationButtonLabel: this.props.args["validation_button_label"],
    };
  }
  componentHeight = Math.min(
    Math.max(250, this.props.args["body"].length / 3),
    500,
  );
  public componentDidMount() {
    Streamlit.setFrameHeight(this.componentHeight);
  }
  public render = (): ReactNode => {
    return (
      <Modal
        isOpen={this.state.isOpen}
        size={this.state.size}
        role={this.state.role}
        onClose={this.onClose}
      >
        <ModalHeader>{this.state.title}</ModalHeader>
        <ModalBody>{this.state.body}</ModalBody>
        <ModalFooter>
          <ModalButton onClick={this.onClose} kind={ButtonKind.tertiary}>
            Cancel
          </ModalButton>
          <ModalButton onClick={this.onConfirm}>
            {this.state.validationButtonLabel}
          </ModalButton>
        </ModalFooter>
      </Modal>
    );
  };

  private onConfirm = () => {
    this.setState({ isOpen: false });
    Streamlit.setComponentValue(true);
  };

  private onClose = () => {
    this.setState({ isOpen: false });
    Streamlit.setComponentValue(null);
  };
}

export default withStreamlitConnection(BaseWebModal);
