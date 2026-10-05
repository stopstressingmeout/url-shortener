from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Url
from app.schemas import UrlCreate,UrlResponse
from app.services.slug import generate_slug

router=APIRouter()

@router.post("/urls",response_model=UrlResponse,status_code=201)
def create_url(payload:UrlCreate,request:Request,db:Session=Depends(get_db)):
    for _ in range(5):
        url=Url(slug=generate_slug(),original_url=str(payload.original_url))
        db.add(url)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(url)
        return UrlResponse(
            slug=url.slug,
            original_url=url.original_url,
            short_url=str(request.base_url) + url.slug,
        )
    raise HTTPException(status_code=500,detail="Could not generate a unique slug")

@router.get("/{slug}")
def redirect_to_original(slug:str,db:Session=Depends(get_db)):
    url=db.scalar(select(Url).where(Url.slug==slug))
    if url is None:
        raise HTTPException(status_code=404,detail="Short URL not found")
    return RedirectResponse(url.original_url,status_code=307)
