#!/bin/sh
set -ex

# requires pip installs done
# requires running STAC server

# reset the STAC API data by using `docker-compose down -v; docker-compose up -d --force-recreate`

ASSET_GENERATOR_TIMEOUT=20

eval "$(conda shell.bash hook)"
conda activate ceda-workflow-3.9-1

# create collections
python3 collection_processor.py collections.yaml

cd ~/projects/stac-generator-example

# add items
timeout -s HUP $ASSET_GENERATOR_TIMEOUT bash -c "python3 -m stac_generator.scripts.stac_generator conf/thredds-cmip6-asset-generator.yaml" &
PID_CMIP6=$!
timeout -s HUP $ASSET_GENERATOR_TIMEOUT bash -c "python3 -m stac_generator.scripts.stac_generator conf/thredds-cmip5-asset-generator.yaml" &
PID_CMIP5=$!

# here we kill the asset generators if CTRL-C is sent
trap "kill -2 ${PID_CMIP6} ${PID_CMIP5} 2> /dev/null; exit 1" INT

echo "Running STAC asset generator for $ASSET_GENERATOR_TIMEOUT seconds..."
wait $PID_CMIP6
wait $PID_CMIP5

cd ~/projects/stac-sandbox/populator

# update collection summaries
python3 collection_processor.py collections.yaml
