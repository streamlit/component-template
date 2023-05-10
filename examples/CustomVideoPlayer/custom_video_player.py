import streamlit
from streamlit import runtime
from streamlit.runtime import caching

import streamlit.components.v1 as components

_custom_videoplayer = components.declare_component(
    "custom_videoplayer", url="http://localhost:3001",
)


def custom_videoplayer(data_or_filename, mimetype: str = "video/mp4", key: str = None):
    dg = streamlit._main
    coordinates = dg._get_delta_path_str()
    
    if runtime.exists():
        file_url = runtime.get_instance().media_file_mgr.add(
            data_or_filename, mimetype, coordinates
        )
        caching.save_media_data(data_or_filename, mimetype, coordinates)
    else:
        # When running in "raw mode", we can't access the MediaFileManager.
        file_url = ""

    return _custom_videoplayer(file_url=file_url, key=key, default=None)


filepath = "./pexels-cottonbro-studio-6853337-338x640-25fps.mp4"
custom_videoplayer(filepath)