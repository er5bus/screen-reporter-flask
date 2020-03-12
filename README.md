# Screen Reporter API
Back end of Report visual bugs directly into your existing issue tracking tool like Trello.

# Requirements
docker;

# Installation

# Set Environment Variables

``` env
# Docker env varibles
FLASK_RUN_MIGRATION=1

# Mail configurations
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=on
MAIL_USERNAME=email
MAIL_PASSWORD=password
FLASK_MAIL_SENDER=team@latech.io

# Trello configurations
TRELLO_APP_KEY=trello key

# App configurations
#development, testing, production
FLASK_ENV=production 
FLASK_DEBUG=1
SECRET_KEY=some key
#DEV_DATABASE_URL=sqlite:///data/data-dev.sqlite
#TEST_DATABASE_URL=sqlite:///data/data-test.sqlite
#DATABASE_URL=sqlite:///data/data-prod.sqlite

# JWT configurations 
JWT_SECRET_KEY=some key
JWT_PUBLIC_KEY=jwt-key.pub
JWT_PRIVATE_KEY=jwt-key

```

## Usage 
Run this command to run the built-in web server and access the application in your browser at http://0.0.0.0:5000:

``` bash
$ docker-compose up -d
```
