from typing import Dict, List, TypeVar, Generic, Optional
from fastapi import UploadFile

from pydantic import BaseModel, Field, field_validator, model_validator

from preloaded_constants import ALL_POI_CATEGORIES_LOWER
from .internal_types import (
    CatalogItems,
    Intelligences,
    NonGeoStdPoint,
    StdGeoJson,
    UserId,
    BooleanQuery,
    IntelligenceViewport,
    Viewport,
)

U = TypeVar("U")


class ReqModel(BaseModel, Generic[U]):
    message: str
    request_info: Dict
    request_body: U


class ReqCityCountry(BaseModel):
    city_name: str
    country_name: str


class boxmapProperties(BaseModel):
    name: str
    rating: float
    address: str
    phone: str
    website: str
    business_status: str
    user_ratings_total: int


class ReqSaveCatalog(CatalogItems):
    image: Optional[UploadFile] = None


class ReqDeleteCatalog(UserId):
    catalog_id: str


class ZoneLayerInfo(BaseModel):
    layer_id: str
    property_key: str


class ReqCatalogId(UserId):
    catalog_id: str


class ReqSingleLayerFullData(UserId):
    layer_id: Optional[str] = ""


class ReqSaveLyer(ReqSingleLayerFullData):
    layer_name: str
    bknd_dataset_id: str
    points_color: str
    layer_legend: str
    layer_description: str
    city_name: str


class ReqDeleteLayer(BaseModel):
    user_id: str
    layer_id: str


class ReqFetchDataset(ReqCityCountry, ReqSingleLayerFullData, Viewport):
    boolean_query: Optional[str] = ""
    action: Optional[str] = ""
    page_token: Optional[str] = ""
    search_type: Optional[str] = "category_search"
    zoom_level: Optional[int] = 0
    radius: Optional[float] = 30000.0
    bounding_box: Optional[list[float]] = []
    included_types: Optional[list[str]] = []
    excluded_types: Optional[list[str]] = []
    include_only_sub_properties: Optional[bool] = True
    full_load: Optional[bool] = False


class ReqFetchCatalogLayers(BaseModel):
    catalog_id: str
    as_layers: bool
    user_id: str


class ReqStreeViewCheck(NonGeoStdPoint):
    pass


class ReqGeodata(NonGeoStdPoint):
    bounding_box: list[float]


class ReqNearestRoute(ReqSingleLayerFullData):
    points: List[NonGeoStdPoint]


class ReqColorBasedon(BaseModel):
    change_layer_id: str
    change_layer_name: str
    change_layer_current_color: str = "#CCCCCC"
    change_layer_new_color: str = "#FFFFFF"
    based_on_layer_id: str
    based_on_layer_name: str
    area_coverage_value: float  # [10min , 20min or 300 m or 500m]
    area_coverage_measure: str  # [Drive_time or Radius]
    evaluation_property_name: str  # ["rating" or "user_ratings_total"]
    evaluation_comparison_operator: str
    color_grid_choice: Optional[List[str]] = []
    evaluation_name_list: Optional[List[str]] = []


class ReqFilterBasedon(ReqColorBasedon):
    property_threshold: float | str


class LayerReference(BaseModel):
    id: str
    name: str


# User prompt -> llm
class ReqLLMEditBasedon(BaseModel):
    user_id: str
    layers: List[LayerReference] = Field(
        ..., description="List of layers with required id and name fields"
    )
    prompt: str


class ResValidationResult(BaseModel):
    is_valid: bool
    reason: Optional[str] = None
    suggestions: Optional[List[str]] = None
    endpoint: Optional[str] = None
    body: ReqColorBasedon = None
    recolor_result: Optional[List] = None


class ReqLLMFetchDataset(UserId, Viewport):
    """Extract Location Based Information from the Query"""

    query: str = Field(default="", description="Original query passed by the user.")


class ReqSrcDistination(BaseModel):
    source: NonGeoStdPoint
    destination: NonGeoStdPoint


class ReqDriveTimePolygon(BaseModel):
    """Request model for Mapbox Isochrone API.

    Creates isochrone contours (polygons or lines) showing areas reachable within
    specified time or distance from a location.
    """

    source_point: NonGeoStdPoint
    # Routing profile - determines travel mode
    profile: str = Field(
        default="mapbox/driving-traffic",
        description="Mapbox routing profile: mapbox/driving-traffic, mapbox/driving, mapbox/walking, or mapbox/cycling",
    )
    # Contour specification (exactly one must be provided)
    contours_minutes: Optional[List[int]] = Field(
        default=[10, 15, 25],
        description="Times in minutes for each contour (1-4 values, max 60 minutes each)",
    )
    depart_at: Optional[str] = Field(
        default="2025-12-06T22:00:00Z",  # saturday at 10 pm
        description="Departure time in ISO 8601 format (YYYY-MM-DDThh:mm:ssZ)",
    )
    # Visual customization
    contours_colors: Optional[List[str]] = Field(
        default=[],
        description="Hex color codes for contours (without #), must match number of contours, If no colors are specified, the Isochrone API will assign a default rainbow color scheme to the output.",
    )
    polygons: bool = Field(
        default=True, description="Return as polygons (true) or linestrings (false)"
    )
    # Refinement options
    denoise: Optional[float] = Field(
        default=1.0,
        description="Remove smaller contours (0.0-1.0, where 1.0 keeps only largest)",
    )
    generalize: Optional[float] = Field(
        default=0.0,
        description="Tolerance for Douglas-Peucker generalization in meters",
    )
    # Routing restrictions
    exclude: Optional[str] = Field(
        default="",
        description="Comma-separated road types to exclude: motorway, toll, ferry, unpaved, cash_only_tolls",
    )
    contours_meters: Optional[List[int]] = Field(
        default=[],
        description="Distances in meters for each contour (1-4 values, max 100000 meters each)",
    )

    @field_validator("contours_minutes", "contours_meters")
    @classmethod
    def validate_contours(cls, v, info):
        if v:
            if len(v) > 4:
                raise ValueError("Maximum 4 contours allowed")
            if len(v) == 0:
                raise ValueError("At least 1 contour required")
            if v:
                if v != sorted(v):
                    raise ValueError("Contours must be in increasing order")
        return v

    @field_validator("contours_minutes")
    @classmethod
    def validate_minutes(cls, v):
        if v:
            if any(m < 1 or m > 60 for m in v):
                raise ValueError("Contours must be between 1 and 60 minutes")
        return v

    @field_validator("contours_meters")
    @classmethod
    def validate_meters(cls, v):
        if v:
            if any(m < 1 or m > 100000 for m in v):
                raise ValueError("Contours must be between 1 and 100000 meters")
        return v


class ReqIntelligenceViewport(IntelligenceViewport, UserId):
    city_name: str = "Riyadh"
    country_name: str = "Saudi Arabia"


class ReqIntelligenceIsochrone(ReqDriveTimePolygon, Intelligences, UserId):
    """Request intelligence data within an isochrone polygon area.

    Automatically generates isochrone polygon using Mapbox Isochrone API
    based on the inherited ReqDriveTimePolygon parameters (source_point,
    profile, contours_minutes/meters, etc.).
    """
    zoom_level: Optional[int] = 12
    city_name: str = "Riyadh"
    country_name: str = "Saudi Arabia"


class ReqIntelligencePolygon(Intelligences, UserId):
    """Request intelligence data within a custom drawn polygon area.

    Accepts a GeoJSON FeatureCollection of polygon(s) drawn by the user on the map.
    All polygons are unioned before querying the PostGIS intelligence tables.
    """
    polygons: StdGeoJson
    zoom_level: Optional[int] = 12
    city_name: str = "Riyadh"
    country_name: str = "Saudi Arabia"


class ReqFetchPoiByPolygon(UserId, ReqCityCountry):
    polygons: StdGeoJson
    boolean_query: Optional[str] = ""
    excluded_names: Optional[List[str]] = []
    layer_id: Optional[str] = ""
    action: Optional[str] = "full data"


class ReqClustersForSalesManData(BooleanQuery, UserId, ReqCityCountry):
    num_sales_man: int
    distance_limit: float = 2.5
    include_raw_data: bool = False


class ReqTerritoryDesign(UserId, ReqCityCountry):
    """Request for territory grouping via server 2. Fetches POI by polygon internally."""
    polygons: StdGeoJson
    boolean_query: Optional[str] = ""
    excluded_names: Optional[List[str]] = []
    num_groups: int
    group_size: int
    outlier_cut_km: float = 0.5
    centroid_lat: float = 21.57066003450175
    centroid_lng: float = 39.19046819882582
    group_size_prune_max: float = 0.05
    max_solving_time: float = 30.0
#       "centroid_lat": 21.57066003450175,
#   "centroid_lng": 39.19046819882582,
#   "group_size_prune_max": 0.05,
#   "max_solving_time": 30.0


class DriverStartPosition(BaseModel):
    """Lat/lng of the driver depot for the single active polygon area."""
    lat: float
    lng: float


class ReqTerritoryDesignVRP(ReqTerritoryDesign):
    """Territory design + VRP scheduling with savings report."""
    num_work_days: int = 12
    current_daily_km_per_van: float = 200.0
    weekly_refill_sar: float = 300.0    
    work_hours_per_day: float = 10.0
    store_visit_minutes: float = 20.0
    current_stores_per_day: int = 20
    driver_monthly_salary_sar: float = 3000.0
    planner_monthly_salary_sar: float = 5000.0
    work_days_per_week: int = 6
    work_days_per_month: int = 24
    avg_revenue_per_store_sar: float = 1500.0
    revenue_period_days: int = 14
    # One start/end depot per polygon area. None means fall back to cluster centroid.
    # Future: extend to Dict[str, DriverStartPosition] when multi-polygon is supported.
    driver_start: Optional[DriverStartPosition] = None


class ReqHubExpansion(BaseModel):
    """Default configuration for hub expansion analysis"""

    # User context
    user_id: str = "default_user"
    # Location context
    city_name: str = "Riyadh"
    country_name: str = "Saudi Arabia"
    analysis_bounds: Optional[dict] = {}

    # Target destinations
    target_search: str = "@الحلقه@"
    max_target_distance_km: float = 5.0
    max_target_time_minutes: int = 8
    search_type: str = "keyword_search"

    # Competitor analysis
    competitor_name: str = "@نينجا@"
    competitor_analysis_radius_km: float = 2.0
    search_type: str = "keyword_search"

    # Hub requirements
    hub_type: str = "warehouse_for_rent"
    min_facility_size_m2: Optional[int] = None
    max_rent_per_m2: Optional[float] = None
    search_type: str = "category_search"

    # Population requirements
    max_population_center_distance_km: float = 10.0
    max_population_center_time_minutes: int = 15
    min_population_threshold: int = 1000

    # Analysis parameters
    scoring_weights: Dict[str, float] = {
        "target_proximity": 0.35,
        "population_access": 0.30,
        "rent_efficiency": 0.10,
        "competitive_advantage": 0.15,
        "population_coverage": 0.10,
    }

    # Scoring thresholds
    scoring_thresholds: Dict[str, Dict[str, float]] = {
        "target_proximity": {
            "min_score": 0.0,
            "max_score": 10.0,
            "penalty_multiplier": 1.0,
        },
        "population_access": {
            "min_score": 0.0,
            "max_score": 10.0,
            "accessibility_bonus_max": 3.0,
        },
        "rent_efficiency": {"min_score": 0.0, "max_score": 10.0},
        "competitive_advantage": {
            "min_score": 2.0,
            "max_score": 10.0,
            "density_penalty_max": 5.0,
        },
        "population_coverage": {"min_score": 0.0, "max_score": 10.0},
    }

    # Coverage methodology
    density_thresholds: Dict[str, Dict[str, float]] = {
        "very_high_density": {
            "threshold": 8000,
            "radius_km": 2.0,
            "max_delivery_minutes": 20,
        },
        "high_density": {
            "threshold": 4000,
            "radius_km": 3.5,
            "max_delivery_minutes": 25,
        },
        "medium_density": {
            "threshold": 2000,
            "radius_km": 5.0,
            "max_delivery_minutes": 30,
        },
        "low_density": {
            "threshold": 0,
            "radius_km": 8.0,
            "max_delivery_minutes": 40,
        },
    }

    # Output preferences
    top_results_count: int = 5
    include_route_optimization: bool = True
    include_market_analysis: bool = True
    include_success_metrics: bool = True

    # User context
    user_id: str = "default_user"


class EvaluationMetrics(BaseModel):
    traffic: float = 0.25
    demographics: float = 0.3
    competition: float = 0.15
    complementary: float = 0.2
    cross_shopping: float = 0.1


class ZoneWeights(BaseModel):
    """Weights for different zones in multi-zone analysis.

    Weights should sum to 1.0 for proper normalization.
    Represents importance of each zone for a specific metric.

    5-zone system:
    - walking: Configurable walking distance (default 500m)
    - time1_peak: First driving time at peak traffic (default 10min)
    - time1_offpeak: First driving time at off-peak traffic (default 10min)
    - time2_peak: Second driving time at peak traffic (default 15min)
    - time3_peak: Third driving time at peak traffic (default 25min)
    """

    walking_distance: float = Field(
        default=0.20, ge=0.0, le=1.0, description="Weight for walking distance zone"
    )
    time1_peak: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Weight for first driving time (peak traffic)",
    )
    time1_offpeak: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Weight for first driving time (off-peak traffic)",
    )
    time2_peak: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Weight for second driving time (peak traffic)",
    )
    time3_peak: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Weight for third driving time (peak traffic)",
    )

    def model_post_init(self, __context):
        total = (
            self.walking_distance
            + self.time1_peak
            + self.time1_offpeak
            + self.time2_peak
            + self.time3_peak
        )
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValueError(f"Zone weights must sum to 1.0, got {total}")
        return self


class MetricZoneWeights(BaseModel):
    """Zone weights configuration for each business metric type.

    Different metrics have different zone importance patterns:
    - Demographics: Balanced across zones (people drive for services)
    - Competition: Heavily weighted to immediate vicinity (walking + first peak time)
    - Complementary: Same as competition (nearby businesses matter most)
    - Cross-shopping: Very local (80% walking, minimal driving zones)
    """

    demographics: ZoneWeights = Field(
        default_factory=lambda: ZoneWeights(
            walking_distance=0.20,
            time1_peak=0.30,
            time1_offpeak=0.10,
            time2_peak=0.25,
            time3_peak=0.15,
        ),
        description="Zone weights for demographics analysis",
    )
    competition: ZoneWeights = Field(
        default_factory=lambda: ZoneWeights(
            walking_distance=0.50,
            time1_peak=0.30,
            time1_offpeak=0.10,
            time2_peak=0.10,
            time3_peak=0.0,
        ),
        description="Zone weights for competition analysis (immediate vicinity critical)",
    )
    complementary: ZoneWeights = Field(
        default_factory=lambda: ZoneWeights(
            walking_distance=0.50,
            time1_peak=0.30,
            time1_offpeak=0.10,
            time2_peak=0.10,
            time3_peak=0.0,
        ),
        description="Zone weights for complementary businesses (nearby matters most)",
    )
    cross_shopping: ZoneWeights = Field(
        default_factory=lambda: ZoneWeights(
            walking_distance=0.70,
            time1_peak=0.15,
            time1_offpeak=0.05,
            time2_peak=0.10,
            time3_peak=0.0,
        ),
        description="Zone weights for cross-shopping (walking distance critical)",
    )


class DemographicsComponentWeights(BaseModel):
    """Component weights for demographics scoring."""

    deviation_from_target: float = 0.25
    category_density: float = 0.20
    population_per_business: float = 0.20
    estimated_overlap: float = 0.15
    traffic_variability: float = 0.10
    fuel_cost: float = 0.10

    def model_post_init(self, __context):
        total = (
            self.deviation_from_target
            + self.category_density
            + self.population_per_business
            + self.estimated_overlap
            + self.traffic_variability
            + self.fuel_cost
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Demographics component weights must sum to 1.0, got {total}"
            )
        return self


class CompetitionComponentWeights(BaseModel):
    """Component weights for competition scoring."""

    deviation_from_target: float = 0.30
    category_density: float = 0.30
    population_per_business: float = 0.20
    estimated_overlap: float = 0.20

    def model_post_init(self, __context):
        total = (
            self.deviation_from_target
            + self.category_density
            + self.population_per_business
            + self.estimated_overlap
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Competition component weights must sum to 1.0, got {total}"
            )
        return self


class ComplementaryComponentWeights(BaseModel):
    """Component weights for complementary business scoring."""

    deviation_from_target: float = 0.30
    category_density: float = 0.30
    population_per_business: float = 0.20
    estimated_overlap: float = 0.20

    def model_post_init(self, __context):
        total = (
            self.deviation_from_target
            + self.category_density
            + self.population_per_business
            + self.estimated_overlap
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Complementary component weights must sum to 1.0, got {total}"
            )
        return self


class CrossShoppingComponentWeights(BaseModel):
    """Component weights for cross-shopping scoring."""

    deviation_from_target: float = 0.30
    category_density: float = 0.30
    population_per_business: float = 0.20
    estimated_overlap: float = 0.20

    def model_post_init(self, __context):
        total = (
            self.deviation_from_target
            + self.category_density
            + self.population_per_business
            + self.estimated_overlap
        )
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Cross-shopping component weights must sum to 1.0, got {total}"
            )
        return self



class Reqsmartreport(UserId):
    city_name: str = "Riyadh"
    country_name: str = "Saudi Arabia"
    potential_business_type: str
    target_income_level: str = "medium"  # low, medium, high
    target_age: int = 30
    avg_order_value: float = 30

    # Isochrone configuration (user-configurable)
    walking_distance: int = 500
    time1_peak: int = 10
    time1_offpeak: int = 10
    time2_peak: int = 15
    time3_peak: int = 25
    peak_time_iso8601: str = "2025-12-06T22:00:00Z"  # Saturday 10 PM
    offpeak_time_iso8601: str = "2025-12-10T10:00:00Z"  # Wednesday 10 AM

    iso_names: List[str] = [
        "walking_distance",
        "time1_peak",
        "time1_offpeak",
        "time2_peak",
        "time3_peak",
    ]
    iso_display_names: List[str] = [
        "Walking (500m)",
        "Driving 10min (peak)",
        "Driving 10min (off-peak)",
        "Driving 15min (peak)",
        "Driving 25min (peak)",
    ]
    iso_colors: List[str] = [
        "#9370db",  # medium purple
        "#4169e1",  # royal blue
        "#32cd32",  # green
        "#ffa500",  # orange
        "#ff7f50",  # light coral
    ]

    # Delivery configuration - demographics component weights
    delivery_demographics_deviation_from_target: float = 0.25
    delivery_demographics_category_density: float = 0.20
    delivery_demographics_population_per_business: float = 0.20
    delivery_demographics_estimated_overlap: float = 0.15
    delivery_demographics_traffic_variability: float = 0.10
    delivery_demographics_fuel_cost: float = 0.10
    # Delivery configuration - competition component weights
    delivery_competition_deviation_from_target: float = 0.30
    delivery_competition_category_density: float = 0.30
    delivery_competition_population_per_business: float = 0.20
    delivery_competition_estimated_overlap: float = 0.20
    # Delivery configuration - complementary component weights
    delivery_complementary_deviation_from_target: float = 0.30
    delivery_complementary_category_density: float = 0.30
    delivery_complementary_population_per_business: float = 0.20
    delivery_complementary_estimated_overlap: float = 0.20
    # Delivery configuration - cross-shopping component weights
    delivery_cross_shopping_deviation_from_target: float = 0.30
    delivery_cross_shopping_category_density: float = 0.30
    delivery_cross_shopping_population_per_business: float = 0.20
    delivery_cross_shopping_estimated_overlap: float = 0.20
    # Delivery configuration - specific parameters
    delivery_driver_salary_per_hour: float = 50.0
    delivery_fuel_cost_per_km: float = 0.5
    delivery_expected_orders_per_day: int = 100
    delivery_time_cost_multiplier: float = 1.0
    delivery_rent_based_cost_efficiency: float = 1.0

    # Dine-in configuration - demographics component weights (no traffic_variability/fuel_cost)
    dine_in_demographics_deviation_from_target: float = 0.40
    dine_in_demographics_category_density: float = 0.25
    dine_in_demographics_population_per_business: float = 0.20
    dine_in_demographics_estimated_overlap: float = 0.15
    dine_in_demographics_traffic_variability: float = 0.0
    dine_in_demographics_fuel_cost: float = 0.0
    # Dine-in configuration - competition component weights
    dine_in_competition_deviation_from_target: float = 0.30
    dine_in_competition_category_density: float = 0.30
    dine_in_competition_population_per_business: float = 0.20
    dine_in_competition_estimated_overlap: float = 0.20
    # Dine-in configuration - complementary component weights
    dine_in_complementary_deviation_from_target: float = 0.30
    dine_in_complementary_category_density: float = 0.30
    dine_in_complementary_population_per_business: float = 0.20
    dine_in_complementary_estimated_overlap: float = 0.20
    # Dine-in configuration - cross-shopping component weights
    dine_in_cross_shopping_deviation_from_target: float = 0.30
    dine_in_cross_shopping_category_density: float = 0.30
    dine_in_cross_shopping_population_per_business: float = 0.20
    dine_in_cross_shopping_estimated_overlap: float = 0.20

##################################################################################################
##################################################################################################
##################################################################################################

    # Delivery zone weights - cross-shopping
    delivery_zone_walking_distance: float = 0.20
    delivery_zone_time1_peak: float = 0.20
    delivery_zone_time1_offpeak: float = 0.20
    delivery_zone_time2_peak: float = 0.20
    delivery_zone_time3_peak: float = 0.20
    # Dine-in zone weights - demographics
    dine_in_zone_walking_distance: float = 0.20
    dine_in_zone_time1_peak: float = 0.30
    dine_in_zone_time1_offpeak: float = 0.10
    dine_in_zone_time2_peak: float = 0.25
    dine_in_zone_time3_peak: float = 0.15

    def get_zone_weights(self, mode: str = "delivery") -> list[float]:
        """
        Returns a list of zone weights for the specified mode ("delivery" or "dine_in"),
        in the order of self.iso_names. Defaults to 0.2 if attribute is missing.
        """
        prefix = f"{mode}_zone_"
        return [getattr(self, f"{prefix}{zone}", 0.2) for zone in self.iso_names]

    @property
    def delivery_zone_weights(self) -> list[float]:
        """List of delivery zone weights in iso_names order."""
        return self.get_zone_weights("delivery")

    @property
    def dine_in_zone_weights(self) -> list[float]:
        """List of dine-in zone weights in iso_names order."""
        return self.get_zone_weights("dine_in")
##################################################################################################
##################################################################################################
##################################################################################################
    # Dine-in configuration - metric-level weights
    dine_in_demographics_weight: float = 0.20
    dine_in_competition_weight: float = 0.20
    dine_in_complementary_weight: float = 0.20
    dine_in_cross_shopping_weight: float = 0.20
    dine_in_traffic_weight: float = 0.20
    # Delivery configuration - metric-level weights
    delivery_demographics_weight: float = 0.20
    delivery_competition_weight: float = 0.20
    delivery_complementary_weight: float = 0.20
    delivery_cross_shopping_weight: float = 0.20
    delivery_traffic_weight: float = 0.20
##################################################################################################
##################################################################################################
##################################################################################################

    delivery_weight: float = 0.5  # Weight for delivery in combined mode (0.0 to 1.0)
    dine_in_weight: float = 0.5  # Weight for dine-in in combined mode (0.0 to 1.0)

    complementary_categories: List[str] = [
        "hospital",
        "dentist",
    ]  # Medical complementary businesses
    optimal_num_complementary_businesses_per_category: int = (
        2  # Ideal number of complementary businesses per category
    )
    cross_shopping_categories: List[str] = [
        "grocery_store",
        "supermarket",
    ]  # Cross-shopping opportunities
    optimal_num_cross_shopping_businesses_per_category: int = (
        3  # Ideal number of cross-shopping businesses per category
    )
    competition_categories: List[str] = ["pharmacy"]
    optimal_num_competition_businesses_per_category: int = 1  # Ideal number of competition businesses per category (raw count in smallest isochrone)
    optimal_competition_per_capita: float = 0.0001  # Ideal competition density per person (e.g., 0.0001 = 1 per 10k when displayed)
    optimal_complementary_per_capita: float = 0.0002  # Ideal complementary density per person (e.g., 0.0002 = 2 per 10k when displayed)
    optimal_cross_shopping_per_capita: float = 0.0003  # Ideal cross-shopping density per person (e.g., 0.0003 = 3 per 10k when displayed)
    custom_locations: Optional[List[NonGeoStdPoint]] = (
        None  # In case the client or user wants to analyze specific locations that don't exist in our db so he will provide the coordinates
    )
    current_location: Optional[NonGeoStdPoint] = (
        None  # In case a client wants to analyze his current location
    )
    single_location: bool = False
    report_tier: str = "premium"  # "basic", "standard", "premium"

    @field_validator("potential_business_type")
    @classmethod
    def validate_potential_business_type(cls, v):
        """
        Validate that the potential_business_type (single string) exists in the POI list.
        Uses ALL_POI_CATEGORIES_LOWER loaded at app startup as the single source of truth.
        """

        if "@" in v:
            return v

        if v.lower() not in ALL_POI_CATEGORIES_LOWER:
            raise ValueError(
                f"Category '{v}' is not in the valid POI list. "
                f"Please use one of the available categories from the /nearby_categories endpoint."
            )
        return v

    @field_validator(
        "complementary_categories",
        "cross_shopping_categories",
        "competition_categories",
    )
    @classmethod
    def validate_category_lists(cls, v):
        """
        Validate that all categories in the list exist in the POI list.
        Validates complementary_categories, cross_shopping_categories, and competition_categories.
        Uses ALL_POI_CATEGORIES_LOWER loaded at app startup as the single source of truth.
        """

        for category in v:
            if "@" in category:
                continue
            if category.lower() not in ALL_POI_CATEGORIES_LOWER:
                raise ValueError(
                    f"Category '{category}' is not in the valid POI list. "
                    f"Please use one of the available categories from the /nearby_categories endpoint."
                )
        return v

    @field_validator("avg_order_value")
    @classmethod
    def validate_avg_order_value(cls, v):
        if v <= 0:
            raise ValueError("avg_order_value must be > 0")
        return v

    @field_validator("report_tier")
    @classmethod
    def validate_report_tier(cls, v):
        """Validate that report_tier is one of the allowed values."""
        valid_tiers = ["basic", "standard", "premium", "single_location_premium"]
        if v not in valid_tiers:
            raise ValueError(
                f"Invalid report_tier: '{v}'. "
                f"Must be one of: {', '.join(valid_tiers)}"
            )
        return v

    @field_validator("target_income_level")
    @classmethod
    def validate_target_income_level(cls, v):
        """Validate that target_income_level is one of the allowed values."""
        valid_targets = ["low", "medium", "high"]
        if v not in valid_targets:
            raise ValueError(
                f"Invalid target_income_level: '{v}'. "
                f"Must be one of: {', '.join(valid_targets)}"
            )
        return v

    @field_validator("target_age")
    @classmethod
    def validate_target_age(cls, v):
        """Validate that target_age is at least 1."""
        if v < 1:
            raise ValueError(
                f"Invalid target age: {v}. Target age must be 1 or greater."
            )
        return v

    @field_validator("delivery_weight", "dine_in_weight")
    @classmethod
    def validate_mode_weights(cls, v, info):
        """Validate that delivery_weight and dine_in_weight are between 0.0 and 1.0."""
        if v < 0.0 or v > 1.0:
            raise ValueError(
                f"{info.field_name} must be between 0.0 and 1.0, got {v}"
            )
        return v

    @model_validator(mode='after')
    def validate_single_location_logic(self):
        """
        Validate the location logic:
        - If single_location = True, custom_locations must have exactly one value
        - Otherwise, both custom_locations and current_location are optional
        """

        if self.single_location:
            if self.report_tier != "single_location_premium":
                raise ValueError(
                    f"When single_location set to True: "
                    f"report_tier must be 'single_location_premium', got '{self.report_tier}'"
                )

            if self.custom_locations is None or not self.custom_locations:
                raise ValueError(
                    "custom_locations is required when single_location set to True. "
                    "Please provide one location coordinate."
                )
            
            if not isinstance(self.custom_locations, list):
                raise ValueError(
                    "custom_locations must be a list when single_location set to True. "
                    f"Got type: {type(self.custom_locations).__name__}"
                )
            
            if len(self.custom_locations) == 0:
                raise ValueError(
                    "custom_locations cannot be empty when single_location set to True. "
                    "Please provide one location coordinate."
                )
        else:
            if self.report_tier == "single_location_premium":
                raise ValueError(
                    "report_tier 'single_location_premium' can only be used when single_location set to True"
                )

        return self

    @model_validator(mode='after')
    def validate_weight_sums(self):
        """Validate that category weights sum to 1.0 for both delivery and dine-in."""

        def check_weight_sum(weights, mode_name):
            total = sum(weights)
            if abs(total - 1.0) > 0.001:  # 0.1% tolerance
                weight_str = " + ".join(f"{w:.2f}" for w in weights)
                raise ValueError(
                    f"{mode_name} weights must sum to 1.0, got {total:.3f} ({weight_str})"
                )

        # Check delivery weights
        delivery_weights = [
            self.delivery_demographics_weight,
            self.delivery_competition_weight,
            self.delivery_complementary_weight,
            self.delivery_cross_shopping_weight,
            self.delivery_traffic_weight
        ]
        check_weight_sum(delivery_weights, "Delivery")

        # Check dine-in weights
        dine_in_weights = [
            self.dine_in_demographics_weight,
            self.dine_in_competition_weight,
            self.dine_in_complementary_weight,
            self.dine_in_cross_shopping_weight,
            self.dine_in_traffic_weight
        ]
        check_weight_sum(dine_in_weights, "Dine-in")

        return self


class ReqDriveTimePolyline(BaseModel):
    source: NonGeoStdPoint
    destination: NonGeoStdPoint


class ReqChat(BaseModel):
    question: str