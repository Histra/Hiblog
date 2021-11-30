# Hiblog

Version:`0.1`

Author : `Histranger`

Email : `1497058369@qq.com`

## Answer API

### Version 1.0

#### Get Answer API list
~~~
Method: GET
URL: http://{ip_or_domain}/answer/api/v1/oauth
~~~

#### Get Answer Token
~~~
Method: POST
URL: http://{ip_or_domain}/answer/api/v1/oauth/token
~~~

Examples:  
You can get oauth token by `python3` using `requests`, your code maybe:
```python
import requests
def get_token():
    payload = {'username': '{your_username}', 'password': '{your_password}', 'grant_type': 'password'}
    res = requests.post('http://{ip_or_domain}/answer/api/v1/oauth/token', data=payload)
    print(res.json())
get_token()
```
+ By the way, you need specify the `your_username` and `your_password`, and `{ip_or_domain}`.  

Then, you get the response which should be similar to the following:  
```python
{'access_token': '{personal_token}', 'expires_in': 3600, 'token_type': 'Bearer'}
```
+ `access_token`: the personal_token that prove that you are you.
+ `expires_in`: the survival time of the access_token.
+ `token_type`: must be 'Bearer'.

### Get Answer item

~~~
Need: access_token
Method: GET
URL: http://{ip_or_domain}/answer/api/v1/oauth/answer_item/{answer_id}
~~~
+ You must have an access_token, otherwise you may get a error status_code json.
+ you should specify the `answer_id`.

Example:
```python
import requests
import json
def get_answer_item():
    headers = {
        "Authorization": "Bearer {access_token}"}
    res = requests.get('http://{ip_or_domain}/answer/api/v1/oauth/answer_item/{answer_id}',
                       headers=headers)

    print(json.dumps(res.json(), ensure_ascii=False))
get_answer_item()
```


### GET answer items
If you want to get lots of answer items at one time, the following API is what you need.

~~~
Need: access_token
Method: GET
URL: http://{ip_or_domain}/answer/api/v1/oauth/answer_items{?page}
~~~
+ You must have an access_token, otherwise you may get a error status_code json.
+ you should specify the `page`.

Example:
```python
import requests
import json
def get_answer_items():
    headers = {
        "Authorization": "Bearer {access_token}"}
    res = requests.get('http://{ip_or_domain}/answer/api/v1/oauth/answer_items?page={page}',
                       headers=headers)
    print(json.dumps(res.json(), ensure_ascii=False))
```

