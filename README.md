# Cold-war-boardgame

This is pet project:

- learning curve for project-manager
- learn rest-api by game development
- learn reinforcement learning pipline for p-to-p board game

## Project resources

- [API](https://coldwar-api.onrender.com/docs)
- [WEB](https://coldwar-web.onrender.com/)
- [project materials](https://drive.google.com/drive/folders/1MoP2Ba2yzKSFf3X8XwieKKc8cv_cEhCU?usp=sharing)
- [project tasks board](https://github.com/users/KonstantinKlepikov/projects/4/views/5)

Other stuff:

- [bordgame geek source](https://boardgamegeek.com/boardgame/24742/cold-war-cia-vs-kgb)

## Run project local

### Add .env file to root with some variables

```sh
DEV_ROOT_USERNAME=<this>
DEV_ROOT_PASSWORD=<this>
TEST_ROOT_USERNAME=<this>
TEST_ROOT_PASSWORD=<this>
ADMINUSERNAME=<this>
ADMINPASSWORD=<this>

# dev mongodb
MONGODB_URL=mongodb://${DEV_ROOT_USERNAME}:${DEV_ROOT_PASSWORD}@mongo-dev:27017/
DB_NAME=dev-db

# test_mongodb
TEST_MONGODB_URL=mongodb://${DEV_ROOT_USERNAME}:${DEV_ROOT_PASSWORD}@mongo-test:27021/

# JWT secret key
SECRET_KEY=<this>

# Test vars
<some>
```

### Run or stop stack from root

- `make serve` to run
- `make down` to stop

### Use local resources to watch project

- [frontend](http://localhost:8501/)
- [backend swagger docs](http://localhost:8000/docs/)
- [backend redoc](http://localhost:8000/redoc/)
- [mongoDB admin panel](http://localhost:8081/)

### Test inside backend container

`pytest -v -s -x`

use `python -m IPython` to check code
