# streamlit-keyup

If you're collecting text input from your users in your streamlit app, `st.text_input` works well -- as long as you're happy with
waiting to get the response when they're finished typing.

But, what if you want to get the input out, and do something with it every time they type a new key (AKA "on keyup")?

## Installation

`pip install streamlit-keyup`

## Usage

```python
from st_keyup import st_keyup

value = st_keyup("Enter a value")

# Notice that value updates with every keyup
st.write(value)
```
