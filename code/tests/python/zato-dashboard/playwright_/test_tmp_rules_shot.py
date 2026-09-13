def test_shot(logged_in_page, zato_dashboard):
    page = logged_in_page
    url = zato_dashboard['dashboard_url'] + '/zato/alerting/rules/config/?cluster=1'
    for _ in range(10):
        page.goto(url)
        if page.locator('#alert-rules-card-soap').count():
            break
        page.wait_for_timeout(3000)
    page.wait_for_selector('#alert-rules-card-soap', state='visible')
    page.click('#alert-rules-card-soap .alert-rules-param-edit[data-field="fault_codes"]')
    page.wait_for_selector('#alert-rules-row-popup', state='visible')
    page.wait_for_timeout(600)
    page.locator('#alert-rules-row-popup').screenshot(path='/tmp/rules_soap.png')
