import asyncio
import json
import aiohttp
from urllib.parse import urlencode

import logging
logging.basicConfig(level=logging.DEBUG)

class DispatchService:

    def __init__(self):
        pass

    def get_logs(self, app, file, servers, auth, search=None, limit=None):
        loop = asyncio.new_event_loop()

        def make_url(server):
            params = {}
            if search is not None:
                params['search'] = ','.join(search)
            if limit is not None:
                params['limit'] = limit

            url = f"http://{server}/v1/logs/{file}?{urlencode(params)}"
            return url

        urls = map(make_url, servers)

        results = asyncio.run(self.async_get_logs(app.logger, urls, auth))

        # start our generators, skipping any that didnt return successfully
        # TODO: error handling/explode as needed. As is any failed request will
        # be silent
        results = [x() for x in results if x is not None]

        i = 0
        done = False
        while not done:
            # roundrobin through all results until either
            # a) the result is drained or
            # b) we've hit our limit
            exhausted = []
            for result in results:
                try:
                    line = loop.run_until_complete(anext(result))
                    log = json.loads(line)
                    yield log
                    i += 1
                    if limit is not None and i >= limit:
                        done = True
                        break
                except StopAsyncIteration:
                    # we've exhausted the stream - this one is done
                    exhausted.append(result)

            # remove any finished streams from the result list
            res = [result for result in results if result not in exhausted]
            if len(res) == 0:
                done = True

    async def get_log(self, logger, url, auth):
        async def read_stream():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url=url,
                        headers={
                            "Authorization": auth,
                            "Accept": "application/stream+json"
                            }) as response:
                        async for line_bytes in response.content:
                            line = line_bytes.decode("UTF-8")
                            yield line
            except Exception as e:
                logger.error(f"Unable to load url {url}: {str(e)}")
        return read_stream

    async def async_get_logs(self, logger, urls, auth):

        ret = await asyncio.gather(*[self.get_log(
            logger, url, auth) for url in urls
        ])
        return ret
