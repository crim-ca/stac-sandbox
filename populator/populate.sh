#!/bin/sh
set -ex

# requires pip installs done
# requires running STAC server

# reset the STAC API data by using `docker-compose down -v; docker-compose up -d --force-recreate`

eval "$(conda shell.bash hook)"
conda activate ceda-workflow-3.9-1

# create collections
# python3 collection_processor.py collections.yaml

cd ../asset-scanner-example

# add items
python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-cmip6-assets.yaml        # CMIP6
# python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-cmip5-assets.yaml          # CMIP5

cd ../stac-sandbox/scripts

# update collection summaries
python3 collection_processor.py collections.yaml
