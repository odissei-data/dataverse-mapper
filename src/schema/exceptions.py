from fastapi.responses import JSONResponse
from main import app


class NonExistentPIDException(Exception):
    def __init__(self, pids: list):
        self.pids = pids


@app.exception_handler(NonExistentPIDException)
async def non_existent_pid_exception_handler(exc: NonExistentPIDException):
    return JSONResponse(
        status_code=422,
        content={
            "message": "No DOI found in mapped persistent identifiers:"
                       f" {exc.pids}"},
    )
