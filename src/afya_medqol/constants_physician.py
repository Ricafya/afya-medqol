"""Constants for the Afya MedQoL model (2024_2 calibration)."""

from __future__ import annotations

ITENS_F1 = [
    "F1_1_enjoymentoflife", "F1_2_financialsufficiency", "F1_3_accesstoinformation",
    "F1_4_leisureopportunities", "F1_5_mobilitypast2weeks", "F1_6_accesstohealthservices",
]
ITENS_F2 = [
    "F2_1_technicaltraining", "F2_2_mentalhealthsupport",
    "F2_3_coworkersupportnetwork", "F2_4_educationalhandlingoferrors",
]
ITENS_F3 = [
    "F3_1_stresshurtsperformance", "F3_2_stressledtoerrors", "F3_3_stresshurtsrelationships",
]
ITENS_TODOS = ITENS_F1 + ITENS_F2 + ITENS_F3

N_CATEGORIES = 5
N_GRID = 25

# Original questionnaire wording for each item, for display/reference purposes
# only — not used by the scoring pipeline itself. Keyed by item, then by
# language code ("en", "pt"), so both translations stay side by side and any
# missing translation is easy to spot.
ITEM_QUESTIONS = {
    "F1_1_enjoymentoflife": {
        "en": "28.3. To what extent do you enjoy life?",
        "pt": "28.3. O quanto você aproveita a vida?",
    },
    "F1_2_financialsufficiency": {
        "en": "29.3. Do you have sufficient financial resources to meet your personal needs?",
        "pt": "29.3. Você tem dinheiro suficiente para satisfazer suas necessidades?",
    },
    "F1_3_accesstoinformation": {
        "en": "29.4. To what degree is the information you need available to you in your daily life?",
        "pt": "29.4. Quão disponíveis para você estão as informações que precisa no seu dia-a-dia?",
    },
    "F1_4_leisureopportunities": {
        "en": "29.5. To what extent do you have opportunities to engage in leisure activities?",
        "pt": "29.5. Em que medida você tem oportunidades de atividade de lazer?",
    },
    "F1_5_mobilitypast2weeks": {
        "en": "30. How well are you able to get around over the past two weeks?",
        "pt": "30. Quão bem você é capaz de se locomover nas últimas duas semanas?",
    },
    "F1_6_accesstohealthservices": {
        "en": "31.9. How satisfied are you with your access to healthcare services?",
        "pt": "31.9. Quão satisfeito(a) você está com o seu acesso aos serviços de saúde?",
    },
    "F2_1_technicaltraining": {
        "en": "59.2. The institution where I work provides technical training to its staff.",
        "pt": "59.2. A instituição em que trabalho, oferece treinamento técnico a equipe.",
    },
    "F2_2_mentalhealthsupport": {
        "en": "59.3. The institution where I work offers support in cases of occupational mental illness or emotional distress.",
        "pt": "59.3. A instituição em que trabalho, oferece suporte em caso de psicoadoecimento adoecimento mental ou sofrimento emocional.",
    },
    "F2_3_coworkersupportnetwork": {
        "en": "59.4. At the institution where I work, I feel I can rely on a collegial support network from my coworkers.",
        "pt": "59.4. Na instituição em que trabalho, sinto que posso contar com uma rede de apoio de meus colegas de trabalho.",
    },
    "F2_4_educationalhandlingoferrors": {
        "en": "59.5. The institution where I work addresses errors or adverse events in care delivery through an educational rather than a punitive approach.",
        "pt": "59.5. A instituição em que trabalho, lida com o erro ou evento adverso na assistência com uma abordagem educativa ao invés de punitiva.",
    },
    "F3_1_stresshurtsperformance": {
        "en": "60.1. My stress level significantly impairs my professional performance at work.",
        "pt": "60.1. Meu nível de estresse compromete muito meu desempenho no trabalho.",
    },
    "F3_2_stressledtoerrors": {
        "en": "60.2. My stress level has previously led me to commit medical errors.",
        "pt": "60.2. Meu nível de estresse já me levou a erros médicos.",
    },
    "F3_3_stresshurtsrelationships": {
        "en": "60.3. My stress level adversely affects my interpersonal relationships outside the work environment.",
        "pt": "60.3. Meu nível de estresse compromete meu relacionamento fora do ambiente de trabalho.",
    },
}
