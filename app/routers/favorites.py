from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from typing import Annotated

from app.utils import security, get_user_id_from_token
from app.db.configuration import get_session
from app.db.models import Order, User, Favorite
from app.schemas.favorites import SFavoritesAll, SFavoritesAdd


router = APIRouter(
    prefix="/favorites",
    tags=["favorites"]
)


@router.get("/all")
async def get_favorites(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> list[SFavoritesAll]:
    
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = select(Favorite.__table__.columns).filter_by(
        user_id=user_id
    )
    favorites = await session.execute(query)
    favorites = favorites.mappings().all()
    return [SFavoritesAll(**favorite) for favorite in favorites]
    

@router.post("/new", status_code=status.HTTP_204_NO_CONTENT)
async def add_favorites(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    favorite: SFavoritesAdd,
    session: AsyncSession = Depends(get_session)
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = insert(Favorite).values(
        user_id=user_id,
        **favorite.model_dump()
    )
    await session.execute(query)
    await session.commit()
    

@router.delete("/del/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    id: int,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> None:
    user_id =  await get_user_id_from_token(authorization.credentials, session)
    query = delete(Favorite).filter_by(user_id=user_id, id=id)
    await session.execute(query)
    await session.commit()