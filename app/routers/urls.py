from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Url, User
from app.schemas import UrlCreate, UrlResponse
from app.services.slug import generate_slug

router = APIRouter()


def to_response(url: Url, request: Request) -> UrlResponse:
    return UrlResponse(
        slug=url.slug,
        original_url=url.original_url,
        short_url=str(request.base_url) + url.slug,
    )


@router.post("/urls", response_model=UrlResponse, status_code=201)
def create_url(
    payload: UrlCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # no valid token = 401
):
    for _ in range(5):
        url = Url(
            slug=generate_slug(),
            original_url=str(payload.original_url),
            owner_id=current_user.id,
        )
        db.add(url)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(url)
        return to_response(url, request)
    raise HTTPException(status_code=500, detail="Could not generate a unique slug")


@router.get("/urls", response_model=list[UrlResponse])
def list_my_urls(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization: we only return links owned by the logged-in user.
    urls = db.scalars(
        select(Url)
        .where(Url.owner_id == current_user.id)
        .order_by(Url.created_at.desc())
    ).all()
    return [to_response(url, request) for url in urls]


@router.get("/{slug}")
def redirect_to_original(slug: str, db: Session = Depends(get_db)):
    # Public on purpose: anyone with a short link can follow it.
    url = db.scalar(select(Url).where(Url.slug == slug))
    if url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=url.original_url, status_code=307)