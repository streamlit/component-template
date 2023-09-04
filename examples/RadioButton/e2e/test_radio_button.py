from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = ROOT_DIRECTORY / "radio_button" / "example.py"


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(BASIC_EXAMPLE_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_user_input(page: Page):
    frame = page.frame_locator(
        'iframe[title="radio_button\\.radio_button"]'
    )

    radio_group = frame.get_by_role("radiogroup")
    first_radio = radio_group.get_by_text("one bat")
    second_radio = radio_group.get_by_text("TWO bats")
    text = page.get_by_text("This many")

    expect(first_radio).to_be_checked()
    expect(second_radio).not_to_be_checked()
    expect(text).to_have_text("This many: one bat")

    second_radio.check()

    expect(first_radio).not_to_be_checked()
    expect(second_radio).to_be_checked()
    expect(text).to_have_text("This many: TWO bats")

    # check if click on checked option will not uncheck it
    second_radio.check()

    expect(first_radio).not_to_be_checked()
    expect(second_radio).to_be_checked()
    expect(text).to_have_text("This many: TWO bats")
