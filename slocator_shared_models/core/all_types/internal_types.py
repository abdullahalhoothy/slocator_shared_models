from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Any, Union


class LayerInfoInCatalogSave(BaseModel):
    layer_id: str
    points_color: str = Field(
        ..., description="Color name for the layer points, e.g., 'red'"
    )


class UserId(BaseModel):
    user_id: str


class CatalogMetaData(UserId):
    catalog_name: str
    catalog_description: str
    total_records: int


class Viewport(BaseModel):
    top_lng: Optional[float] = None
    top_lat: Optional[float] = None
    bottom_lng: Optional[float] = None
    bottom_lat: Optional[float] = None
    zoom_level: Optional[int] = None
    # add lat and lng as temporary datatypes for backward compatibility
    _lat: Optional[float] = None
    _lng: Optional[float] = None

class Intelligences(BaseModel):
    population: Optional[bool]
    income: Optional[bool]
    real_estate: Optional[bool] = False
    sample: bool = False

class IntelligenceViewport(Intelligences, Viewport):
    pass



class CatalogNonLayerItems(BaseModel):
    display_elements: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible field for frontend to store arbitrary key-value pairs",
    )
    intelligence_viewport: Optional[IntelligenceViewport] = Field(
        default=None,
        description="Flexible field for frontend to store arbitrary key-value pairs for intelligence viewport",
    )



class CatalogItems(CatalogMetaData, CatalogNonLayerItems):
    layers: List[LayerInfoInCatalogSave] = Field(
        ..., description="list of layer objects."
    )


class UserCatalogItemInfo(BaseModel):
    catalog_id: str
    thumbnail_url: str


class CatalogFullNonGeoData(CatalogItems, UserCatalogItemInfo):
    pass


class BooleanQuery(BaseModel):
    boolean_query: Optional[str] = ""


class Geometry(BaseModel):
    type: Literal["Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"]
    coordinates: Any


class Feature(BaseModel):
    type: Literal["Feature"]
    properties: dict
    geometry: Geometry

class CityCountry(BaseModel):
    city_name: str
    country_name: str

class PurchaseItem(UserId, CityCountry):
    cost: int
    expiration: Optional[str] = None
    explanation: Optional[str] = None
    is_currently_owned: Optional[bool] = None
    free_as_part_of_package: Optional[bool] = None
    description: Optional[str] = None
    data_variables: Optional[dict] = None


class ReportPurchaseItem(PurchaseItem):
    report_tier: str
    credits: int
    report_potential_business_type: Optional[str] = ""

class ConsumeReportCredit(UserId, CityCountry):
    report_tier: str
    report_potential_business_type: str


class IntelligencePurchaseItem(PurchaseItem):
    intelligence_name: str


class DatasetPurchaseItem(PurchaseItem):
    dataset_name: str


class TotalPurchaseItems(BaseModel):
    total_cost: int
    report_purchase_items: List[ReportPurchaseItem] = []
    intelligence_purchase_items: List[IntelligencePurchaseItem] = []
    dataset_purchase_items: List[DatasetPurchaseItem] = []


class LayerInfo(BaseModel):
    layer_name: str
    layer_id: str
    bknd_dataset_id: str
    points_color: str
    layer_legend: str
    layer_description: str
    records_count: int
    city_name: str
    is_zone_layer: str
    progress: Optional[int]


class StdGeoJson(BaseModel):
    type: Literal["FeatureCollection"]
    features: List[Union[Feature, str]] = []


class GeoJson(StdGeoJson):
    properties: list[str] = []


class TrafficCondition(BaseModel):
    start_index: int
    end_index: int
    speed: Optional[str]


class LegInfo(BaseModel):
    start_location: dict
    end_location: dict
    distance: float
    duration: str
    static_duration: str
    polyline: str
    # traffic_conditions: List[TrafficCondition]


class RouteInfo(BaseModel):
    origin: str
    destination: str
    route: List[LegInfo]


class NonGeoStdPoint(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    properties: dict[str, Any] = {}


class NonGeoStdPolygon(BaseModel):
    coordinates: List[NonGeoStdPoint]  # List of points defining the polygon


class NonGeoStdFeature(BaseModel):
    geometry: Union[NonGeoStdPoint, NonGeoStdPolygon]
    properties: dict[str, Any] = {}


class NonGeoStdFeatureCollection(BaseModel):
    features: List[NonGeoStdFeature] = []


class StripePaymentIntent(BaseModel):
    user_id: str
    cost: int
    description: str
