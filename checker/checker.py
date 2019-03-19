from urllib.parse import urlencode
from sys import argv, exit, stdout, stderr

import requests


CONFIG_API_ENDPOINT = '/config'

QUERY_STRINGS = {
    '*': ['test', 'savant', 'bbc.com' ],
    'normal': [ 'test', 'savant' ],
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


def is_url_image(image_url):
    if image_url.startswith('//'):
        image_url='https:' + image_url

    if image_url.startswith('data:'):
        return image_url.startswith('data:image/')

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
            print(e)
            return False


def check_result(result):
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
        return is_url_image(result.get('thumbnail_src'))
    if template == 'videos.html':
        return is_url_image(result.get('thumbnail'))
    return True


def check_results(results):
    for result in results:
        if not check_result(result):
            return False
    return True


def get_instance_url_from_params(argv):
    if len(argv) == 2:
        return argv[1]
    print('Invalid arguments', file=stderr)
    exit(1)


def get_engines(url):
    resp = requests.get(url + CONFIG_API_ENDPOINT)
    if resp.status_code != 200:
        print('Error get ', CONFIG_API_ENDPOINT, ', status code=',resp.status_code)
        exit(2)
    config = resp.json()
    if 'engines' in config:
        return config['engines']
    print('Error while getting the engines', file=stderr)
    exit(2)


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
        return False
    if 'unresponsive_engines' in resp_json and len(resp_json['unresponsive_engines']) > 0:
        return False

    if 'results' in resp_json and len(resp_json['results']) != 0:
        return check_results(resp_json['results'])
    if 'answers' in resp_json and len(resp_json['answers']) != 0:
        return True
    if 'infoboxes' in resp_json and len(resp_json['infoboxes']) != 0:
        return True

    return False


def _is_engine_result_provided(instance_url, engine, query_string):
    url = _construct_url(instance_url, query_string, engine['shortcut'])
    resp = requests.get(url)
    print('.', end='')

    return _check_response(resp)


def _request_results(instance_url, engine):
    print(engine['name'], end='')

    query_strings_key = ENGINE_QUERY.get(engine['name'], '*')
    query_strings = QUERY_STRINGS.get(query_strings_key)

    for query in query_strings:
        provides_results = _is_engine_result_provided(instance_url, engine, query)
        if provides_results:
            print('OK')
            return True

    print('ERROR')
    return False


def check_engines_state(instance_url, engines):
    engines_state = list()
    for engine in sorted(engines, key=lambda engine: engine['name']):
        provides_results = _request_results(instance_url, engine)
        engines_state.append((engine['name'], provides_results))

    return engines_state


def print_intro(instance_url, engines_number):
    if engines_number == 1:
        print('Testing {} engine of {}'.format(engines_number, instance_url))
    elif engines_number > 1:
        print('Testing {} engines of {}'.format(engines_number, instance_url))
        print('This might take a while...')


def print_report(instance_url, engines_state):
    print('\nEngines of {url} not returning results:'.format(url=instance_url))
    for engine_name, returns_resuts in engines_state:
        if not returns_resuts:
            print('{name}'.format(name=engine_name))
    print('You might want to check these manually...')


def main():
    instance_url = get_instance_url_from_params(argv)
    engines = get_engines(instance_url)

    print_intro(instance_url, len(engines))

    state = check_engines_state(instance_url, engines)

    print_report(instance_url, state)


if __name__ == "__main__":
    main()
