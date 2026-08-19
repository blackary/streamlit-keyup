*** Settings ***

Resource           resources/app_keywords.robot
Library            Process
Suite Setup        Do Suite Setup
Suite Teardown     Do Suite Teardown

*** Variables ***

${app_url}         http://localhost:8501

*** Test Cases ***

1. Basic value round-trips to Python
    Wait Until Keyword Succeeds        30s    1s    Open URL    ${app_url}
    Wait For Component                 0
    Type Into Component                0    hello basic
    Wait Until Page Contains           'hello basic'    timeout=15s

2. Default value is pre-filled
    Nth Component Value Should Be      1    preset text
    Wait Until Page Contains           'preset text'    timeout=15s

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
    [Documentation]    The value must NOT reach Python before the debounce
    ...                elapses, then must arrive once it does.
    Type Into Component                9    debounced text
    Sleep                              0.2s
    Page Should Not Contain            'debounced text'
    Wait Until Page Contains           'debounced text'    timeout=15s

9. on_change callback fires
    Type Into Component                10    cb test
    Wait Until Page Contains           'cb test'    timeout=15s
    Page Should Not Contain            change_count: 0

10. on_change forwards args and kwargs
    Type Into Component                11    args test
    Wait Until Page Contains           'args test'    timeout=15s
    Page Should Contain                'first'
    Page Should Contain                'second'
    Page Should Contain                'kw'

11. on_submit fires when Enter is pressed
    Type Into Component                12    submit me
    Wait Until Page Contains           'submit me'    timeout=15s
    Press Enter In Component           12
    Wait Until Page Does Not Contain   submit_count: 0    timeout=15s

12. Reset by changing the key clears the field
    [Documentation]    Rendering the widget under a new key produces a fresh,
    ...                empty input — the supported way to reset from Python.
    Type Into Component                13    will be reset
    Wait Until Page Contains           'will be reset'    timeout=15s
    Click Element                      xpath=//button[normalize-space()='Reset the field above']
    Wait Until Keyword Succeeds        15s    0.5s
    ...    Nth Component Value Should Be      13    ${EMPTY}

13. session_state holds a plain str, not a dict
    [Documentation]    st.session_state[key] must be a raw string so callers can
    ...                read and assign it without a nested "value" lookup.
    Wait Until Page Contains           Type: str    timeout=15s
    Page Should Not Contain            _WriteThrough

14. Unkeyed component round-trips to Python
    [Documentation]    A component with key=None must still send its value to
    ...                Python and must not raise.
    Type Into Component                14    no key here
    Wait Until Page Contains           'no key here'    timeout=15s
    Nth Component Value Should Be      14    no key here
    Page Should Not Contain            Traceback

15. Unrelated rerun does not stomp typed input
    [Documentation]    Typing then triggering an unrelated rerun must NOT
    ...                clear or reset the user's input.
    Type Into Component                15    must survive
    Wait Until Page Contains           'must survive'    timeout=15s
    Click Element                      xpath=//button[normalize-space()='Unrelated rerun']
    Wait Until Page Contains           unrelated: 1    timeout=15s
    Nth Component Value Should Be      15    must survive

16. Enter key without on_submit raises no exception
    [Documentation]    Pressing Enter in a component with no on_submit
    ...                must not raise a StreamlitAPIException.
    Type Into Component                16    enter safe
    Wait Until Page Contains           'enter safe'    timeout=15s
    Press Enter In Component           16
    Sleep                              1s
    Page Should Not Contain            StreamlitAPIException
    Page Should Not Contain            Traceback
