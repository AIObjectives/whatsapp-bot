from shared.firebase_setup import db
from shared.logger import logger

def initialize_listener_event(event_id, config):
    collection_ref = db.collection(f'Listener_{event_id}')
    info_doc_ref = collection_ref.document('info')

    info_doc_ref.set({
        'event_initialized': True,
        **config
    })
    logger.info(f"Listener mode event '{config['event_name']}' initialized.")
