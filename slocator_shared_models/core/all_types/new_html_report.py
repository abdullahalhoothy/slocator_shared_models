from pydantic import BaseModel
from typing import Any, Optional, List, Union
from datetime import datetime, timedelta

# Components
class Accordion(BaseModel):
  # Icon is a font awesome icon like
  # fa-sliders-h
  icon: str
  title: str
  # Desc is the description
  desc: str
  # Colors represents a Tailwind Class like
  # from-indigo-50 to-purple-50 text-indigo-600
  colors: str

class Dropdown(BaseModel):
  icon: str
  title: str
  colors: str

# Header
# Section 01 - Blue rounded rectangle
class Header(BaseModel):
  city_name: str
  potential_business_type: str
  created_at: str
  delivery: int
  dine_in: int

# Customer Request Parameters
# Section 02 - Accordion that has a blue icon
class CustomerRequestParametersSectionData(BaseModel):
  key: str
  value: Any
  desc: str

class CustomerRequestParametersSection(BaseModel):
  icon: str
  title: str
  data: list[CustomerRequestParametersSectionData]

class CustomerRequestParameters(BaseModel):
  accordion: Accordion
  sections: list[CustomerRequestParametersSection]

# Market Research
# Section 03 - Accordion with a green icon

# Delivery & Dine In
class MarketResearchCard(BaseModel):
  icon: str
  title: str
  data: dict[str, Any]
  insight: str
  highlightColor: str
  insightColor: str
  colors: str

# Future Trends & Market Outlook
class MarketResearchTrends(BaseModel):
  icon: str
  title: str
  data: dict[str, Any]
  overall: str

# Verified Sources
class MarketResearchSources(BaseModel):
  note: str
  keypoints: list[str]

class MarketResearch(BaseModel):
  market_overview: str
  sources: MarketResearchSources
  cards: list[MarketResearchCard]
  trends: MarketResearchTrends
  accordion: Accordion

# Analysis Methodology
# Section 04 - Accordion with a purple icon
class AnalysisMethodologyScoringItem(BaseModel):
  icon: str
  title: str
  color: str
  lines: list[str]

class AnalysisMethodologyScoring(BaseModel):
  items: list[AnalysisMethodologyScoringItem]
  dropdown: Dropdown

class AnalysisMethodologyMetricsColumnRow(BaseModel):
  keyColor: Optional[str] = None
  key: str
  value: Any

class AnalysisMethodologyMetricsColumn(BaseModel):
  title: str
  rows: list[AnalysisMethodologyMetricsColumnRow]
  
class AnalysisMethodologyMetrics(BaseModel):
  columns: list[AnalysisMethodologyMetricsColumn]
  dropdown: Dropdown

class AnalysisMethodologyZonesItem(BaseModel):
  title: str
  subtitle: str
  containerColor: str
  titleColor: str

class AnalysisMethodologyZones(BaseModel):
  items: list[AnalysisMethodologyZonesItem]
  text: str
  dropdown: Dropdown

class AnalysisMethodology(BaseModel):
  accordion: Accordion
  text: str
  scoring: AnalysisMethodologyScoring
  metrics: AnalysisMethodologyMetrics
  zones: AnalysisMethodologyZones

# Executive Summary
# Section 5 - Text next to the candidates image
class ExecutiveSummaryPoint(BaseModel):
  num: int
  text: str
  numColor: str
  containerColor: str

class ExecutiveSummary(BaseModel):
  icon: str
  title: str
  image: str
  points: list[ExecutiveSummaryPoint]

# Recommendation Dashboard Grid
# Section 6 - The sites tab list and map grid
class RecommendationDashboardGridChild(BaseModel):
  value: Union[float, int]
  # if positive, display arrow up
  # if negative, display arrow down
  diff: Union[float, int]
  tooltip: str
  title: str
  multiplier: Optional[Union[int]] = None
  children: List['RecommendationDashboardGridChild'] = []

class RecommendationDashboardGridMapCategoryValue(BaseModel):
  class_name: Optional[str] = None
  color: Optional[str] = None
  title: str
  value: Optional[str] = None
  
class RecommendationDashboardGridMapCategory(BaseModel):
  title: str
  values: List[RecommendationDashboardGridMapCategoryValue]

class RecommendationDashboardGridMap(BaseModel):
  name: str
  final_score: Union[float, int]
  categories: List[RecommendationDashboardGridMapCategory]
  url: str

class RecommendationOverallAnalysisBadge(BaseModel):
  class_name: str
  icon: str
  text: str
  
class RecommendationOverallAnalysis(BaseModel):
  text: str
  badges: List[RecommendationOverallAnalysisBadge]
  
class RecommendationDashboardGridSite(BaseModel):
  values: List['RecommendationDashboardGridChild'] = []
  traffic_url: str
  visual_data: str
  source: str
  map: RecommendationDashboardGridMap
  price: Union[float,int]
  overall_analysis: RecommendationOverallAnalysis
  url: Optional[str]

class RecommendationDashboardGrid(BaseModel):
  sites: List['RecommendationDashboardGridSite'] = []

# Top 10 Rankings
# Section 7 - Table
class Top10RankingsTableItem(BaseModel):
  value: str
  arrowUp: Optional[bool]

class Top10RankingsTable(BaseModel):
  header: list[str]
  rows: list[list[Top10RankingsTableItem]]

class Top10RankingsSubTab(BaseModel):
  title: str
  icon: str
  tab_index: Optional[int]

class Top10RankingsTab(BaseModel):
  title: str
  icon: str
  sub_tabs: Optional[list[Top10RankingsSubTab]] = None
  tab_index: Optional[int] = None

class Top10Rankings(BaseModel):
  icon: str
  title: str
  subtitle: str
  tables: list[Top10RankingsTable] 
  static_columns: list[list[str]]
  clickable_columns: list[bool]
  tabs: list[Top10RankingsTab]

# Graphs
class GraphsImage(BaseModel):
  title: str
  url: str

class Graphs(BaseModel):
  title: str
  subtitle: str
  images: list[GraphsImage]
