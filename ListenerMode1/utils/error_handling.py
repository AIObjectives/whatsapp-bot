from fastapi import HTTPException

def handle_exception(logger, error_message):
    logger.error(error_message)
    raise HTTPException(status_code=500, detail=error_message)
