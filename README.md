# Cold-war-boardgame

This is pet project:

- learning curve for project-manager
- learn rest-api by game development
- learn reinforcement learning pipline for p-to-p board game

## Project resources

- [API stage](https://cold-war-api-stage.herokuapp.com/)
- [API prod](https://cold-war-api.herokuapp.com/)
- [WEB app stage](https://cold-war-api.herokuapp.com/)
- [WEB app prod](https://cold-war-web.herokuapp.com/)
- [docs](https://drive.google.com/drive/folders/1MoP2Ba2yzKSFf3X8XwieKKc8cv_cEhCU?usp=sharing)
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
```

### Run or stop stack from root

- `make serve` to run
- `make down` to stop

### Use local resources to watch project

- [frontend](http://localhost:8501/)
- [backend swagger docs](http://localhost:8000/docs/)
- [backend redoc](http://localhost:8000/redoc/)
- [mongoDB admin panel](http://localhost:8081/)

## More

Problem with heroku-22 stack and poetry buildpack
