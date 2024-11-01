# What it does

This script opens a headless chrome to visit https://trialsearch.who.int/AdvSearch.aspx and run a search for clinical trials for a specified condition.

The results are downloaded as an XML file and uploaded to an install of [Gregory-AI](https://github.com/brunoamaral/gregory-ai).

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

