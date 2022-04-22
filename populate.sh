#!/bin/sh
set -ex

# requires pip installs done
# requires running STAC server

cd ../asset-scanner-example
eval "$(conda shell.bash hook)"
conda activate ceda-workflow-3.9-1

# create collections
python3 scripts/collection_processor.py scripts/collections.yaml

# add items
python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-assets.yaml        # CMIP5
python3 -m asset_scanner.scripts.asset_scanner conf/thredds-extract-assets-2.yaml      # CMIP6

# update collection summaries
python3 scripts/collection_processor.py scripts/collections.yaml
