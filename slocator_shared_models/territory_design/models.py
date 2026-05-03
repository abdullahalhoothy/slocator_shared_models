from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Location(BaseModel):
    id: str
    name: str
    lat: float
    lng: float


# ── GeoJSON input models (FeatureCollection from server 1) ───────────────────

class GeoJsonGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJsonFeature(BaseModel):
    type: str = "Feature"
    properties: dict[str, Any] = {}
    geometry: GeoJsonGeometry


class LocationFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJsonFeature] = []


class TerritoryRequest(BaseModel):
    user_id: str = "anonymous"
    locations: LocationFeatureCollection
    num_groups: int
    group_size: int
    outlier_cut_km: float
    centroid_lat: float
    centroid_lng: float
    group_size_prune_max: float
    max_solving_time: float


class Group(BaseModel):
    num_locations: int
    centroid_lat: float
    centroid_lng: float
    avg_dist_to_centroid: float
    locations: list[Location]


# ── Territory FeatureCollection response ─────────────────────────────────────

class TerritoryGroupMeta(BaseModel):
    group_index: int
    num_locations: int
    centroid_lat: float
    centroid_lng: float
    avg_dist_to_centroid: float


class TerritoryFeatureResponse(BaseModel):
    type: str = "FeatureCollection"
    features: list[dict[str, Any]] = []
    running_time: float
    records_count: int
    groups_metadata: list[TerritoryGroupMeta] = []
    shops_map_url: str = ""
    clusters_map_url: str = ""
    shops_xlsx_url: str = ""
    shops_json_url: str = ""


class TerritoryResponse(BaseModel):
    running_time: float
    groups: list[Group]


# ── VRP models ────────────────────────────────────────────────────────────────

class DriverPosition(BaseModel):
    lat: float
    lng: float


class VRPGroup(Group):
    """Group extended with an optional driver start/end position."""
    driver_start: DriverPosition | None = None


class VRPRequest(BaseModel):
    running_time: float
    groups: list[VRPGroup]
    num_work_days: int = 12
    # Extended fields for combined VRP+report response
    user_id: str
    locations: LocationFeatureCollection = LocationFeatureCollection()
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


class VRPRoute(BaseModel):
    route_index: int
    locations: list[Location]
    total_time_seconds: float
    gmap_links: list[str]


class ClusterVRP(BaseModel):
    cluster_index: int
    centroid_lat: float
    centroid_lng: float
    driver_start_lat: float
    driver_start_lng: float
    num_routes: int
    time_matrix_source: str
    routes: list[VRPRoute]


class VRPResponse(BaseModel):
    running_time: float
    clusters: list[ClusterVRP]


# ── VRP FeatureCollection response (with savings + file URLs) ─────────────────

class SavingItemOut(BaseModel):
    label: str
    before_value: float
    after_value: float
    diff_value: float
    unit: str
    per_day_sar: float
    per_2_weeks_sar: float
    per_month_sar: float
    note: str = ""


class SavingsBreakdownOut(BaseModel):
    num_drivers: int
    num_work_days: int
    total_stops_planned: int
    gas_per_km_sar: float
    driver_hourly_sar: float
    planner_hourly_sar: float
    current_daily_km_fleet: float
    planned_daily_km_fleet: float
    delta_daily_km_fleet: float
    current_road_h_per_driver_day: float
    planned_road_h_per_driver_day_avg: float
    delta_road_h_fleet_per_day: float
    current_visits_per_day_fleet: int
    planned_visits_per_day_fleet: float
    delta_visits_per_day_fleet: float
    items: list[SavingItemOut] = []
    total_per_day_sar: float
    total_per_2_weeks_sar: float
    total_per_month_sar: float


class VRPFeatureResponse(BaseModel):
    type: str = "FeatureCollection"
    features: list[dict[str, Any]] = []
    running_time: float
    records_count: int
    savings: SavingsBreakdownOut
    excel_url: str
    html_url: str
    pdf_url: str = ""
    routes_map_url: str = ""
    shops_map_url: str = ""
    clusters_map_url: str = ""
    shops_xlsx_url: str = ""
    shops_json_url: str = ""


# ── Report models ─────────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    locations: list[Location]
    vrp: VRPResponse

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
