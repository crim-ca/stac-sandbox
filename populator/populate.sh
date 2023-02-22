#!/bin/sh
set -ex

# requires pip installs done
# requires running STAC server

# reset the STAC API data by using `docker-compose down -v; docker-compose up -d --force-recreate`

eval "$(conda shell.bash hook)"
conda activate ceda-workflow-3.9-1

# create collections
python3 collection_processor.py collections.yaml

cd ~/projects/stac-generator-example

# add items
python3 -m stac_generator.scripts.stac_generator conf/thredds-cmip6-asset-generator.yaml        # CMIP6
python3 -m stac_generator.scripts.stac_generator conf/thredds-cmip5-asset-generator.yaml        # CMIP5

cd ~/projects/stac-sandbox/populator

# update collection summaries
python3 collection_processor.py collections.yaml
