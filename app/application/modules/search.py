from flask import current_app
from application import celery
from whoosh.filedb.filestore import FileStorage

def index_document(indice: str, data: dict):
    store = FileStorage(indice)
    ix = store.open_index()
    current_app.logger.debug('Writing {} to {}'.format(data, indice))
    with ix.writer() as writer:
        writer.update_document(**data)

@celery.task
def index_document_async(*args, **kwargs):
    index_document(*args, **kwargs)
