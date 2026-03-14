from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success(data=None, message: str = "Success", status_code: int = 200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    # jsonable_encoder converts datetime, UUID, Enum → JSON-safe types
    return JSONResponse(content=jsonable_encoder(body), status_code=status_code)


def error(message: str = "Error", status_code: int = 400):
    return JSONResponse(
        content={"success": False, "message": message},
        status_code=status_code,
    )
