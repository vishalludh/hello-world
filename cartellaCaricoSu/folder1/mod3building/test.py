import aiohttp
import argparse
import asyncio
import os
from pprint import pprint

from medifor.ApplicationClient import ApplicationClient
from medifor.resources import Resource


async def main(loop):
    parser = argparse.ArgumentParser()
    parser.add_argument('base_address', help='base address of algorithm service')
    args = parser.parse_args()

    with aiohttp.ClientSession(loop=loop) as session:
        client = ApplicationClient(args.base_address, session)

        filenames = ['GoodCropped.jpg']

        paths = [os.path.join('MOD3/TestImgs', filename) for filename in filenames]
        tasks = [client.process_run({'image': Resource.from_file('image', path) }, delete=False) for path in paths]
        runs = await asyncio.gather(*tasks, loop=loop)
        for run in runs:
            pprint(run)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
