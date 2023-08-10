from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = ROOT_DIRECTORY / "selectable_data_table" / "example.py"

@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(BASIC_EXAMPLE_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_selectable_data_table(page: Page):
    frame = page.frame_locator(
        'iframe[title="selectable_data_table\\.selectable_data_table"]'
    )

    main_checkbox = frame.get_by_role("row", name="First Name Last Name Age").get_by_role("checkbox")
    first_row_checkbox = frame.get_by_role("row", name="Jason Miller 42").get_by_role("checkbox")

    main_checkbox.check()
    expect(first_row_checkbox).to_be_checked()

    expect(page.get_by_text("0:0")).to_be_visible()

    first_row_checkbox.uncheck()
    expect(main_checkbox).not_to_be_checked()


