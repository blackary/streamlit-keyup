*** Settings ***

Library             SeleniumLibrary

*** Variables ***

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
    # Components v2 renders in Shadow DOM — no iframe, access via JS
    Wait Until Element Is Visible       css:[data-testid='stBidiComponentIsolated']
    Execute Javascript
    ...    var host = document.querySelector("[data-testid='stBidiComponentIsolated']");
    ...    var inp = host.shadowRoot.querySelector("#input");
    ...    inp.value = "${text}";
    ...    inp.dispatchEvent(new Event("input", {bubbles: true, composed: true}));

Open URL
    [Arguments]                         ${url}
    Create Chrome WebDriver
    Maximize Browser Window
    Go To                               ${url}
    Wait For Condition                  return document.readyState == "complete"
    Wait Until Page Does Not Contain    Running...
    Sleep                               1 second
    ${result}=   Run Keyword And Return Status   Page Should Not Contain      Traceback
    IF   ${result} != True
        ${error_text}=  Get Text    css:.message
        Fail    Page should not contain "Traceback". Error: ${error_text}
    END

Create Chrome WebDriver
    ${chrome_options} =    Evaluate    selenium.webdriver.ChromeOptions()
    Call Method    ${chrome_options}    add_argument    ${additional_chrome_options}
    Create WebDriver    Chrome    options=${chrome_options}
