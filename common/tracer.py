import functools
from contextvars import ContextVar

import aiozipkin as az

from aiozipkin import Tracer, SpanAbc

_tracer: ContextVar[Tracer | None] = ContextVar("_tracer", default=None)
_span: ContextVar[SpanAbc | None] = ContextVar("_span", default=None)


async def setup(zipkin_address: str, service_name: str, sample_rate: float = 1.0, **kwargs) -> None:
    endpoint = az.create_endpoint(service_name)
    set_tracer(await az.create(zipkin_address, endpoint, sample_rate=sample_rate, **kwargs))


def setup_decorator(zipkin_address: str, service_name: str, sample_rate: float = 1.0, **kwargs):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs_):
            await setup(
                zipkin_address=zipkin_address,
                service_name=service_name,
                sample_rate=sample_rate,
                **kwargs,
            )
            try:
                return await func(*args, **kwargs_)
            finally:
                if tracer := get_tracer():
                    await tracer.close()

        return wrapped

    return wrapper


async def close():
    tracer = get_tracer()
    await tracer.close()


def get_tracer() -> Tracer | None:
    return _tracer.get()


def set_tracer(tracer: Tracer) -> None:
    _tracer.set(tracer)


def get_span() -> SpanAbc | None:
    return _span.get()


def _set_span(span: SpanAbc) -> None:
    _span.set(span)


def annotate(msg: str, timestamp: float | None = None) -> None:
    if span := get_span():
        span.annotate(msg, ts=timestamp)


def tag(key: str, value: str) -> None:
    if span := get_span():
        span.tag(key, value)


def name(span_name: str) -> None:
    if span := get_span():
        span.name(span_name)


def kind(span_kind: str) -> None:
    if span := get_span():
        span.kind(span_kind)


def trace(func_=None, *, span_name: str | None = None):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if not get_tracer():
                return await func(*args, **kwargs)

            span = get_span()
            if span:
                new_span = span.new_child()
            else:
                new_span = get_tracer().new_trace(sampled=True)
            _set_span(new_span)
            try:
                with new_span:
                    new_span.name(span_name or func.__qualname__)
                    return await func(*args, **kwargs)
            finally:
                _set_span(span)

        return wrapped

    if func_:
        return wrapper(func_)
    else:
        return wrapper
