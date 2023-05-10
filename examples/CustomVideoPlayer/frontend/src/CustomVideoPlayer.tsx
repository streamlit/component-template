import React, { useEffect } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"

/**
 * VidePlayer example.
 */
const CustomVidePlayer: React.FC<ComponentProps> = (props) => {
  useEffect(() => {
    Streamlit.setFrameHeight()
  })

  const file_url = document.referrer + props.args.file_url.replace(/^\//gm, '');
  return (
    <div>
      <video width="320" height="240" controls loop>
        <source src={file_url} type="video/mp4"/>
      </video>
      <div><a href={file_url}>Download</a></div>
    </div>
  )
}

export default withStreamlitConnection(CustomVidePlayer)
