LUFTDICHTE = 1.2
LUFT_SPEZIFISCHE_WAERME = 1006.0


def raumgeometrie(room) -> dict:
    flaeche = room.laenge * room.breite
    volumen = flaeche * room.hoehe
    wandflaeche = 2 * (room.laenge + room.breite) * room.hoehe
    deckenflaeche = flaeche
    bodenflaeche = flaeche
    return {
        "flaeche": flaeche,
        "volumen": volumen,
        "wandflaeche": wandflaeche,
        "deckenflaeche": deckenflaeche,
        "bodenflaeche": bodenflaeche,
    }


def berechne_kaelteleistung(room) -> dict:
    geo = raumgeometrie(room)
    delta_t = room.umgebungstemperatur - room.solltemperatur

    q_transmission = (
        room.u_wand * geo["wandflaeche"]
        + room.u_decke * geo["deckenflaeche"]
        + room.u_boden * geo["bodenflaeche"]
    ) * delta_t

    q_lueftung = (
        geo["volumen"] * room.luftwechsel / 3600.0
        * LUFTDICHTE * LUFT_SPEZIFISCHE_WAERME * delta_t
    )

    q_innere = room.innere_laste

    zwischensumme = q_transmission + q_lueftung + q_innere
    gesamt = zwischensumme * (1.0 + room.sicherheitsfaktor / 100.0)

    return {
        "flaeche": geo["flaeche"],
        "volumen": geo["volumen"],
        "delta_t": delta_t,
        "transmission": q_transmission,
        "lueftung": q_lueftung,
        "innere": q_innere,
        "zwischensumme": zwischensumme,
        "gesamt": gesamt,
    }


def formel_erklaerung(room) -> str:
    geo = raumgeometrie(room)
    return (
        "So rechnet das Raumbuch:\n\n"
        "1. Transmissionslast (Wärme durch Bauteile):\n"
        "   Q_T = (U_Wand x A_Wand + U_Decke x A_Decke + U_Boden x A_Boden) x Delta-T\n"
        f"   A_Wand = 2 x (Länge + Breite) x Höhe = {geo['wandflaeche']:.2f} m²\n"
        f"   A_Decke = A_Boden = Länge x Breite = {geo['deckenflaeche']:.2f} m²\n"
        f"   Delta-T = {room.umgebungstemperatur:.1f} °C - {room.solltemperatur:.1f} °C\n\n"
        "2. Lüftungslast (Luftaustausch/Infiltration):\n"
        "   Q_L = (Volumen x Luftwechsel / 3600) x 1,2 kg/m³ x 1006 J/(kg·K) x Delta-T\n\n"
        "3. Interne Lasten (Menscher, Geräte, Prozesse) in Watt\n\n"
        "4. Gesamt = (Q_T + Q_L + interne Lasten) x (1 + Sicherheitsfaktor / 100)\n\n"
        "Alle Werte basieren auf Ihrer Eingabe im Raumformular."
    )
