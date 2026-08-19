*** Settings ***

Library             SeleniumLibrary

*** Variables ***

${additional_chrome_options}            ""

*** Keywords ***

Do Suite Setup
    ${process} =   Start Process
    ...    uv    run    streamlit         run   tests/test_app.py
    ...        --server.port                     8501
    ...        --server.headless                 true
    ...        --browser.gatherUsageStats        false
    Log                                PID: ${process.pid}
    VAR        ${PROCESS}    ${process}   scope=SUITE

Do Suite Teardown
    Log                                 PID: ${PROCESS.pid}
    ${result} =   Terminate Process     ${PROCESS}
    Log                                 Terminate process result: ${result}

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

Wait For Component
    [Arguments]                         ${n}
    Wait Until Element Is Visible       css:[data-testid='stBidiComponentIsolated']    timeout=30s

Type Into Component
    [Documentation]    Set input value and fire an input event in the Nth
    ...                shadow-DOM component (0-indexed).
    [Arguments]                         ${n}    ${text}
    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    var inp = h.shadowRoot.querySelector('#input');
    ...    inp.value = "${text}";
    ...    inp.dispatchEvent(new Event('input', {bubbles: true, composed: true}));

Press Enter In Component
    [Documentation]    Fire a keydown Enter event in the Nth shadow-DOM component.
    [Arguments]                         ${n}
    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    var inp = h.shadowRoot.querySelector('#input');
    ...    inp.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, composed: true}));

Nth Component Value Should Be
    [Documentation]    Assert the input value in the Nth shadow-DOM component.
    [Arguments]                         ${n}    ${expected}
    ${actual}=    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    return h.shadowRoot.querySelector('#input').value;
    Should Be Equal    ${actual}    ${expected}

Nth Component Attr Should Be
    [Documentation]    Assert a DOM attribute/property of the Nth component's input.
    [Arguments]                         ${n}    ${attr}    ${expected}
    ${actual}=    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    var inp = h.shadowRoot.querySelector('#input');
    ...    return String(inp['${attr}'] !== undefined ? inp['${attr}'] : inp.getAttribute('${attr}'));
    Should Be Equal    ${actual}    ${expected}

Label Visibility Should Be
    [Documentation]    Check that the label in the Nth component has the correct
    ...                visibility state: "visible", "hidden" (visibility:hidden),
    ...                or "collapsed" (display:none).
    [Arguments]                         ${n}    ${state}
    ${display}=    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    var lbl = h.shadowRoot.querySelector('#label');
    ...    return getComputedStyle(lbl).display;
    ${visibility}=    Execute Javascript
    ...    var h = document.querySelectorAll("[data-testid='stBidiComponentIsolated']")[${n}];
    ...    var lbl = h.shadowRoot.querySelector('#label');
    ...    return getComputedStyle(lbl).visibility;
    IF    '${state}' == 'visible'
        Should Not Be Equal    ${display}    none
        Should Not Be Equal    ${visibility}    hidden
    ELSE IF    '${state}' == 'hidden'
        Should Not Be Equal    ${display}    none
        Should Be Equal        ${visibility}    hidden
    ELSE IF    '${state}' == 'collapsed'
        Should Be Equal        ${display}    none
    END
