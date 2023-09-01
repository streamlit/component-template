from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = ROOT_DIRECTORY / "material_login" / "example.py"

@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(BASIC_EXAMPLE_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_material_login(page: Page):
    frame = page.frame_locator(
        'iframe[title="material_login\\.material_login"]'
    )
    component_return_value = page.get_by_test_id('stMarkdownContainer')
    component_return_value_json = page.get_by_test_id('stJson')

    email_field = frame.get_by_placeholder("username@domain.com")
    password_field = frame.get_by_placeholder("your password")
    invalid_username_text = frame.get_by_text("username must be a valid email")
    invalid_password_text = frame.get_by_text("password is a required field")
    login_button = frame.get_by_role("button", name="Login")
    cancel_button = frame.get_by_role("button", name="Cancel")

    email_field.click()
    email_field.fill("hello")

    expect(invalid_username_text).to_be_visible()
    expect(invalid_password_text).to_be_visible()
    expect(login_button).to_be_disabled()

    email_field.click()
    email_field.fill("hello@hello.com")
    password_field.click()
    password_field.fill("password")
    expect(invalid_username_text).to_be_hidden()
    expect(invalid_password_text).to_be_hidden()
    expect(component_return_value).to_have_text('None')
    login_button.click()

    expect(component_return_value_json).to_contain_text("\"username\":\"hello@hello.com\"")
    expect(component_return_value_json).to_contain_text("\"password\":\"password\"")
    cancel_button.click()
    expect(email_field).to_be_empty()
    expect(password_field).to_be_empty()
    expect(invalid_username_text).to_be_hidden()
    expect(invalid_password_text).to_be_hidden()
    expect(component_return_value_json).to_have_text('{}')
