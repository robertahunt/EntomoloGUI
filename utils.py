import requests
import logging


def try_url(url):

    log = logging.getLogger("UThread")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        log.info(
            f'RequestException encountered connecting to url: "{url}", Exception raised: "{err}"'
        )
    except requests.exceptions.HTTPError as errh:
        log.info(
            f'HTTPError encountered connecting to url: "{url}", Exception raised: "{errh}"'
        )
    except requests.exceptions.ConnectionError as errc:
        log.info(
            f'ConnectionError encountered connecting to url: "{url}", Exception raised: "{errc}"'
        )
    except requests.exceptions.Timeout as errt:
        log.info(
            f'Timeout encountered connecting to url: "{url}", Exception raised: "{errt}"'
        )
    except Exception as e:
        log.info(f'Error connecting to url: "{url}", Exception raised: "{e}"')

    return None
