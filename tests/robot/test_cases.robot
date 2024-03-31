*** Settings ***

Resource   resources/app_keywords.robot

*** Variables ***

${app_url}                   http://localhost:8501

*** Test Cases ***

Interact with st_keyup
    Open browser                       ${app_url}    Chrome
    Input text into st_keyup           adjunta
    Wait until page contains           URB San Joaquin
    Wait until page contains           Jard De Adjuntas
    Wait until page contains           Colinas Del Gigante
