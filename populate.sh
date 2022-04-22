#!/bin/sh
set -ex

# requires pip installs done
# requires running STAC server

# reset the STAC API data by using `docker-compose down -v; docker-compose up -d --force-recreate`

cd ../asset-scanner-example
eval "$(conda shell.bash hook)"
conda activate ceda-workflow-3.9-1

# create collections
python3 scripts/collection_processor.py scripts/collections.yaml

# add items
python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-assets-2.yaml        # CMIP6
python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-assets.yaml          # CMIP5

# update collection summaries
python3 scripts/collection_processor.py scripts/collections.yaml
