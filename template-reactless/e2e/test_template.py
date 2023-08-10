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
    page.pause()
    frame_0 = page.frame_locator(
        'iframe[title="my_component\\.my_component"]'
    )

    text = page.get_by_test_id("stMarkdownContainer")

    expect(text).to_have_text("You've clicked 0 times!")

    frame_0.get_by_role("button", name="Click me!").click()

    expect(text).to_have_text("You've clicked 1 times!")