from typing import Dict, List, TypeVar, Generic, Literal, Any, Optional, Union

from pydantic import BaseModel, Field

from .internal_types import (
    CatalogMetaData,
    CatalogNonLayerItems,
    Feature,
    GeoJson,
    LayerInfo,
    LayerInfoInCatalogSave,
    RouteInfo,
    CatalogItems,
    UserCatalogItemInfo,
)
from .request_dtypes import ReqFetchDataset

T = TypeVar("T")


class ResPropertyAnalysisResult(BaseModel):
    """Individual property analysis result"""

    rank: int
    property_id: str
    final_score: float
    price: float
    url: str
    traffic_score: float
    business_score: float
    demographics_score: float
    competition_score: float


class ResAnalysisSummary(BaseModel):
    """Summary statistics for the analysis"""

    total_properties: int
    avg_score: float
    top_score: float
    avg_price: float
    total_businesses: int
    total_competitors: int


class ResModel(BaseModel, Generic[T]):
    message: str
    request_id: str
    data: T


class ResCostEstimate(BaseModel):
    cost: float
    api_calls: int
    expiration: Optional[str] = None


class ResCardMetadata(BaseModel):
    id: str
    name: str
    description: str
    thumbnail_url: str
    catalog_link: str
    records_number: int
    can_access: int


class ResCityData(BaseModel):
    name: str
    lat: float
    lng: float
    borders: Any
    type: str = None


class ResFetchDataset(BaseModel):
    type: Literal["FeatureCollection"]
    features: List[Feature]
    bknd_dataset_id: str
    layer_id: str
    records_count: int
    delay_before_next_call: Optional[int] = 0
    progress: Optional[int] = 0
    next_page_token: Optional[str] = ""


class ResSingleLayerFullData(GeoJson, LayerInfo):
    pass


class ResRecolorBasedon(ResSingleLayerFullData):
    sub_layer_id: str  # This is the additional property


class ResAddPaymentMethod(BaseModel):
    payment_method_id: str
    status: str


# types for llm agents
class ResGradientColorBasedOnZoneLLM(BaseModel):
    layers: List[ResRecolorBasedon]
    explanation: str  # This is the additional property


class ResLLMFetchDataset(BaseModel):
    """Extract Location Based Information from the Query"""

    query: str = Field(default="", description="Original query passed by the user.")
    is_valid: Literal["Valid", "Invalid"] = Field(
        default="",
        description="Status is valid if the user query is from approved categories and cities. Otherwise, it is invalid.",
    )
    reason: str = Field(
        default="",
        description="""Response message for the User after processing the query. It helps user to identify issues in the query like if city and 
                          place is an approved city or place or not.""",
    )

    endpoint: Literal["/fastapi/fetch_dataset"] = "/fastapi/fetch_dataset"

    suggestions: List[str] = Field(
        default=[], description="List of suggestions to improve the query."
    )

    body: Optional[ReqFetchDataset] = Field(
        default=None,
        description="An object containing detailed request parameters for fetching dataset",
    )
    cost: str = Field(
        default="", description="The cost value returned by calculate_cost_tool"
    )


class ResSrcDistination(BaseModel):
    distance_in_km: float
    drive_time_in_min: float
    drive_polygon: str


class ResSalesman(BaseModel):
    success: bool
    request_id: str
    plots: dict[str, str]
    metadata: dict[str, Any]


class ResIntelligenceViewport(GeoJson):
    metadata: dict[str, Any]
    records_count: int


class ResIntelligenceIsochrone(BaseModel):
    """Standard GeoJSON FeatureCollection for isochrone intelligence data.
    
    Follows GeoJSON RFC 7946 standard with metadata in feature properties.
    """
    type: Literal["FeatureCollection"]
    features: List[Dict[str, Any]]  # Each feature contains geometry and properties with metadata


class ResHubExpansion(BaseModel):
    """Response model for hub expansion analysis"""

    analysis_summary: Dict[str, Any]
    scoring_methodology: Dict[str, Any]
    primary_recommendation: Dict[str, Any]
    alternative_locations: List[Dict[str, Any]]
    market_competitive_analysis: Dict[str, Any]


class MetricConfig(BaseModel):
    name: str
    description: str
    icon: str
    default_weight: int
    min_weight: int = 0
    max_weight: int = 100


class BusinessTypeConfig(BaseModel):
    business_type: str
    display_name: str
    icon: str
    description: str
    competition_categories: List[str]
    complementary_categories: List[str]
    cross_shopping_categories: List[str]
    metrics: Dict[str, MetricConfig]


class BusinessTypeResponse(BaseModel):
    success: bool
    data: BusinessTypeConfig


class ResCartCost(BaseModel):
    total_cost_usd: float
    details: Dict[str, Any]


class ResUserCatalogInfo(UserCatalogItemInfo, CatalogMetaData):
    pass


class ResCatalog(CatalogItems):
    pass


class ResFetchCatalogWithGeoData(CatalogNonLayerItems):
    layers_geo_data: list[ResSingleLayerFullData]


class ResChat(BaseModel):
    answer: Optional[str] = None
    blocked: bool = False
    reason: Optional[str] = None


# ── Territory Design responses ────────────────────────────────────────────────

class ResTerritoryDesign(BaseModel):
    """FeatureCollection of grouped locations (mirrors server 2 TerritoryFeatureResponse)."""
    type: str
    features: List[Dict[str, Any]]
    running_time: float
    records_count: int
    groups_metadata: List[Dict[str, Any]]
    shops_map_url: str = ""
    clusters_map_url: str = ""


class ResTerritoryDesignVRP(BaseModel):
    """FeatureCollection of routed locations with savings + file URLs (mirrors VRPFeatureResponse)."""
    type: str
    features: List[Dict[str, Any]]
    running_time: float
    records_count: int
    savings: Dict[str, Any]
    excel_url: str
    html_url: str
    pdf_url: str = ""
    routes_map_url: str = ""
    shops_map_url: str = ""
    clusters_map_url: str = ""