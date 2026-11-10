from dataclasses import dataclass, field, asdict
from typing import List
import uuid


@dataclass
class Room:
    nummer: str = ""
    name: str = ""
    raumtyp: str = "Kühlraum"
    laenge: float = 0.0
    breite: float = 0.0
    hoehe: float = 0.0
    solltemperatur: float = 4.0
    umgebungstemperatur: float = 25.0
    u_wand: float = 0.4
    u_decke: float = 0.4
    u_boden: float = 0.4
    luftwechsel: float = 0.5
    innere_laste: float = 0.0
    sicherheitsfaktor: float = 10.0
    notizen: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        room = cls()
        for key, value in data.items():
            if hasattr(room, key):
                if key in ("name", "nummer", "raumtyp", "notizen"):
                    setattr(room, key, str(value))
                else:
                    try:
                        setattr(room, key, float(value))
                    except (TypeError, ValueError):
                        pass
        return room


@dataclass
class Project:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    nummer: str = ""
    kunde: str = ""
    adresse: str = ""
    bauvorhaben: str = ""
    ansprechpartner: str = ""
    datum: str = ""
    planungsstand: str = "In Planung"
    notizen: str = ""
    archiviert: bool = False
    raeume: List[Room] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "nummer": self.nummer,
            "kunde": self.kunde,
            "adresse": self.adresse,
            "bauvorhaben": self.bauvorhaben,
            "ansprechpartner": self.ansprechpartner,
            "datum": self.datum,
            "planungsstand": self.planungsstand,
            "notizen": self.notizen,
            "archiviert": self.archiviert,
            "raeume": [room.to_dict() for room in self.raeume],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        project = cls()
        for key in ("id", "name", "nummer", "kunde", "adresse", "bauvorhaben",
                    "ansprechpartner", "datum", "planungsstand", "notizen"):
            if key in data:
                setattr(project, key, str(data[key] or ""))
        project.archiviert = bool(data.get("archiviert", False))
        project.raeume = [Room.from_dict(r) for r in data.get("raeume", [])]
        return project

    def gesamtflaeche(self) -> float:
        return sum(r.laenge * r.breite for r in self.raeume)

    def gesamtvolumen(self) -> float:
        return sum(r.laenge * r.breite * r.hoehe for r in self.raeume)

    def gesamtleistung(self) -> float:
        from .calculation import berechne_kaelteleistung
        return sum(berechne_kaelteleistung(r)["gesamt"] for r in self.raeume)


def neuer_raum_standard() -> Room:
    return Room(nummer="", name="")
