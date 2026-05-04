from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Root"])


@router.get("/", response_class=JSONResponse)
async def read_root() -> JSONResponse:
    """
    Root endpoint that returns a simple JSON response.

    Returns
    -------
    JSONResponse
        A dictionary containing a greeting message.
    """
    return JSONResponse({"Hello": "World"})


@router.get("/health", response_class=JSONResponse)
async def health_check() -> JSONResponse:
    """
    Health check endpoint that returns a simple JSON response indicating the service is healthy.

    Returns
    -------
    JSONResponse
        A dictionary containing a health status message.
    """
    return JSONResponse({"status": "ok"})
