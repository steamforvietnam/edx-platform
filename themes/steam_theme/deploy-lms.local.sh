#!/bin/bash

CONTAINER_NAME="tutor_local_lms_1"
THEME_NAME="steam_theme"

echo && echo "Copying local repository to running container..."
docker cp ./ "${CONTAINER_NAME}:/openedx/themes/${THEME_NAME}"
docker cp ./scripts/lms/assets.py "${CONTAINER_NAME}:/openedx/edx-platform/lms/envs/tutor/"

echo && echo "Processing theme..."
docker exec -it $CONTAINER_NAME bash -c "cd /openedx/edx-platform"
docker exec -it $CONTAINER_NAME openedx-assets themes --systems lms

echo && echo "Collecting assets..."
docker exec -it $CONTAINER_NAME openedx-assets collect --systems lms --settings=tutor.assets

echo && echo "Activating theme..."
tutor local settheme $THEME_NAME $(tutor config printvalue LMS_HOST)

echo && echo "Restarting docker containers..."
tutor local start -d