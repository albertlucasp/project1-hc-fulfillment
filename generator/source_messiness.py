from datetime import date
import random

from generator.config import SOURCE_MESSINESS_RATE


GENDER_VARIANTS = {
    "Male": ["Male", "M", "L", "LAKI-LAKI", "Laki-laki"],
    "Female": ["Female", "F", "P", "PEREMPUAN", "Perempuan"],
}

JOB_TITLE_VARIANTS = {
    "Manager": ["Manager", "Mgr", "MANAGER"],
    "Assistant Manager": ["Assistant Manager", "Asst Manager", "ASSISTANT MANAGER"],
    "Team Leader": ["Team Leader", "TL", "TEAM LEADER"],
    "Supervisor": ["Supervisor", "Spv", "SUPERVISOR"],
    "Coordinator": ["Coordinator", "Coord", "COORDINATOR"],
    "Senior Staff": ["Senior Staff", "Sr Staff", "SENIOR STAFF"],
    "Junior Staff": ["Junior Staff", "Jr Staff", "JUNIOR STAFF"],
    "Associate Staff": ["Associate Staff", "Assoc Staff", "ASSOCIATE STAFF"],
}


def maybe_blank(value: object, rng: random.Random, rate: float | None = None) -> object:
    if value in (None, ""):
        return value
    if rng.random() < (SOURCE_MESSINESS_RATE if rate is None else rate):
        return ""
    return value


def messy_date(value: date | None, rng: random.Random, blank_rate: float = 0.0) -> str:
    if value is None:
        return ""
    if rng.random() < blank_rate:
        return ""

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%d.%m.%Y",
    ]
    weights = [0.65, 0.18, 0.12, 0.05]
    return value.strftime(rng.choices(formats, weights=weights, k=1)[0])


def messy_gender(value: str, rng: random.Random) -> str:
    variants = GENDER_VARIANTS.get(value, [value])
    if rng.random() < SOURCE_MESSINESS_RATE * 2:
        return rng.choice(variants)
    return value


def messy_job_title(value: str, rng: random.Random) -> str:
    variants = JOB_TITLE_VARIANTS.get(value)
    if variants and rng.random() < SOURCE_MESSINESS_RATE:
        return rng.choice(variants)
    if rng.random() < SOURCE_MESSINESS_RATE / 3:
        return value.upper()
    return value


def messy_org_name(value: str, rng: random.Random) -> str:
    if rng.random() >= SOURCE_MESSINESS_RATE:
        return value

    text = value.replace("Sub Branch", "Sub-Branch")
    text = text.replace("Branch", "Br")
    if rng.random() < 0.35:
        return text.upper()
    return text
