*** Settings ***

Resource           resources/app_keywords.robot
Library            Process
Suite Setup        Do Suite Setup
Suite Teardown     Do Suite Teardown

*** Variables ***

${app_url}         http://localhost:8501

*** Test Cases ***

1. Basic value round-trips to Python
    Sleep                              2s
    Open URL                           ${app_url}
    Wait For Component                 0
    Type Into Component                0    hello basic
    Wait Until Page Contains           'hello basic'

2. Default value is pre-filled
    Nth Component Value Should Be      1    preset text

3. Password type is applied
    Nth Component Attr Should Be       2    type    password

4. max_chars is enforced
    Nth Component Attr Should Be       3    maxLength    5

5. Placeholder is set
    Nth Component Attr Should Be       4    placeholder    type here...

6. Disabled input cannot be edited
    Nth Component Attr Should Be       5    disabled    true

7a. label_visibility=visible shows label
    Label Visibility Should Be         6    visible

7b. label_visibility=hidden hides label but keeps space
    Label Visibility Should Be         7    hidden

7c. label_visibility=collapsed removes label space
    Label Visibility Should Be         8    collapsed

8. Debounce delays the Python update
    Type Into Component                9    debounced text
    Sleep                              0.2s
    Page Should Not Contain            'debounced text'
    Sleep                              2s
    Wait Until Page Contains           'debounced text'

9. on_change callback fires
    Type Into Component                10    cb test
    Sleep                              2s
    Page Should Not Contain            change_count: 0

10. on_change forwards args and kwargs
    Type Into Component                11    args test
    Sleep                              2s
    Page Should Contain                'first'
    Page Should Contain                'second'
    Page Should Contain                'kw'

11. on_submit fires when Enter is pressed
    Type Into Component                12    submit me
    Sleep                              1.5s
    Press Enter In Component           12
    Sleep                              2s
    Page Should Not Contain            submit_count: 0

12. Programmatic clear via session_state works
    Type Into Component                13    will be cleared
    Sleep                              2s
    Click Button                       css:[data-testid='stButton'] button
    Sleep                              3s
    Nth Component Value Should Be      13    ${EMPTY}

15. B1 Regression - Unrelated rerun does not stomp typed input
    [Documentation]    Typing then triggering an unrelated rerun must NOT
    ...                clear or reset the user's input.
    Type Into Component                15    must survive
    Sleep                              2s
    Click Button                       css:[data-testid='stBaseButton-secondary']
    Sleep                              2.5s
    Nth Component Value Should Be      15    must survive

16. B2 Regression - Enter without on_submit raises no exception
    [Documentation]    Pressing Enter in a component with no on_submit
    ...                must not raise a StreamlitAPIException.
    Type Into Component                16    enter safe
    Sleep                              1.5s
    Press Enter In Component           16
    Sleep                              2s
    Page Should Not Contain            StreamlitAPIException
    Page Should Not Contain            Traceback
