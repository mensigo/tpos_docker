#/bin/bash

delay=15
status=$(docker inspect --format {{.State}} $1)

while [ ! "$status" = "exited" ]
do
  sleep $delay
  status=$(docker inspect --format {{.State}} $1)
done

python app.py
