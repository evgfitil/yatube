# yatube

***Yatube*** is a blog platform based on the Django Web Framework.

Yatube users can post their articles, attach images to them, read articles of other authors, exchange comments and follow to favourite authors.

Demo site https://yatube.ea4ws.tk available with all authentication methods, including email auth and anonymous access

### Developing and testing locally (Quick Start)

#### With Docker

  1. Clone this repository
  2. Copy or rename `.env.docker-example` file to `.env` and `.env.db-example` to `.env.db`. Customize it for your needs
  3. Use provided `Dockerfile` and `docker-compose.yml`, build the images and run the containers
  ```
  docker-compose up -d --build
  ```
  If everything went well, you now have a server running on http://localhost:1337 and four running containers:
    
    yt-web - container with Django app
    yt-nginx - Nginx reverse proxy for Gunicorn
    yt-db - Postgres database
    yt-cache - Redis cache
  
  To apply migrations and create Django admin user run:
  ```
  docker exec -ti yt-web ./first-run.sh
  ```
  To remove builder image run `docker image prune --filter label=stage=builder`
  You can also run tests to make sure everything is ok, for that run:
  ```
  docker exec -ti yt-web pytest
  ```
  To confirm the reset of the user password use `sent_emails` folder on `yt-web` container `workdir` and then look into ``*.log`` files
  
