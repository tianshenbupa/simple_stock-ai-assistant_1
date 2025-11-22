from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StockAnalysisRequest(BaseModel):
    stock_ticker: str = Field(..., description="股票代码")
    query: str = Field(..., description="分析问题")

class StockAnalysisResponse(BaseModel):
    stock_ticker: str
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)
    analysis: str
    recommendation: Optional[str] = None
    target_price: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"