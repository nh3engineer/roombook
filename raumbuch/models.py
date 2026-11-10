from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Room:
    nummer: str = ""
    name: str = ""
    raumtyp: str = "Lager"
    laenge: float = 0.0
    breite: float = 0.0
    hoehe: float = 0.0
    notizen: str = ""

    def flaeche(self) -> float:
        return self.laenge * self.breite

    def volumen(self) -> float:
        return self.flaeche() * self.hoehe

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        room = cls()
        for key, value in (data or {}).items():
            if hasattr(room, key):
                if key in ("nummer", "name", "raumtyp", "notizen"):
                    setattr(room, key, str(value))
                else:
                    try:
                        setattr(room, key, float(value))
                    except (TypeError, ValueError):
                        pass
        return room


@dataclass
class Zentrale:
    bezeichnung: str = ""
    medium: str = "NH3"
    leistung_kw: float = 0.0
    temperatur_c: float = 0.0
    notizen: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Zentrale":
        z = cls()
        for key, value in (data or {}).items():
            if hasattr(z, key):
                if key in ("bezeichnung", "medium", "notizen"):
                    setattr(z, key, str(value))
                else:
                    try:
                        setattr(z, key, float(value))
                    except (TypeError, ValueError):
                        pass
        return z


@dataclass
class Fuellmenge:
    medium: str = ""
    menge_kg: float = 0.0
    ort: str = ""
    notizen: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Fuellmenge":
        f = cls()
        for key, value in (data or {}).items():
            if hasattr(f, key):
                if key in ("medium", "ort", "notizen"):
                    setattr(f, key, str(value))
                else:
                    try:
                        setattr(f, key, float(value))
                    except (TypeError, ValueError):
                        pass
        return f


@dataclass
class Project:
    id: str = ""
    version: str = "Auslegung 1"
    name: str = ""
    nummer: str = ""
    kunde: str = ""
    adresse: str = ""
    bauvorhaben: str = ""
    ansprechpartner: str = ""
    datum: str = ""
    planungsstand: str = "In Planung"
    bearbeiter: str = ""
    notizen: str = ""
    raeume: List[Room] = field(default_factory=list)
    zentrale: List[Zentrale] = field(default_factory=list)
    fuellmengen: List[Fuellmenge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "nummer": self.nummer,
            "kunde": self.kunde,
            "adresse": self.adresse,
            "bauvorhaben": self.bauvorhaben,
            "ansprechpartner": self.ansprechpartner,
            "datum": self.datum,
            "planungsstand": self.planungsstand,
            "bearbeiter": self.bearbeiter,
            "notizen": self.notizen,
            "raeume": [r.to_dict() for r in self.raeume],
            "zentrale": [z.to_dict() for z in self.zentrale],
            "fuellmengen": [f.to_dict() for f in self.fuellmengen],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        p = cls()
        for key in ("id", "version", "name", "nummer", "kunde", "adresse",
                    "bauvorhaben", "ansprechpartner", "datum", "planungsstand",
                    "bearbeiter", "notizen"):
            if key in data:
                setattr(p, key, str(data[key] or ""))
        p.raeume = [Room.from_dict(r) for r in data.get("raeume", [])]
        p.zentrale = [Zentrale.from_dict(z) for z in data.get("zentrale", [])]
        p.fuellmengen = [Fuellmenge.from_dict(f) for f in data.get("fuellmengen", [])]
        return p

    def gesamtflaeche(self) -> float:
        return sum(r.flaeche() for r in self.raeume)

    def gesamtvolumen(self) -> float:
        return sum(r.volumen() for r in self.raeume)

    def gesamtleistung_kw(self) -> float:
        return sum(z.leistung_kw for z in self.zentrale)

    def gesamtmenge_kg(self) -> float:
        return sum(f.menge_kg for f in self.fuellmengen)
