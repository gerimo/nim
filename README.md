## Getting Started
Fetch the git project and build it. This may take long.
```bash
# To create the external database module locally
docker volume create --name=mongo-data
# To run the main container in foreground
docker-compose up web mongo
# To connecto to a running instance
docker ps
docker exec -it neem_CONTAINER_NAME_1 bash
# To run a disposable container
docker-compose run --rm CONTAINER_NAME /bin/bash

* Add all views that are already created.
=======
# nim

