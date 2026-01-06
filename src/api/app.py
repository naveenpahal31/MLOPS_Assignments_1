"""
FastAPI application for Heart Disease Prediction Model Serving.

Provides REST API endpoints for model inference.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import numpy as np

from src.models.load_model import load_best_model
from src.data.preprocessing import get_feature_names

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Heart Disease Prediction API",
    description="MLOps API for predicting heart disease risk",
    version="1.0.0"
)

# Global model loader (loaded on startup)
model_loader = None


class HeartDiseaseInput(BaseModel):
    """Input schema for heart disease prediction."""
    age: float = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (1=male, 0=female)")
    cp: int = Field(..., ge=1, le=4, description="Chest pain type (1-4)")
    trestbps: float = Field(..., ge=0, description="Resting blood pressure")
    chol: float = Field(..., ge=0, description="Serum cholesterol")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 (1=true, 0=false)")
    restecg: int = Field(..., ge=0, le=2, description="Resting electrocardiographic results")
    thalach: float = Field(..., ge=0, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina (1=yes, 0=no)")
    oldpeak: float = Field(..., ge=0, description="ST depression induced by exercise")
    slope: int = Field(..., ge=1, le=3, description="Slope of peak exercise ST segment")
    ca: int = Field(..., ge=0, le=3, description="Number of major vessels colored by flourosopy")
    thal: int = Field(..., ge=3, le=7, description="Thalassemia (3=normal, 6=fixed, 7=reversible)")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 63,
                "sex": 1,
                "cp": 1,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 2,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.3,
                "slope": 3,
                "ca": 0,
                "thal": 6
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for prediction."""
    prediction: int = Field(..., description="Prediction (0=No Disease, 1=Disease Present)")
    prediction_label: str = Field(..., description="Human-readable prediction label")
    probability: float = Field(..., ge=0, le=1, description="Probability of disease")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    message: str


@app.on_event("startup")
async def load_model():
    """Load model on application startup."""
    global model_loader
    try:
        logger.info("Loading model on startup...")
        model_loader = load_best_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.warning("API will start without model. Train models first using: python src/models/train.py")
        model_loader = None
        # Don't raise - allow API to start, health check will indicate status


@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    if model_loader is None:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            message="Model not loaded"
        )
    
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        message="API is ready to serve predictions"
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(input_data: HeartDiseaseInput):
    """
    Predict heart disease risk.
    
    Accepts patient health data and returns prediction with confidence.
    """
    if model_loader is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check /health endpoint."
        )
    
    try:
        # Log request
        logger.info(f"Prediction request received: {input_data.dict()}")
        
        # Convert input to dictionary
        input_dict = input_data.dict()
        
        # Make prediction
        result = model_loader.predict_single(**input_dict)
        
        # Log prediction
        logger.info(
            f"Prediction made: {result['prediction_label']} "
            f"(probability: {result['probability']:.4f})"
        )
        
        return PredictionResponse(**result)
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", tags=["Prediction"])
async def predict_batch(inputs: List[HeartDiseaseInput]):
    """
    Batch prediction endpoint.
    
    Accepts multiple patient records and returns predictions for all.
    """
    if model_loader is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check /health endpoint."
        )
    
    try:
        logger.info(f"Batch prediction request received: {len(inputs)} samples")
        
        results = []
        for input_data in inputs:
            input_dict = input_data.dict()
            result = model_loader.predict_single(**input_dict)
            results.append(result)
        
        logger.info(f"Batch prediction completed: {len(results)} predictions")
        
        return {
            "predictions": results,
            "count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/model/info", tags=["Model"])
async def model_info():
    """Get information about the loaded model."""
    if model_loader is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    info = {
        "model_name": model_loader.model_name,
        "model_type": type(model_loader.model).__name__,
        "preprocessor_loaded": model_loader.preprocessor is not None,
    }
    
    if model_loader.model_info:
        info["training_metrics"] = model_loader.model_info
    
    return info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

