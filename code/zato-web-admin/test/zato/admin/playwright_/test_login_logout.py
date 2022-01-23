# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    # Go to http://localhost:8183/accounts/login/?next=/zato/
    page.goto("http://localhost:8183/accounts/login/?next=/zato/")

    # Click input[name="username"]
    page.click("input[name=\"username\"]")

    # Fill input[name="username"]
    page.fill("input[name=\"username\"]", "admin")

    # Press Tab
    page.press("input[name=\"username\"]", "Tab")

    # Fill input[name="password"]
    page.fill("input[name=\"password\"]", "************")

    # Press Enter
    page.press("input[name=\"password\"]", "Enter")
    # assert page.url == "http://localhost:8183/zato/"

    # Click text=My settings
    page.click("text=My settings")
    # assert page.url == "http://localhost:8183/account/settings/basic/"

    # Click text=Log out (admin)
    page.click("text=Log out (admin)")
    # assert page.url == "http://localhost:8183/accounts/login/?next=/zato/"

    # Click input[name="password"]
    page.click("input[name=\"password\"]")

    # Fill input[name="password"]
    page.fill("input[name=\"password\"]", "************")

    # Click text=Log in
    page.click("text=Log in")
    # assert page.url == "http://localhost:8183/zato/"

    # Click text=My settings
    page.click("text=My settings")
    # assert page.url == "http://localhost:8183/account/settings/basic/"

    # Click text=Log out (admin)
    page.click("text=Log out (admin)")
    # assert page.url == "http://localhost:8183/accounts/login/?next=/zato/"

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
