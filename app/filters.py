# encoding: utf-8
"""

"""
__author__ = 'Mathieu Provencher'
__date__ = '21 Apr 2022'
__copyright__ = 'Copyright 2022 Computer Research Institute of Montréal'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'mathieu.provencher@crim.ca'

from stac_fastapi.types.core import AsyncBaseFiltersClient
from utils import dict_merge

from stac_fastapi.pgstac.core import CoreCrudClient

import attr

from typing import Dict, Any, Optional


@attr.s
class FiltersClient(AsyncBaseFiltersClient):

    async def collection_summaries(self, collection_id: str, **kwargs) -> Dict:
        properties = {}
        core_crud_client = CoreCrudClient()
        item_collection = await core_crud_client.item_collection(collection_id, 9999, **kwargs)

        for feat in item_collection["features"]:
            for property in feat["properties"]:
                if property == "datetime":
                    continue

                if property not in properties:
                    properties[property] = []

                if feat["properties"][property] not in properties[property]:
                    properties[property].append(feat["properties"][property])

        return properties

    async def get_queryables(
            self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:

        schema = await super().get_queryables()

        if collection_id:

            properties = await self.collection_summaries(collection_id, **kwargs)

            schema['$id'] = f'{kwargs["request"].base_url}/{collection_id}/queryables'
            schema['title'] = f'Queryables for {collection_id}'
            schema['description'] = f'Queryable names and values for the {collection_id} collection'
            schema['properties'] = properties

        # else:
        #     query_params = kwargs['request'].query_params
        #     collections = query_params.get('collections', [])
        #     if collections:
        #         collections = collections.split(',')
        #
        #     properties = {}
        #
        #     for collection in collections:
        #         if not properties:
        #             # Initialise with first collection
        #             properties = self.collection_summaries(collection)
        #         else:
        #             # Get properties of following collections
        #             new_props = self.collection_summaries(collection)
        #             intersect = {}
        #             for prop, value in properties.items():
        #                 if prop in new_props:
        #                     if value.get('type') == 'string':
        #                         intersect[prop] = dict_merge(value, new_props[prop])
        #             properties = intersect
        #
        #             # If the resultant intersect is an empty dict, short-circuit
        #             # loop.
        #             if not properties:
        #                 break
        #
        #     schema['$id'] = f'{kwargs["request"].base_url}/queryables'
        #     schema['title'] = f'Global queryables, reduced by collection context'
        #     schema['description'] = f'Queryable names and values'
        #     schema['properties'] = properties

        return schema
