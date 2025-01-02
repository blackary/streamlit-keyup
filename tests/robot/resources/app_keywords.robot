*** Settings ***

Library             SeleniumLibrary

*** Variables ***

${st_keyup_iframe_locator}   css:iframe[title="st_keyup.st_keyup"]

*** Keywords ***

Input text into st_keyup
    [Arguments]                         ${text}
    Wait until element is visible       ${st_keyup_iframe_locator}
    Select frame                        ${st_keyup_iframe_locator}
    Input text                          css:input[type="text"]      ${text}
    Unselect frame
