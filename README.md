# Usage

## 1. Create a .env file

```
REMOTE_USER=username #ssh user
REMOTE_HOST=Host #ssh host
REMOTE_DIRECTORY=/PATH-WHERE-GREGORY-AI-IS-INSTALLED/django/
```
## 2. Install requirements

`pip install -r requirements.txt`

## 3. Run command

Get the ID you need to use from [Gregory-AI](https://github.com/brunoamaral/gregory-ai)'s backoffice

`python download-cts.py --source-id 17 --condition "Multiple Sclerosis"`

