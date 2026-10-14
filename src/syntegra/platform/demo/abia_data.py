"""Reference data for the Abia State demonstration dataset (``syntegra_demo_abia``).

The 17 local government areas and their towns are real; every school, person and score generated from them is
synthetic demonstration data for end-to-end testing and must never be mistaken for a real record.
"""

from __future__ import annotations

# code, name, towns (one school of each kind per town), urban (affects the synthetic quality bias)
LGAS: list[tuple[str, str, tuple[str, ...], bool]] = [
    ("AB-ABN", "Aba North", ("Eziama", "Ogbor Hill", "Osusu", "Umuola", "Old Aba GRA"), True),
    ("AB-ABS", "Aba South", ("Ohanku", "Eziukwu", "Ndiegoro", "Asa Road", "Ngwa Road"), True),
    ("AB-ARO", "Arochukwu", ("Arochukwu", "Ihechiowa", "Ohafor", "Utuga", "Isu"), False),
    ("AB-BEN", "Bende", ("Bende", "Uzuakoli", "Item", "Igbere", "Alayi"), False),
    ("AB-IKW", "Ikwuano", ("Isiala Oboro", "Ariam", "Usaka", "Oloko", "Umudike"), False),
    ("AB-ISN", "Isiala Ngwa North", ("Okpuala Ngwa", "Umuoha", "Nsulu", "Amapu", "Mbawsi"), False),
    ("AB-ISS", "Isiala Ngwa South", ("Omoba", "Ovungwu", "Mbutu", "Owerrinta", "Ngwaukwu"), False),
    ("AB-ISU", "Isuikwuato", ("Mbalano", "Uturu", "Ovim", "Amaba", "Imenyi"), False),
    ("AB-OBN", "Obi Ngwa", ("Mgboko", "Umuobiala", "Okpulo", "Umunnato", "Ntigha"), False),
    ("AB-OHF", "Ohafia", ("Ebem Ohafia", "Abiriba", "Nkporo", "Amaeke", "Asaga"), False),
    ("AB-OSI", "Osisioma Ngwa", ("Osisioma", "Umuojima", "Amaitolu", "Okpu Umuobo", "Umuode"), True),
    ("AB-UGW", "Ugwunagbo", ("Ugwunagbo", "Obegu", "Ayaba", "Umuogele", "Ihie"), False),
    ("AB-UKE", "Ukwa East", ("Akwete", "Ohambele", "Obohia", "Ikwuorie", "Ohanso"), False),
    ("AB-UKW", "Ukwa West", ("Oke Ikpe", "Ipu", "Obokwe", "Ozaa", "Asa"), False),
    ("AB-UMN", "Umuahia North", ("Umuahia", "Ibeku", "Afugiri", "Isingwu", "Umuawa"), True),
    ("AB-UMS", "Umuahia South", ("Apumiri", "Ubakala", "Olokoro", "Umuopara", "Nsirimo"), True),
    ("AB-UMU", "Umu Nneochi", ("Isuochi", "Umuchieze", "Lekwesi", "Ndiwo", "Mbala"), False),
]
# approximate centre of each LGA (lat, lon) for synthetic school locations
CENTRES: dict[str, tuple[float, float]] = {
    "AB-ABN": (5.12, 7.37), "AB-ABS": (5.10, 7.36), "AB-ARO": (5.39, 7.91), "AB-BEN": (5.56, 7.63),
    "AB-IKW": (5.43, 7.57), "AB-ISN": (5.38, 7.38), "AB-ISS": (5.30, 7.38), "AB-ISU": (5.82, 7.47),
    "AB-OBN": (5.18, 7.42), "AB-OHF": (5.62, 7.83), "AB-OSI": (5.15, 7.33), "AB-UGW": (5.03, 7.32),
    "AB-UKE": (4.92, 7.53), "AB-UKW": (4.87, 7.30), "AB-UMN": (5.53, 7.49), "AB-UMS": (5.45, 7.47),
    "AB-UMU": (5.95, 7.40),
}  # fmt: skip

PRIMARY_NAMES = ("Community Primary School", "Central School", "Town School", "Model Primary School", "Primary School")
SECONDARY_NAMES = (
    "Government Secondary School",
    "Community Secondary School",
    "Girls' Secondary School",
    "Comprehensive Secondary School",
    "Boys' High School",
)

MALE = (
    "Chukwuemeka", "Chinedu", "Obinna", "Ikenna", "Nnamdi", "Emeka", "Uchenna", "Chidi", "Kelechi", "Ifeanyi",
    "Somtochukwu", "Chibuike", "Ebuka", "Kosisochukwu", "Tochukwu", "Chukwudi", "Nonso", "Ugochukwu", "Onyekachi",
    "Chimezie", "Kenechukwu", "Ikechukwu", "Okechukwu", "Azubuike", "Ekene", "Chiemelie", "David", "Daniel",
    "Samuel", "Michael", "Emmanuel", "Victor", "Joshua", "Godswill", "Chijioke", "Munachimso", "Ebube", "Kamsiyochukwu",
)  # fmt: skip
FEMALE = (
    "Chiamaka", "Ngozi", "Adaeze", "Chioma", "Nneka", "Ifeoma", "Uchechi", "Amarachi", "Chidinma", "Obiageli",
    "Ebere", "Ogechi", "Kosisochi", "Somadina", "Ozioma", "Ijeoma", "Nkechi", "Onyinyechi", "Ugochi", "Chinwe",
    "Adanna", "Munachi", "Chisom", "Esther", "Mercy", "Blessing", "Grace", "Joy", "Peace", "Precious", "Miracle",
    "Favour", "Chinaza", "Ezinne", "Nmesoma", "Oluchi", "Ujunwa", "Kambili",
)  # fmt: skip
FAMILY = (
    "Okafor", "Okonkwo", "Nwosu", "Eze", "Okeke", "Nwachukwu", "Nwankwo", "Okoro", "Ibe", "Agu", "Kalu", "Uzor",
    "Onwuka", "Nnadi", "Ogbonna", "Ezeh", "Chukwu", "Obi", "Udeh", "Mba", "Oti", "Nwaogu", "Ukaegbu", "Nwokocha",
    "Ihejirika", "Onyeama", "Igwe", "Orji", "Ogbu", "Nwoke", "Iroegbu", "Anyanwu", "Emenike", "Ndukwe", "Nwogu",
    "Ekeh", "Uduma", "Ofoegbu", "Okorie", "Ubani", "Ekwueme", "Kanu", "Ezeani", "Onuoha", "Chikere", "Nwaigwe",
    "Amadi", "Ahamba", "Otuonye", "Nwala", "Egwu", "Mbakwe", "Nwadike", "Akpa", "Arua", "Uka", "Okwara", "Ezenwa",
    "Iheanacho", "Nwagwu", "Ogwo", "Onyekwere", "Enyinnaya", "Nwangwu", "Ukandu", "Ezike", "Kalu-Uka", "Agbai",
)  # fmt: skip
TITLES_M, TITLES_F = ("Mr", "Chief", "Engr", "Dr", "Elder"), ("Mrs", "Lolo", "Dr", "Barr", "Deaconess")

# subjects: code, name, levels
PRIMARY_LEVELS = ("PRY1", "PRY2", "PRY3", "PRY4", "PRY5", "PRY6")
SECONDARY_LEVELS = ("JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3")
SUBJECTS: list[tuple[str, str, tuple[str, ...]]] = [
    ("ENG", "English Studies / English Language", PRIMARY_LEVELS + SECONDARY_LEVELS),
    ("MTH", "Mathematics", PRIMARY_LEVELS + SECONDARY_LEVELS),
    ("BST", "Basic Science and Technology", PRIMARY_LEVELS + ("JSS1", "JSS2", "JSS3")),
    ("NVE", "National Values Education", PRIMARY_LEVELS),
    ("IGB", "Igbo Language", PRIMARY_LEVELS + SECONDARY_LEVELS),
    ("CIV", "Civic Education", SECONDARY_LEVELS),
    ("BIO", "Biology", ("SSS1", "SSS2", "SSS3")),
]
PRIMARY_SUBJECTS = ("ENG", "MTH", "BST", "NVE", "IGB")
JSS_SUBJECTS = ("ENG", "MTH", "BST", "CIV", "IGB")
SSS_SUBJECTS = ("ENG", "MTH", "BIO", "CIV", "IGB")
SUBJECT_BIAS = {"ENG": 1.5, "MTH": -4.0, "BST": 0.0, "NVE": 3.0, "IGB": 2.0, "CIV": 2.5, "BIO": -1.5}
# age at the start of the session for each level
AGE = {"PRY1": 6, "PRY2": 7, "PRY3": 8, "PRY4": 9, "PRY5": 10, "PRY6": 11,
       "JSS1": 12, "JSS2": 13, "JSS3": 14, "SSS1": 15, "SSS2": 16, "SSS3": 17}  # fmt: skip

# ---------------------------------------------------------------- tertiary
# institution key → (name, short name, category, LGA, town, levels, (lat, lon))
TERTIARY = {
    "ABSU": (
        "Abia State University, Uturu",
        "ABSU",
        "university",
        "AB-ISU",
        "Uturu",
        ("UG100", "UG200", "UG300", "UG400", "UG500", "UG600", "PG"),
        (5.83, 7.43),
    ),
    "ASCETA": (
        "Abia State College of Education (Technical), Arochukwu",
        "ASCETA",
        "college_of_education",
        "AB-ARO",
        "Arochukwu",
        ("NCE",),
        (5.39, 7.92),
    ),
}
# faculty (or school) → departments: (programme code, programme name, department name, terms)
FACULTIES = {
    "ABSU": {
        ("FBPS", "Faculty of Biological and Physical Sciences"): [
            ("CSC", "B.Sc. Computer Science", "Department of Computer Science", 8),
            ("BCH", "B.Sc. Biochemistry", "Department of Biochemistry", 8),
        ],
        ("FBA", "Faculty of Business Administration"): [
            ("ACC", "B.Sc. Accountancy", "Department of Accountancy", 8),
            ("BFN", "B.Sc. Banking and Finance", "Department of Banking and Finance", 8),
        ],
        ("FEES", "Faculty of Engineering and Environmental Studies"): [
            ("CVE", "B.Eng. Civil Engineering", "Department of Civil Engineering", 10),
            ("EEE", "B.Eng. Electrical/Electronic Engineering", "Department of Electrical/Electronic Engineering", 10),
        ],
        ("FLAW", "Faculty of Law"): [("LAW", "LL.B. Law", "Department of Public and Private Law", 10)],
        ("CMHS", "College of Medicine and Health Sciences"): [
            ("MED", "MBBS Medicine and Surgery", "Department of Medicine and Surgery", 12),
            ("NSC", "B.N.Sc. Nursing Science", "Department of Nursing Science", 10),
        ],
        ("FSS", "Faculty of Social Sciences"): [
            ("ECO", "B.Sc. Economics", "Department of Economics", 8),
            ("MAC", "B.Sc. Mass Communication", "Department of Mass Communication", 8),
        ],
        ("FAG", "Faculty of Agriculture"): [
            ("AEC", "B.Agric. Agricultural Economics", "Department of Agricultural Economics", 10)
        ],
    },
    "ASCETA": {
        ("SVTE", "School of Vocational and Technical Education"): [
            (
                "TEE",
                "NCE Technical Education (Electrical/Electronics)",
                "Department of Electrical/Electronics Education",
                6,
            ),
            ("TEB", "NCE Technical Education (Building)", "Department of Building Technology Education", 6),
        ],
        ("SSC", "School of Sciences"): [
            ("CSE", "NCE Computer Science Education", "Department of Computer Science Education", 6),
            ("ISC", "NCE Integrated Science", "Department of Integrated Science", 6),
        ],
        ("SASS", "School of Arts and Social Sciences"): [
            ("ENG", "NCE English Language", "Department of English", 6),
            ("ECN", "NCE Economics", "Department of Economics", 6),
        ],
        ("SED", "School of Education"): [
            ("PES", "NCE Primary Education Studies", "Department of Primary Education", 6)
        ],
    },
}
# three first-semester courses per programme (generic titles by programme)
COURSES = ("Foundations of the discipline", "Quantitative methods", "Use of English and communication")

# academic staff ranks: (rank title, grade level) — CONTISS-style, illustrative
UNIVERSITY_RANKS = (("Professor", 15), ("Reader", 14), ("Senior Lecturer", 13), ("Lecturer I", 12),
                    ("Lecturer II", 11), ("Assistant Lecturer", 9), ("Graduate Assistant", 8))  # fmt: skip
COLLEGE_RANKS = (("Chief Lecturer", 14), ("Principal Lecturer", 13), ("Senior Lecturer", 12), ("Lecturer I", 11),
                 ("Lecturer II", 10), ("Lecturer III", 9))  # fmt: skip
SUPPORT_POSTS = (("Registry Officer", 8), ("Accountant", 9), ("Laboratory Technologist", 8), ("Librarian", 10),
                 ("Executive Officer", 7), ("Secretary", 6), ("Driver", 4), ("Security Officer", 4),
                 ("ICT Officer", 8), ("Works Officer", 7))  # fmt: skip
