# Docker compose instructions

Application has been isolated into frontend, backend, database
Each component has its own Dockerfile

# Running docker

To start the application just do -
docker compose up

# Quitting docker

To remove all containers and quit the application just do -
docker compose down

# NOTE

if you made changes to any file we need to build the component before we do a docker compose up
so do

## if u change backend

docker compose build backend

## if u change frontend

docker compose build frontend

then u can compose up and compose down
