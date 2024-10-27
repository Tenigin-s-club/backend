from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from typing import Annotated
from httpx import Headers

from app.utils import security, get_user_id_from_token
from app.db.configuration import get_session
from app.db.models import Order, User, Favorite
from app.schemas.favorites import SFavoritesAll, SFavoritesAdd
from app.config import settings, client
from app.schemas.train import STrainObject, STrainStorage, STrainWagonInfo, STrainAllWagon, STrainAllTrain


router = APIRouter(
    prefix="/train",
    tags=["train"]
)


@router.get("/wagon/{id}")
async def get_info_wagon(
    wagon_id: int,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ):
    link = "/api/info/wagons/{}"
    wagon_data = await client.get(settings.API_ADDRESS + link.format(wagon_id),
                                  headers=Headers({"Authorization": f"Bearer {authorization.credentials}"}))
    wagon_data = wagon_data.json()
    wagon_data = wagon_data["seats"]
    wagon_data.sort(key=lambda x: int(x["seatNum"]))    
    main_storage = []
    while wagon_data:                
        storage = []
        for _ in range(min(4, len(wagon_data))):
            storage.append(STrainObject(**(wagon_data.pop())))
            
        main_storage.append(STrainStorage(cupe=storage))
        
    return STrainWagonInfo(data=main_storage)


@router.get("/wagons")
async def get_all_wagons(
    train_id: int,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    wagons_link = "/api/info/wagons"
    wagons_data = await client.get(settings.API_ADDRESS + wagons_link + f"?trainId={train_id}", 
                                   headers=Headers({"Authorization": f"Bearer {authorization.credentials}"}))
    
    main_storage = []
    for wagon in wagons_data.json():
        wagon_data = wagon["seats"]
        wagon_data.sort(key=lambda x: int(x["seatNum"]))    
        wagon_storage = []
        while wagon_data:                
            storage = []
            for _ in range(min(4, len(wagon_data))):
                storage.append(STrainObject(**(wagon_data.pop())))
                
            wagon_storage.append(STrainStorage(cupe=storage))
            
        main_storage.append(STrainAllWagon(id=wagon["wagon_id"], wagon=wagon_storage))
        
    return STrainAllTrain(train=main_storage)
