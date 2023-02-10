import logging
import requests
import numpy as np

from PIL import Image
from logging import handlers
from PIL.ImageQt import ImageQt


def init_logger(debug):
    log_level = logging.DEBUG if debug else logging.INFO

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s in %(pathname)s:%(lineno)d"
    )
    logger = logging.getLogger()
    logger.setLevel(log_level)

    fileHandler = handlers.RotatingFileHandler(
        "log.log", maxBytes=(1048576 * 5), backupCount=7
    )
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger


def try_url(url):

    log = logging.getLogger("UThread")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        log.debug(
            f'RequestException encountered connecting to url: "{url}", Exception raised: "{err}"'
        )
    except requests.exceptions.HTTPError as errh:
        log.debug(
            f'HTTPError encountered connecting to url: "{url}", Exception raised: "{errh}"'
        )
    except requests.exceptions.ConnectionError as errc:
        log.debug(
            f'ConnectionError encountered connecting to url: "{url}", Exception raised: "{errc}"'
        )
    except requests.exceptions.Timeout as errt:
        log.debug(
            f'Timeout encountered connecting to url: "{url}", Exception raised: "{errt}"'
        )
    except Exception as e:
        log.debug(f'Error connecting to url: "{url}", Exception raised: "{e}"')

    return None


def make_big_x(width, height):
    size = max(width, height)
    thickness = 5

    big_x = np.abs(np.add.outer(np.arange(size), -np.arange(size))) < thickness
    big_x = (big_x | np.fliplr(big_x)).astype("uint8") * 255
    big_x = np.repeat(big_x[..., np.newaxis], 3, axis=-1)

    start_row = big_x.shape[0] // 2 - height // 2
    end_row = big_x.shape[0] // 2 + height // 2
    start_col = big_x.shape[0] // 2 - width // 2
    end_col = big_x.shape[0] // 2 + width // 2

    big_x = big_x[start_row:end_row, start_col:end_col]
    return ImageQt(Image.fromarray(big_x))
