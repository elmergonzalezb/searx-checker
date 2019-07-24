from urllib.parse import urlencode, urlparse
from sys import exit, stdout, stderr
from json import dumps
import collections
import argparse
import requests
import calendar
import datetime


EngineResult = collections.namedtuple('EngineResult', ['status', 'error'])

CONFIG_API_ENDPOINT = '/config'

QUERY_STRINGS = {
    '*': ['time', 'test', 'savant', 'bbc.com' ],
    'currency': [ '10 usd in eur' ],
    'translate' : [ 'en-ru apple' ],
    'map' : [ 'paris' ],
    'calc' : [ '1/x' ]
    }

ENGINE_QUERY = {
    'dictzone': 'translate',
    'mymemory translated': 'translate',
    'currency': 'currency',
    'photon' : 'map',
    'openstreetmap': 'map',
    'wolframalpha': 'calc'
}


def _is_url(url):
    try:
        result = urlparse(url)
        return True
    except Exception as e:
        return False


def _is_url_image(image_url):
    if image_url.startswith('//'):
        image_url='https:' + image_url

    if image_url.startswith('data:'):
        return image_url.startswith('data:image/')

    if not _is_url(image_url):
        return False

    try:
        r = requests.head(image_url, allow_redirects=True)
        if r.headers["content-type"].startswith('image/'):
            return True
        return False
    except Exception as e:
        # some server doesn't support HEAD
        try:
            r = requests.get(image_url, allow_redirects=True)
            if r.headers["content-type"].startswith('image/'):
                return True
            return False
        except Exception as e2:
            return False


def _check_result(result):
    template=result.get('template', 'default.html')
    if template == 'default.html':
        return True
    if template == 'code.html':
        return True
    if template == 'torrent.html':
        return True
    if template == 'map.html':
        return True
    if template == 'images.html':
        return _is_url_image(result.get('thumbnail_src'))
    if template == 'videos.html':
        return _is_url_image(result.get('thumbnail'))
    return True


def _check_results(results):
    for result in results:
        if not _check_result(result):
            return EngineResult(False, "Engine returns an unavailable thumbnail URL")
    return EngineResult(True, None)


def get_config(url):
    resp = requests.get(url + CONFIG_API_ENDPOINT)
    if resp.status_code != 200:
        print('Error get ', CONFIG_API_ENDPOINT, ', status code=',resp.status_code)
        exit(2)
    return resp.json()


def get_engines(config):
    if 'engines' in config:
        return config['engines']
    print('Error while getting the engines', file=stderr)
    exit(2)


def get_version(config):
    if 'version' in config:
        return config['version']
    return None


def _construct_url(instance_url, query_string, shortcut):
    query = urlencode({'q': '!{} {}'.format(shortcut, query_string),
                       'format': 'json'})
    url = '{url}/?{query}'.format(url=instance_url, query=query)
    return url


def _check_response(resp):
    if 'Rate limit exceeded' in resp.text:
        print('Exceeded rate limit of instance', file=stderr)
        exit(3)

    resp_json = resp.json()

    if 'error' in resp_json and resp_json['error'] == 'search error':
        return EngineResult(False, resp_json['error'][0][1])
    if 'unresponsive_engines' in resp_json and len(resp_json['unresponsive_engines']) > 0:
        return EngineResult(False, resp_json['unresponsive_engines'][0][1])

    if 'results' in resp_json and len(resp_json['results']) != 0:
        return _check_results(resp_json['results'])
    if 'answers' in resp_json and len(resp_json['answers']) != 0:
        return EngineResult(True, None)
    if 'infoboxes' in resp_json and len(resp_json['infoboxes']) != 0:
        return EngineResult(True, None)

    return EngineResult(False, "No result")


def _query_engine_result(instance_url, engine, query_string):
    url = _construct_url(instance_url, query_string, engine['shortcut'])
    resp = requests.get(url)
    print('.', end='')

    return _check_response(resp)


def _request_results(instance_url, engine):
    print(engine['name'], end='')

    query_strings_key = ENGINE_QUERY.get(engine['name'], '*')
    query_strings = QUERY_STRINGS.get(query_strings_key)

    for query in query_strings:
        engine_result = _query_engine_result(instance_url, engine, query)
        if engine_result.status:
            print('OK')
            return engine_result

    print('ERROR', engine_result.error)
    return engine_result


def check_engines_state(instance_url, engines):
    engines_state = list()
    for engine in sorted(engines, key=lambda engine: engine['name']):
        provides_results = _request_results(instance_url, engine)
        engines_state.append((engine['name'], provides_results))

    return engines_state


def print_intro(instance_url, engines_number, version):
    if version is None:
        print('Searx version : unknown')
    else:
        print('Searx version : {}'.format(version))

    if engines_number == 1:
        print('Testing {} engine of {}'.format(engines_number, instance_url))
    elif engines_number > 1:
        print('Testing {} engines of {}'.format(engines_number, instance_url))
        print('This might take a while...')


def print_report(instance_url, engines_state):
    print('\nEngines of {url} not returning results:'.format(url=instance_url))
    for engine_name, engine_result in engines_state:
        if not engine_result.status:
            print('{name}: {error}'.format(name=engine_name, error=engine_result.error))
    print('You might want to check these manually...')


def write_report(instance_url, version, engines_state, file_name):
    output = {
        "timestamp": calendar.timegm(datetime.datetime.now().utctimetuple()),
        "version": version,
        "engines_state": {e[0]: { "status": e[1].status, "error": e[1].error }  for e in engines_state }
    }

    output_json = dumps(output, sort_keys=True, indent=4, ensure_ascii=False)

    with open(file_name, 'w') as outfile:
        outfile.write(output_json)


def main(instance_url, file_name):
    config = get_config(instance_url)
    engines = get_engines(config)
    version = get_version(config)

    print_intro(instance_url, len(engines), version)

    state = check_engines_state(instance_url, engines)

    print_report(instance_url, state)

    if file_name is not None:
        write_report(instance_url, version, state, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('url', metavar='URL', type=str, help='searx URL')
    parser.add_argument('-o', type=str, nargs='?', help='JSON file will contains the results')
    args = parser.parse_args()
    main(args.url, args.o)
