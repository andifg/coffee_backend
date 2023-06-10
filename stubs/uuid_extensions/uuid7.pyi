import datetime
import time
import uuid
from typing import Callable, List, Optional, Union

time_ns = time.time_ns

def uuid7(
    ns: Optional[int] = ...,
    as_type: Optional[str] = ...,
    time_func: Callable[[], int] = ...,
    _last: Optional[List[int]] = ...,
    _last_as_of: Optional[List[int]] = ...,
) -> uuid.UUID: ...
def uuid7str(ns: Optional[int] = ...) -> str: ...
def check_timing_precision(
    timing_func: Optional[Callable[[], int]] = ...
) -> str: ...
def uuid_to_datetime(
    s: Union[str, uuid.UUID, int], suppress_error: bool = ...
) -> Optional[datetime.datetime]: ...
