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
   
