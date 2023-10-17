import asyncio
import inspect
import logging

from fastapi import APIRouter, FastAPI, Request, Response, WebSocket
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from manager.request import RequestManager
from manager.websocket import WebsocketManager
from payload import exception_to_payload, processed_to_payload
from workers import Workers

uvicorn_logger = logging.getLogger("uvicorn")


class ResponseHandler:
    def __init__(self, model_name, *, extra_meta=None):
        self.model_name = model_name
        self.SuccessJSONResponse = self._build_success_response()
        self.ExceptionHandlerRoute = self._build_exception_handler_route()
        self._meta = {"model": self.model_name}
        if extra_meta:
            self._meta.update(extra_meta)

    def get_meta(self):
        return self._meta

    def result_response(self, result_type, result, to_response):
        payload, status_code = processed_to_payload(result_type, result)
        payload["meta"] = self.get_meta()
        if to_response:
            return JSONResponse(payload, status_code=status_code)
        return payload

    def exception_response(self, exc, to_response):
        payload, status_code = exception_to_payload(exc)
        payload["meta"] = self.get_meta()
        if to_response:
            return JSONResponse(payload, status_code=status_code)
        return payload

    def _build_success_response(builder_self):
        class SuccessJSONResponse(JSONResponse):
            def __init__(self, content, *args, **kwargs):
                content = {
                    "success": True,
                    "data": content,
                    "meta": builder_self.get_meta(),
                }
                super().__init__(content, *args, **kwargs)

        return SuccessJSONResponse

    def _build_exception_handler_route(builder_self):
        class ExceptionHandlerRoute(APIRoute):
            def get_route_handler(self):
                original_route_handler = super().get_route_handler()

                async def custom_route_handler(request: Request):
                    try:
                        return await original_route_handler(request)
                    except HTTPException:
                        raise
                    except Exception as exc:
                        return builder_self.exception_response(exc, True)

                return custom_route_handler

        return ExceptionHandlerRoute


class FuncFastAPI(FastAPI):
    def __init__(
        self,
        function_or_object,
        validator,
        *args,
        model_name=None,
        threads=1,
        batch_size=32,
        cache_size=0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if inspect.isfunction(function_or_object) or inspect.ismethod(
            function_or_object
        ):
            function = function_or_object
        else:
            function = function_or_object.__call__
        try:
            extra_meta = function_or_object.get_meta()
        except AttributeError:
            extra_meta = None
        response_handler = ResponseHandler(model_name, extra_meta=extra_meta)
        self.api_router = APIRouter(
            route_class=response_handler.ExceptionHandlerRoute,
            default_response_class=response_handler.SuccessJSONResponse,
        )
        self.workers = Workers(
            function, num_threads=threads, batch_size=batch_size, cache_size=cache_size
        )
        self.model_name = model_name

        async def validate(_: validator):
            pass

        async def index(body: validator, request: Request):
            return await RequestManager(request, response_handler).send_to_workers(
                body.dict(), self.workers
            )

        async def websocket(websocket: WebSocket):
            await WebsocketManager(
                websocket, validator, response_handler
            ).loop_until_disconnect(self.workers)

        async def health():
            pass

        async def statistics():
            return self.workers.statistics() | {
                "futures in event loop": len(
                    asyncio.all_tasks(asyncio.get_running_loop())
                )
            }

        _schema = validator.schema()

        async def schema():
            return _schema

        self.on_event("startup")(self.log_settings)
        self.on_event("startup")(self.workers.startup)
        self.on_event("shutdown")(self.workers.shutdown)
        self.api_router.post("/validate")(validate)
        self.api_router.post("/")(index)
        self.api_router.get("/health")(health)
        self.api_router.get("/statistics")(statistics)
        self.api_router.get("/schema")(schema)
        self.api_router.websocket("/websocket")(websocket)
        if hasattr(function_or_object, "router_hook"):
            function_or_object.router_hook(self.api_router)
        self.include_router(self.api_router, prefix="")

    def log_settings(self):
        for setting, value in self.workers.settings().items():
            uvicorn_logger.info(f"{setting.upper()}: {value}")
