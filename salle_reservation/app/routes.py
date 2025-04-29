import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database

router = APIRouter()

# Vérification via API que la salle existe
async def verifier_salle_existe(salle_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://salle_service:8001/salles/{salle_id}')
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Salle non trouvée")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service des salles indisponible")

# Route POST pour créer une réservation
@router.post("/reservations/", response_model= schemas.ReservationOut)
async def reserver_salle(
    reservation: schemas.ReservationCreate,
    db: Session = Depends(database.get_db)
):
    # Vérifier que la salle existe via le microservice de salle
    await verifier_salle_existe(reservation.salle_id)

    # Vérifier qu'il n'y a pas de conflit de réservation
    conflit = db.query(models.Reservation).filter(
        models.Reservation.salle_id == reservation.salle_id,
        models.Reservation.debut < reservation.fin,
        models.Reservation.fin > reservation.debut
    ).first()

    if conflit:
        raise HTTPException(status_code=409, detail="Salle déjà réservée pour ce créneau")

    # Créer et enregistrer la réservation
    nouvelle_reservation = models.Reservation(
        user_id=reservation.user_id,
        salle_id=reservation.salle_id,
        debut=reservation.debut,
        fin=reservation.fin
    )

    db.add(nouvelle_reservation)
    db.commit()
    db.refresh(nouvelle_reservation)

    return nouvelle_reservation
