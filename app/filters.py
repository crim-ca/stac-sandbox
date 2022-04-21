# encoding: utf-8
"""

"""
__author__ = 'Mathieu Provencher'
__date__ = '21 Apr 2022'
__copyright__ = 'Copyright 2022 Computer Research Institute of Montréal'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'mathieu.provencher@crim.ca'

# from .database import PostgresCollection

import asyncio
import threading
import time
from urllib import request
from stac_fastapi.types.core import BaseFiltersClient
from .utils import dict_merge

from stac_fastapi.pgstac.core import CoreCrudClient

from stac_fastapi.api.models import EmptyRequest

from fastapi import FastAPI, Request

import attr

from typing import Dict, Any, Optional

import concurrent.futures

from starlette.requests import Request


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
    ev_loop = asyncio.new_event_loop()

    def __init__(self, name="Asyncio"):
        self.ev_loop = asyncio.new_event_loop()

        asyncio.get_child_watcher().attach_loop(self.ev_loop)

        self.ev_loop.set_debug(enabled=True)

        self.logger.debug("created asyncio loop: {}:{}".format(id(self.ev_loop), self.ev_loop))
        self.ev_loop_done = AsyncioEventThreadsafe(loop=self.ev_loop)
        self.ev_loop_done.clear()
        self.ev_loop_started = threading.Event()

    def run_async_coroutine(self, coroutine_to_run, timeout):
        """Start coroutine in dedicated thread and await its result with timeout"""
        start_time = time.time()
        coro_future = self.start_async_coroutine(coroutine_to_run)
        # run_coroutine_threadsafe returns future as concurrent.futures.Future() and not asyncio.Future
        # so, we can await it with timeout inside current thread
        try:
            coro_result = coro_future.result(timeout=timeout)
            # self.logger.debug("scheduled {} returned {}".format(coroutine_to_run, coro_result))
            return coro_result
        except concurrent.futures.TimeoutError:
            passed = time.time() - start_time
            # raise MolerTimeout(timeout=timeout,
            #                    kind="run_async_coroutine({})".format(coroutine_to_run),
            #                    passed_time=passed)
        except concurrent.futures.CancelledError:
            raise

    def start_async_coroutine(self, coroutine_to_run):
            """Start coroutine in dedicated thread, don't await its result"""
            # we are scheduling to other thread (so, can't use asyncio.ensure_future() )
            # self.logger.debug("scheduling {} into {}".format(coroutine_to_run, self.ev_loop))
            coro_future = asyncio.run_coroutine_threadsafe(coroutine_to_run, loop=self.ev_loop)
            return coro_future



    def collection_summaries(self, collection_id: str, **kwargs) -> Dict:

        properties = {}

        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=start_loop, args=(new_loop,))
        t.start()

        # loop = asyncio.get_running_loop()
        # start_loop(loop)

        # collection = self.run_async_coroutine(CoreCrudClient.get_collection(self, "sss", **kwargs), 3)
        collection = asyncio.run_coroutine_threadsafe(CoreCrudClient.get_collection(self, "sss", **kwargs), new_loop)

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
