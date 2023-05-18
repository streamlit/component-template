import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import {useStyletron} from 'baseui';
import React, { ReactNode } from "react"
import {
    AppNavBar,
    setItemActive
} from "baseui/app-nav-bar";
import {
    ChevronDown,
    Delete,
    Overflow,
    Upload
  } from "baseui/icon";

  const [css] = useStyletron();

class BaseWebNavigationBar extends StreamlitComponentBase {
    constructor(props: any) {
        super(props);
        this.state = { mainItems: this.props.args["main_items"] }
    }
    public componentDidMount(): void { Streamlit.setFrameHeight(1000) };
    public componentDidUpdate(): void {Streamlit.setFrameHeight(1000) }
    public render = (): ReactNode => {
        return (
            <AppNavBar
                title={this.props.args["title"]}
                mainItems={this.props.args["main_items"]}
                onMainItemSelect={item => {
                    this.setState({ mainItems: item });
                }}
                username={this.props.args["user_name"]}
                usernameSubtitle={this.props.args["username_subtitle"]}
                userItems={this.props.args['user_items']}
                userImgUrl={this.props.args['user_image_url']}
                onUserItemSelect={item => console.log(item)}
            />
        );

    }
}

export default withStreamlitConnection(BaseWebNavigationBar)