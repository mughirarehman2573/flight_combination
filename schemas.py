from pydantic import BaseModel
from typing import List, Union, Tuple, Optional, Dict


class ReDepartureStrategy(BaseModel):
    roadtrip_km: Optional[Tuple[int, int]] = None
    custom_redeparture_airports: Optional[List[str]] = None

class Stop(BaseModel):
    destination: Union[str, List[str]]
    stay_range: Tuple[int, int]
    re_departure_strategy: ReDepartureStrategy

class GeneralSettings(BaseModel):
    departure_date_range: Tuple[str, str]
    total_stay_range: Tuple[int, int]
    departure_airports: List[str]
    exclude_departure_weekdays: List[str]
    exclude_return_weekdays: List[str]
    return_to: Union[str, List[str], Dict[str, Tuple[int, int]]]

class RequestModel(BaseModel):
    general: GeneralSettings
    number_of_stops: int
    interchangeable_stops: bool
    stops: List[Stop]
