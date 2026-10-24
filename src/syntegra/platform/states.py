"""The 36 states of Nigeria and the Federal Capital Territory (ISO 3166-2:NG), with each capital's LGA.

The capital LGA seeds the governance hierarchy when a state is provisioned; the state's full LGA list is
imported at onboarding (governance import), never hard-coded.
"""

from __future__ import annotations

# code, name, (capital LGA code, capital LGA name)
STATES: list[tuple[str, str, tuple[str, str]]] = [
    ("NG-AB", "Abia State", ("AB-UMN", "Umuahia North")),
    ("NG-AD", "Adamawa State", ("AD-YLN", "Yola North")),
    ("NG-AK", "Akwa Ibom State", ("AK-UYO", "Uyo")),
    ("NG-AN", "Anambra State", ("AN-AWS", "Awka South")),
    ("NG-BA", "Bauchi State", ("BA-BAU", "Bauchi")),
    ("NG-BY", "Bayelsa State", ("BY-YEN", "Yenagoa")),
    ("NG-BE", "Benue State", ("BE-MKD", "Makurdi")),
    ("NG-BO", "Borno State", ("BO-MAI", "Maiduguri")),
    ("NG-CR", "Cross River State", ("CR-CAL", "Calabar Municipal")),
    ("NG-DE", "Delta State", ("DE-OSS", "Oshimili South")),
    ("NG-EB", "Ebonyi State", ("EB-ABK", "Abakaliki")),
    ("NG-ED", "Edo State", ("ED-ORE", "Oredo")),
    ("NG-EK", "Ekiti State", ("EK-ADO", "Ado-Ekiti")),
    ("NG-EN", "Enugu State", ("EN-ENN", "Enugu North")),
    ("NG-FC", "Federal Capital Territory", ("FC-AMA", "Abuja Municipal")),
    ("NG-GO", "Gombe State", ("GO-GOM", "Gombe")),
    ("NG-IM", "Imo State", ("IM-OWM", "Owerri Municipal")),
    ("NG-JI", "Jigawa State", ("JI-DUT", "Dutse")),
    ("NG-KD", "Kaduna State", ("KD-KDN", "Kaduna North")),
    ("NG-KN", "Kano State", ("KN-KMC", "Kano Municipal")),
    ("NG-KT", "Katsina State", ("KT-KAT", "Katsina")),
    ("NG-KE", "Kebbi State", ("KE-BKB", "Birnin Kebbi")),
    ("NG-KO", "Kogi State", ("KO-LKJ", "Lokoja")),
    ("NG-KW", "Kwara State", ("KW-ILW", "Ilorin West")),
    ("NG-LA", "Lagos State", ("LA-IKJ", "Ikeja")),
    ("NG-NA", "Nasarawa State", ("NA-LAF", "Lafia")),
    ("NG-NI", "Niger State", ("NI-CHA", "Chanchaga")),
    ("NG-OG", "Ogun State", ("OG-ABS", "Abeokuta South")),
    ("NG-ON", "Ondo State", ("ON-AKS", "Akure South")),
    ("NG-OS", "Osun State", ("OS-OSG", "Osogbo")),
    ("NG-OY", "Oyo State", ("OY-IBN", "Ibadan North")),
    ("NG-PL", "Plateau State", ("PL-JSN", "Jos North")),
    ("NG-RI", "Rivers State", ("RI-PHC", "Port Harcourt")),
    ("NG-SO", "Sokoto State", ("SO-SKN", "Sokoto North")),
    ("NG-TA", "Taraba State", ("TA-JAL", "Jalingo")),
    ("NG-YO", "Yobe State", ("YO-DAM", "Damaturu")),
    ("NG-ZA", "Zamfara State", ("ZA-GUS", "Gusau")),
]
BY_CODE = {code: (name, capital) for code, name, capital in STATES}
assert len(STATES) == 37  # 36 states and the FCT

# Geopolitical zones (used by federal institutions, CR-005)
ZONES: dict[str, str] = {
    **dict.fromkeys(("NG-BE", "NG-KO", "NG-KW", "NG-NA", "NG-NI", "NG-PL", "NG-FC"), "north_central"),
    **dict.fromkeys(("NG-AD", "NG-BA", "NG-BO", "NG-GO", "NG-TA", "NG-YO"), "north_east"),
    **dict.fromkeys(("NG-JI", "NG-KD", "NG-KN", "NG-KT", "NG-KE", "NG-SO", "NG-ZA"), "north_west"),
    **dict.fromkeys(("NG-AB", "NG-AN", "NG-EB", "NG-EN", "NG-IM"), "south_east"),
    **dict.fromkeys(("NG-AK", "NG-BY", "NG-CR", "NG-DE", "NG-ED", "NG-RI"), "south_south"),
    **dict.fromkeys(("NG-EK", "NG-LA", "NG-OG", "NG-ON", "NG-OS", "NG-OY"), "south_west"),
}
assert len(ZONES) == 37
