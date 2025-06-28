*** Settings ***

Library             SeleniumLibrary

*** Variables ***

${st_keyup_iframe_locator}   css:iframe[title="st_keyup.st_keyup"]
${additional_chrome_options}            ""

*** Keywords ***

Do Suite Setup
    ${process} =   Start Process
    ...    streamlit                   run   streamlit_app.py
    ...        --server.port                     8501
    ...        --server.headless                 true
    ...        --browser.gatherUsageStats        false
    Log                                PID: ${process.pid}
    VAR        ${PROCESS}    ${process}   scope=SUITE

Do Suite Teardown
    Log                                 PID: ${PROCESS.pid}
    ${result} =   Terminate Process     ${PROCESS}
    Log                                 Terminate process result: ${result}

Input text into st_keyup
    [Arguments]                         ${text}
    Wait until element is visible       ${st_keyup_iframe_locator}
    Select frame                        ${st_keyup_iframe_locator}
    Input text                          css:input[type="text"]      ${text}
    Unselect frame

Open URL
    [Arguments]                         ${url}
    Create Chrome WebDriver
    Maximize Browser Window
    Go To                               ${url}
    Wait For Condition                  return document.readyState == "complete"
    Wait Until Page Does Not Contain    Running...
    Sleep                               1 second
    ${result}=   Run Keyword And Return Status   Page Should Not Contain      Traceback
    # Log To Console  ${result}
    IF   ${result} != True
        ${error_text}=  Get Text    css:.message
        Fail    Page should not contain "Traceback". Error: ${error_text}
    END

Create Chrome WebDriver
    ${chrome_options} =    Evaluate    selenium.webdriver.ChromeOptions()
    # Call Method    ${chrome_options}    add_argument    --no-sandbox
    Call Method    ${chrome_options}    add_argument    ${additional_chrome_options}
    Create WebDriver    Chrome    options=${chrome_options}