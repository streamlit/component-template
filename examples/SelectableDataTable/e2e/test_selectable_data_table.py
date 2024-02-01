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

    expect(frame.get_by_role('checkbox')).to_have_count(6)
    root_checkbox = frame.get_by_role('checkbox').nth(0)
    first_row_checkbox = frame.get_by_role('checkbox').nth(1)
    second_row_checkbox = frame.get_by_role('checkbox').nth(2)
    third_row_checkbox = frame.get_by_role('checkbox').nth(3)
    fourth_row_checkbox = frame.get_by_role('checkbox').nth(4)
    fifth_row_checkbox = frame.get_by_role('checkbox').nth(5)
    none_root_checkboxes = [
        first_row_checkbox,
        second_row_checkbox,
        third_row_checkbox,
        fourth_row_checkbox,
        fifth_row_checkbox
    ]

    root_checkbox.check()
    for checkbox in none_root_checkboxes:
        expect(checkbox).to_be_checked()

    first_row_checkbox.uncheck()
    expect(root_checkbox).not_to_be_checked()
    expect(root_checkbox).to_have_attribute('data-indeterminate', 'true')

    for checkbox in none_root_checkboxes:
        checkbox.uncheck()

    expect(root_checkbox).not_to_be_checked()
    expect(root_checkbox).to_have_attribute('data-indeterminate', 'false')

    for checkbox in none_root_checkboxes:
        checkbox.check()

    expect(root_checkbox).to_be_checked()
    expect(root_checkbox).to_have_attribute('data-indeterminate', 'false')
