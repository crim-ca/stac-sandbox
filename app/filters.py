# encoding: utf-8
"""

"""
__author__ = 'Mathieu Provencher'
__date__ = '21 Apr 2022'
__copyright__ = 'Copyright 2022 Computer Research Institute of Montréal'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'mathieu.provencher@crim.ca'

import asyncio
import threading
from stac_fastapi.types.core import BaseFiltersClient
from .utils import dict_merge

from stac_fastapi.pgstac.core import CoreCrudClient

import attr

from typing import Dict, Any, Optional


class AsyncioEventThreadsafe(asyncio.Event):
    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


@attr.s
class FiltersClient(BaseFiltersClient):

    def collection_summaries(self, collection_id: str, **kwargs) -> Dict:

        properties = {}

        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=start_loop, args=(new_loop,))
        t.start()

        collection = asyncio.run_coroutine_threadsafe(CoreCrudClient.get_collection(self, "c604ffb6d610adbb9a6b4787db7b8fd7", **kwargs), new_loop)

        collection = collection.result(3)

        # try:
        # collection = ElasticsearchCollection.get(id=collection_id)
        # except NotFoundError:
            # raise (NotFoundError(404, f'Collection: {collection_id} not found'))

        if summaries := collection.get_summaries():
            for k, v in summaries.items():
                prop = {
                    k: {
                        'title': k.replace('_', ' ').title(),
                        'type': 'string',
                        'enum': v
                    }
                }
                properties.update(prop)

        if extent := collection.get_extent():
            temp_min, temp_max = extent['temporal']['interval'][0]
            prop = {
                'datetime': {
                    'type': 'datetime',
                    'minimum': temp_min,
                    'maximum': temp_max
                },
                'bbox': {
                    'description': 'bounding box for the collection',
                    'type': 'array',
                    'minItems': 4,
                    'maxItems': 6,
                    'items': {
                        'type': 'number'
                    }
                }
            }

            properties.update(prop)

        return properties

    def get_queryables(
            self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:

        schema = super().get_queryables()

        if collection_id:

            properties = self.collection_summaries(collection_id, **kwargs)

            schema['$id'] = f'{kwargs["request"].base_url}/{collection_id}/queryables'
            schema['title'] = f'Queryables for {collection_id}'
            schema['description'] = f'Queryable names and values for the {collection_id} collection'
            schema['properties'] = properties

        else:
            query_params = kwargs['request'].query_params
            collections = query_params.get('collections', [])
            if collections:
                collections = collections.split(',')

            properties = {}

            for collection in collections:
                if not properties:
                    # Initialise with first collection
                    properties = self.collection_summaries(collection)
                else:
                    # Get properties of following collections
                    new_props = self.collection_summaries(collection)
                    intersect = {}
                    for prop, value in properties.items():
                        if prop in new_props:
                            if value.get('type') == 'string':
                                intersect[prop] = dict_merge(value, new_props[prop])
                    properties = intersect

                    # If the resultant intersect is an empty dict, short-circuit
                    # loop.
                    if not properties:
                        break

            schema['$id'] = f'{kwargs["request"].base_url}/queryables'
            schema['title'] = f'Global queryables, reduced by collection context'
            schema['description'] = f'Queryable names and values'
            schema['properties'] = properties

        return schema
