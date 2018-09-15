# indiana-phone
Flask-API for ofono

| Method     | Endpoint                     |
| ---------- |------------------------------|
| GET        | /devices                     |
| POST       | /\<device>/dial/\<number>    |
| GET        | /\<device>/calls             |
| POST       | /\<device>/hangup            |
| POST/GET   | /\<device>/answer            |



# Installation
Raspbian requirements (may be incomplete):

```bash
$ sudo apt-get install libgirepository1.0-dev libcairo2-dev
````

Clone the repo:
```
git clone https://github.com/ejojmjn/indiana-phone.git
cd indiana-phone
```

Create a virtual environment and activate it
```
$ python3 -m venv env
$ source env/bin/activate
```

Install Python requirements:
```
$ pip install -r requirements.txt
```

Run the app:
```
$ python3 app.py
```

Example:
```
(env) $ python3 app.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
$ 
```
