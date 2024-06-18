from celery import shared_task, states
import requests
import os
import logging

logger=logging.getLogger('worker')
logger.setLevel(logging.DEBUG)
logger.debug('Setting logging level to DEBUG')

@shared_task(bind=True)
def download_file(self, url, filename, filetype, directory):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192  # 8 KB chunks
        downloaded_size = 0
        filename = filename + "." + filetype
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            raise FileExistsError("File already exists")

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    progress = (downloaded_size / total_size) * 100
                    self.update_state(state='PROGRESS', meta={'progress': progress})

        return {'file_path': file_path, 'progress': 100}

    except requests.exceptions.RequestException as e:
        logger.debug(str(e))
        self.update_state(state=states.FAILURE, )

    except FileExistsError as e:
        logger.debug(str(e))
        self.update_state(state=states.FAILURE)

    except Exception as e:
        logger.debug(str(e))
        self.update_state(state=states.FAILURE)
