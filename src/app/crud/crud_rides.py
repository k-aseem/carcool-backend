from fastcrud import FastCRUD

from ..models.ride import Ride
from ..schemas.ride import RideRead, RideCreate, RideUpdate, RideDelete

CRUDRide = FastCRUD[Ride, RideRead, RideCreate, RideUpdate, RideDelete]
crud_ride = CRUDRide(Ride)
