*** Settings ***

Resource           resources/app_keywords.robot
Library            Process
Suite Setup        Do Suite Setup
Suite Teardown     Do Suite Teardown

*** Variables ***

${app_url}         http://localhost:8501

*** Test Cases ***

Interact with st_keyup
    Sleep                              2s
    Open URL                           ${app_url}
    Input text into st_keyup           adjunta
    Wait until page contains           URB San Joaquin
    Wait until page contains           Jard De Adjuntas
    Wait until page contains           Colinas Del Gigante
