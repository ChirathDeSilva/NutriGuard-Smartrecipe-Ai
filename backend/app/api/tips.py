"""
TIPS & NEWS API ROUTE: Curated Nutrition Tips & Food Safety News
===============================================================
Exposes GET /api/tips and GET /api/tips/{id} endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import NutritionTip
from backend.app.db.schemas import NutritionTipResponse, NutritionTipCreate

router = APIRouter(tags=["Nutrition Tips & News"])


@router.get("/tips", response_model=List[NutritionTipResponse])
def get_tips(
    category: Optional[str] = Query(None, description="Filter by category ('tip' or 'news')"),
    tag: Optional[str] = Query(None, description="Filter by tag keyword"),
    db: Session = Depends(get_db)
):
    """
    Retrieves all published nutrition tips and food safety news articles.
    """
    query = db.query(NutritionTip).filter(NutritionTip.is_published == True)

    if category:
        query = query.filter(NutritionTip.category == category.lower().strip())

    if tag:
        query = query.filter(NutritionTip.tags.like(f"%{tag.lower().strip()}%"))

    tips = query.order_by(NutritionTip.created_at.desc()).all()
    return tips


@router.get("/tips/{tip_id}", response_model=NutritionTipResponse)
def get_tip_by_id(tip_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single nutrition tip or news article by its ID.
    """
    tip = db.query(NutritionTip).filter(NutritionTip.id == tip_id, NutritionTip.is_published == True).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Nutrition tip or article not found.")
    return tip


@router.post("/tips", response_model=NutritionTipResponse, status_code=201)
def create_tip(tip_in: NutritionTipCreate, db: Session = Depends(get_db)):
    """
    Creates a new nutrition tip or food safety news entry.
    """
    new_tip = NutritionTip(
        title=tip_in.title,
        summary=tip_in.summary,
        content=tip_in.content,
        category=tip_in.category,
        author=tip_in.author,
        image_url=tip_in.image_url,
        tags=tip_in.tags,
        is_published=True
    )
    db.add(new_tip)
    db.commit()
    db.refresh(new_tip)
    return new_tip
