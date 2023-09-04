from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = ROOT_DIRECTORY / "custom_dataframe" / "example.py"

@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(BASIC_EXAMPLE_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_dataframe(page: Page):
    frame = page.frame_locator(
        'iframe[title="custom_dataframe\\.custom_dataframe"]'
    )
    cell_in_frame = frame.get_by_role("cell", name="Jason")
    expect(cell_in_frame).to_be_visible()

    st_table = page.get_by_test_id('stTable')

    frame.get_by_role("button", name="Return dataframe").click()
    cell_generated = st_table.get_by_role("cell", name="Jason")
    expect(cell_generated).to_be_visible()
