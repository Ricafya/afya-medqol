"""Constants for the Afya MedQoL Student model (medical students, 8 items, bifactor)."""

from __future__ import annotations

STUDENT_ITEMS = [
    "F1_1_overallqol", "F1_2_satisfactionwithhealth", "F1_3_enjoymentoflife", "F1_4_perceivedmeaninginlife", "F2_1_energyfordailyactivities", "F2_2_satisfactionwithsleep", "F3_1_performdailyactivities", "F3_2_capacityforwork",
]

N_CATEGORIES_STUDENT = 5
N_GRID_STUDENT = 121
GRID_LIMIT_STUDENT = 6.0

MISSING_CODE_STUDENT = 999

# Original questionnaire wording for each item, for display/reference purposes
# only — not used by the scoring pipeline itself. Keyed by item, then by
# language code ("en", "pt"), so both translations stay side by side and any
# missing translation is easy to spot.
ITEM_QUESTIONS = {
    "F1_1_overallqol": {
        "en": "22. How would you rate your quality of life?",
        "pt": "22. Pensando nas duas últimas semanas, como você avaliaria sua qualidade de vida?",
    },
    "F1_2_satisfactionwithhealth": {
        "en": "23. How satisfied are you with your health?",
        "pt": "23. Pensando nas duas últimas semanas, quão satisfeito(a) você está com a sua saúde?",
    },
    "F1_3_enjoymentoflife": {
        "en": "24.3 How much do you enjoy life?",
        "pt": "24.3 O quanto você aproveita a vida?",
    },
    "F1_4_perceivedmeaninginlife": {
        "en": "24.4 To what extent do you feel your life to be meaningful?",
        "pt": "24.4 Em que medida você acha que a sua vida tem sentido?",
    },
    "F2_1_energyfordailyactivities": {
        "en": "25.1 Do you have enough energy for everyday life?",
        "pt": "25.1 Você tem energia suficiente para seu dia-a-dia?",
    },
    "F2_2_satisfactionwithsleep": {
        "en": "27.1 How satisfied are you with your sleep?",
        "pt": "27.1 Quão satisfeito(a) você está com o seu sono?",
    },
    "F3_1_performdailyactivities": {
        "en": "27.2 How satisfied are you with your ability to perform your daily living activities?",
        "pt": "27.2 Quão satisfeito(a) você está com sua capacidade de desempenhar as atividades do seu dia-a-dia?",
    },
    "F3_2_capacityforwork": {
        "en": "27.3 How satisfied are you with your capacity for work?",
        "pt": "27.3 Quão satisfeito(a) você está com sua capacidade para o trabalho?",
    },
}

# Original response-option wording for each item, for display/reference
# purposes only — not used by the scoring pipeline itself. Keyed by item,
# then by language code ("en", "pt"), each a list of 5 labels ordered from
# response value 1 to 5.
ITEM_OPTIONS = {
    "F1_1_overallqol": {
        "en": ["Very poor (1)", "Poor (2)", "Neither poor nor good (3)", "Good (4)", "Very good (5)"],
        "pt": ["Muito ruim (1)", "Ruim (2)", "Nem ruim, nem boa (3)", "Boa (4)", "Muito boa (5)"],
    },
    "F1_2_satisfactionwithhealth": {
        "en": ["Very dissatisfied (1)", "Dissatisfied (2)", "Neither satisfied nor dissatisfied (3)", "Satisfied (4)", "Very Satisfied (5)"],
        "pt": ["Muito insatisfeito (1)", "Insatisfeito (2)", "Nem satisfeito, nem insatisfeito (3)", "Satisfeito (4)", "Muito satisfeito (5)"],
    },
    "F1_3_enjoymentoflife": {
        "en": ["Not at all (1)", "A little (2)", "A moderate amount (3)", "Very much (4)", "An extreme amount (5)"],
        "pt": ["Nada (1)", "Muito pouco (2)", "Mais ou menos (3)", "Bastante (4)", "Extremamente (5)"],
    },
    "F1_4_perceivedmeaninginlife": {
        "en": ["Not at all (1)", "A little (2)", "A moderate amount (3)", "Very much (4)", "An extreme amount (5)"],
        "pt": ["Nada (1)", "Muito pouco (2)", "Mais ou menos (3)", "Bastante (4)", "Extremamente (5)"],
    },
    "F2_1_energyfordailyactivities": {
        "en": ["Not at all (1)", "A little (2)", "Moderately (3)", "Mostly (4)", "Completely (5)"],
        "pt": ["Nada (1)", "Muito pouco (2)", "Médio (3)", "Muito (4)", "Completamente (5)"],
    },
    "F2_2_satisfactionwithsleep": {
        "en": ["Very dissatisfied (1)", "Dissatisfied (2)", "Neither satisfied nor dissatisfied (3)", "Satisfied (4)", "Very Satisfied (5)"],
        "pt": ["Muito insatisfeito (1)", "Insatisfeito (2)", "Nem satisfeito, nem insatisfeito (3)", "Satisfeito (4)", "Muito satisfeito (5)"],
    },
    "F3_1_performdailyactivities": {
        "en": ["Very dissatisfied (1)", "Dissatisfied (2)", "Neither satisfied nor dissatisfied (3)", "Satisfied (4)", "Very Satisfied (5)"],
        "pt": ["Muito insatisfeito (1)", "Insatisfeito (2)", "Nem satisfeito, nem insatisfeito (3)", "Satisfeito (4)", "Muito satisfeito (5)"],
    },
    "F3_2_capacityforwork": {
        "en": ["Very dissatisfied (1)", "Dissatisfied (2)", "Neither satisfied nor dissatisfied (3)", "Satisfied (4)", "Very Satisfied (5)"],
        "pt": ["Muito insatisfeito (1)", "Insatisfeito (2)", "Nem satisfeito, nem insatisfeito (3)", "Satisfeito (4)", "Muito satisfeito (5)"],
    },
}
