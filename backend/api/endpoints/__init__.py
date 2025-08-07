from fastapi import APIRouter
from . import generate_chart, insight_analysis, ai_model_config, insight_analysis_stream

router = APIRouter()


router.include_router(generate_chart.router, prefix="/api", tags=["generate_chart"])
router.include_router(insight_analysis.router, prefix="/api", tags=["insight_analysis"])
router.include_router(ai_model_config.router, prefix="/api", tags=["ai_model_config"])
router.include_router(insight_analysis_stream.router, prefix="/api", tags=["insight_analysis_stream"])