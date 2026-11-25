"""Conteúdo oficial versionado em código — a fonte da verdade é o MySQL.

Não é upload, não é planilha, não é segredo: um conjunto pequeno e auditável de
unidades, lições, itens e exercícios. Aplicar de novo é seguro (`seed_content`
verifica o slug da unidade antes de gravar). Glossas ficam em `item_translations`;
a frase estudada permanece sempre no idioma alvo.
"""

from __future__ import annotations

from typing import Any, TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Deck, DeckItem, Exercise, Item, ItemTranslation, Lesson, Unit
from ..models.base import uuid7


class ItemSpec(TypedDict):
    key: str
    kind: str
    front_text: str
    example: str
    glosses: dict[str, str]


class ExerciseSpec(TypedDict):
    type: str
    item: str
    prompt: str
    answer: str
    options: list[str] | None
    order: int


class LessonSpec(TypedDict):
    slug: str
    title: str
    order: int
    xp: int
    items: list[str]
    exercises: list[ExerciseSpec]


class UnitSpec(TypedDict):
    slug: str
    title: str
    description: str
    level: str
    order: int
    prerequisite: str | None
    lessons: list[LessonSpec]


class DeckSpec(TypedDict):
    slug: str
    title: str
    description: str
    level: str
    items: list[str]


# =============================================================================
# ESPANHOL (es) - Português → Espanhol
# =============================================================================

ES_ITEMS: list[ItemSpec] = [
    # A1 - Saudações
    {
        "key": "hola",
        "kind": "word",
        "front_text": "Hola",
        "example": "Hola, María.",
        "glosses": {"pt-BR": "Olá", "en-US": "Hello"},
    },
    {
        "key": "buenos_dias",
        "kind": "phrase",
        "front_text": "Buenos días",
        "example": "Buenos días, profesor.",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "buenas_tardes",
        "kind": "phrase",
        "front_text": "Buenas tardes",
        "example": "Buenas tardes, ¿cómo estás?",
        "glosses": {"pt-BR": "Boa tarde", "en-US": "Good afternoon"},
    },
    {
        "key": "buenas_noches",
        "kind": "phrase",
        "front_text": "Buenas noches",
        "example": "Buenas noches, mamá.",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good night"},
    },
    {
        "key": "como_estas",
        "kind": "phrase",
        "front_text": "¿Cómo estás?",
        "example": "¿Cómo estás? — Muy bien, gracias.",
        "glosses": {"pt-BR": "Como você está?", "en-US": "How are you?"},
    },
    {
        "key": "mucho_gusto",
        "kind": "phrase",
        "front_text": "Mucho gusto",
        "example": "Mucho gusto en conocerte.",
        "glosses": {"pt-BR": "Prazer em conhecê-lo", "en-US": "Nice to meet you"},
    },
    {
        "key": "gracias",
        "kind": "word",
        "front_text": "Gracias",
        "example": "Gracias por tu ayuda.",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "de_nada",
        "kind": "phrase",
        "front_text": "De nada",
        "example": "— Gracias. — De nada.",
        "glosses": {"pt-BR": "De nada", "en-US": "You're welcome"},
    },
    {
        "key": "adios",
        "kind": "word",
        "front_text": "Adiós",
        "example": "Adiós, amigos.",
        "glosses": {"pt-BR": "Tchau", "en-US": "Goodbye"},
    },
    {
        "key": "hasta_luego",
        "kind": "phrase",
        "front_text": "Hasta luego",
        "example": "Hasta luego, nos vemos.",
        "glosses": {"pt-BR": "Até logo", "en-US": "See you later"},
    },
    # A1 - Números 1-10
    {
        "key": "uno",
        "kind": "word",
        "front_text": "Uno",
        "example": "Tengo uno.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "dos",
        "kind": "word",
        "front_text": "Dos",
        "example": "Dos libros.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "tres",
        "kind": "word",
        "front_text": "Tres",
        "example": "Tres amigos.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "cuatro",
        "kind": "word",
        "front_text": "Cuatro",
        "example": "Cuatro sillas.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "cinco",
        "kind": "word",
        "front_text": "Cinco",
        "example": "Cinco dedos.",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "seis",
        "kind": "word",
        "front_text": "Seis",
        "example": "Seis huevos.",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "siete",
        "kind": "word",
        "front_text": "Siete",
        "example": "Siete días.",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "ocho",
        "kind": "word",
        "front_text": "Ocho",
        "example": "Ocho planetas.",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "nueve",
        "kind": "word",
        "front_text": "Nueve",
        "example": "Nueve vidas.",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "diez",
        "kind": "word",
        "front_text": "Diez",
        "example": "Diez mandamientos.",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    # A1 - Apresentações
    {
        "key": "me_llamo",
        "kind": "phrase",
        "front_text": "Me llamo",
        "example": "Me llamo Juan.",
        "glosses": {"pt-BR": "Me chamo", "en-US": "My name is"},
    },
    {
        "key": "soy_de",
        "kind": "phrase",
        "front_text": "Soy de",
        "example": "Soy de Brasil.",
        "glosses": {"pt-BR": "Sou de", "en-US": "I'm from"},
    },
    {
        "key": "tengo_anos",
        "kind": "phrase",
        "front_text": "Tengo ... años",
        "example": "Tengo veinte años.",
        "glosses": {"pt-BR": "Tenho ... anos", "en-US": "I'm ... years old"},
    },
    # A1 - Cores
    {
        "key": "rojo",
        "kind": "word",
        "front_text": "Rojo",
        "example": "El coche es rojo.",
        "glosses": {"pt-BR": "Vermelho", "en-US": "Red"},
    },
    {
        "key": "azul",
        "kind": "word",
        "front_text": "Azul",
        "example": "El cielo es azul.",
        "glosses": {"pt-BR": "Azul", "en-US": "Blue"},
    },
    {
        "key": "verde",
        "kind": "word",
        "front_text": "Verde",
        "example": "La hierba es verde.",
        "glosses": {"pt-BR": "Verde", "en-US": "Green"},
    },
    {
        "key": "amarillo",
        "kind": "word",
        "front_text": "Amarillo",
        "example": "El sol es amarillo.",
        "glosses": {"pt-BR": "Amarelo", "en-US": "Yellow"},
    },
    {
        "key": "negro",
        "kind": "word",
        "front_text": "Negro",
        "example": "El gato es negro.",
        "glosses": {"pt-BR": "Preto", "en-US": "Black"},
    },
    {
        "key": "blanco",
        "kind": "word",
        "front_text": "Blanco",
        "example": "La nieve es blanca.",
        "glosses": {"pt-BR": "Branco", "en-US": "White"},
    },
    # A1 - Familia
    {
        "key": "padre",
        "kind": "word",
        "front_text": "Padre",
        "example": "Mi padre trabaja.",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "madre",
        "kind": "word",
        "front_text": "Madre",
        "example": "Mi madre cocina.",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "hermano",
        "kind": "word",
        "front_text": "Hermano",
        "example": "Tengo un hermano.",
        "glosses": {"pt-BR": "Irmão", "en-US": "Brother"},
    },
    {
        "key": "hermana",
        "kind": "word",
        "front_text": "Hermana",
        "example": "Mi hermana estudia.",
        "glosses": {"pt-BR": "Irmã", "en-US": "Sister"},
    },
    {
        "key": "abuelo",
        "kind": "word",
        "front_text": "Abuelo",
        "example": "Mi abuelo tiene 80 años.",
        "glosses": {"pt-BR": "Avô", "en-US": "Grandfather"},
    },
    {
        "key": "abuela",
        "kind": "word",
        "front_text": "Abuela",
        "example": "Mi abuela es dulce.",
        "glosses": {"pt-BR": "Avó", "en-US": "Grandmother"},
    },
    # A2 - Verbos básicos
    {
        "key": "ser",
        "kind": "word",
        "front_text": "Ser",
        "example": "Yo soy estudiante.",
        "glosses": {"pt-BR": "Ser", "en-US": "To be"},
    },
    {
        "key": "estar",
        "kind": "word",
        "front_text": "Estar",
        "example": "Estoy cansado.",
        "glosses": {"pt-BR": "Estar", "en-US": "To be"},
    },
    {
        "key": "tener",
        "kind": "word",
        "front_text": "Tener",
        "example": "Tengo un perro.",
        "glosses": {"pt-BR": "Ter", "en-US": "To have"},
    },
    {
        "key": "hacer",
        "kind": "word",
        "front_text": "Hacer",
        "example": "Hago la tarea.",
        "glosses": {"pt-BR": "Fazer", "en-US": "To do/make"},
    },
    {
        "key": "ir",
        "kind": "word",
        "front_text": "Ir",
        "example": "Voy a la escuela.",
        "glosses": {"pt-BR": "Ir", "en-US": "To go"},
    },
    {
        "key": "venir",
        "kind": "word",
        "front_text": "Venir",
        "example": "Viene mañana.",
        "glosses": {"pt-BR": "Vir", "en-US": "To come"},
    },
    {
        "key": "comer",
        "kind": "word",
        "front_text": "Comer",
        "example": "Como arroz.",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "beber",
        "kind": "word",
        "front_text": "Beber",
        "example": "Bebo agua.",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
    {
        "key": "dormir",
        "kind": "word",
        "front_text": "Dormir",
        "example": "Duermo ocho horas.",
        "glosses": {"pt-BR": "Dormir", "en-US": "To sleep"},
    },
    {
        "key": "trabajar",
        "kind": "word",
        "front_text": "Trabajar",
        "example": "Trabajo en una oficina.",
        "glosses": {"pt-BR": "Trabalhar", "en-US": "To work"},
    },
    # A2 - Comida
    {
        "key": "pan",
        "kind": "word",
        "front_text": "Pan",
        "example": "Como pan.",
        "glosses": {"pt-BR": "Pão", "en-US": "Bread"},
    },
    {
        "key": "agua",
        "kind": "word",
        "front_text": "Agua",
        "example": "Bebo agua.",
        "glosses": {"pt-BR": "Água", "en-US": "Water"},
    },
    {
        "key": "leche",
        "kind": "word",
        "front_text": "Leche",
        "example": "La leche es blanca.",
        "glosses": {"pt-BR": "Leite", "en-US": "Milk"},
    },
    {
        "key": "carne",
        "kind": "word",
        "front_text": "Carne",
        "example": "Como carne.",
        "glosses": {"pt-BR": "Carne", "en-US": "Meat"},
    },
    {
        "key": "pescado",
        "kind": "word",
        "front_text": "Pescado",
        "example": "El pescado es bueno.",
        "glosses": {"pt-BR": "Peixe", "en-US": "Fish"},
    },
    {
        "key": "arroz",
        "kind": "word",
        "front_text": "Arroz",
        "example": "Arroz con pollo.",
        "glosses": {"pt-BR": "Arroz", "en-US": "Rice"},
    },
    {
        "key": "fruta",
        "kind": "word",
        "front_text": "Fruta",
        "example": "Como fruta.",
        "glosses": {"pt-BR": "Fruta", "en-US": "Fruit"},
    },
    {
        "key": "verdura",
        "kind": "word",
        "front_text": "Verdura",
        "example": "Como verdura.",
        "glosses": {"pt-BR": "Legume", "en-US": "Vegetable"},
    },
    # A2 - Lugares
    {
        "key": "casa",
        "kind": "word",
        "front_text": "Casa",
        "example": "Mi casa es grande.",
        "glosses": {"pt-BR": "Casa", "en-US": "House"},
    },
    {
        "key": "escuela",
        "kind": "word",
        "front_text": "Escuela",
        "example": "Voy a la escuela.",
        "glosses": {"pt-BR": "Escola", "en-US": "School"},
    },
    {
        "key": "trabajo",
        "kind": "word",
        "front_text": "Trabajo",
        "example": "Mi trabajo es lejos.",
        "glosses": {"pt-BR": "Trabalho", "en-US": "Work"},
    },
    {
        "key": "mercado",
        "kind": "word",
        "front_text": "Mercado",
        "example": "Voy al mercado.",
        "glosses": {"pt-BR": "Mercado", "en-US": "Market"},
    },
    {
        "key": "parque",
        "kind": "word",
        "front_text": "Parque",
        "example": "Juego en el parque.",
        "glosses": {"pt-BR": "Parque", "en-US": "Park"},
    },
    {
        "key": "playa",
        "kind": "word",
        "front_text": "Playa",
        "example": "La playa es bonita.",
        "glosses": {"pt-BR": "Praia", "en-US": "Beach"},
    },
    # A2 - Tiempo
    {
        "key": "hoy",
        "kind": "word",
        "front_text": "Hoy",
        "example": "Hoy es lunes.",
        "glosses": {"pt-BR": "Hoje", "en-US": "Today"},
    },
    {
        "key": "manana",
        "kind": "word",
        "front_text": "Mañana",
        "example": "Mañana es martes.",
        "glosses": {"pt-BR": "Amanhã", "en-US": "Tomorrow"},
    },
    {
        "key": "ayer",
        "kind": "word",
        "front_text": "Ayer",
        "example": "Ayer fue domingo.",
        "glosses": {"pt-BR": "Ontem", "en-US": "Yesterday"},
    },
    {
        "key": "semana",
        "kind": "word",
        "front_text": "Semana",
        "example": "Una semana tiene siete días.",
        "glosses": {"pt-BR": "Semana", "en-US": "Week"},
    },
    {
        "key": "mes",
        "kind": "word",
        "front_text": "Mes",
        "example": "Enero es un mes.",
        "glosses": {"pt-BR": "Mês", "en-US": "Month"},
    },
    {
        "key": "ano",
        "kind": "word",
        "front_text": "Año",
        "example": "El año tiene 12 meses.",
        "glosses": {"pt-BR": "Ano", "en-US": "Year"},
    },
]

ES_UNITS: list[UnitSpec] = [
    # A1
    {
        "slug": "saudacoes",
        "title": "Saudações",
        "description": "Cumprimentos e despedidas básicas.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "primeiras-saudacoes",
                "title": "Primeiras saudações",
                "order": 1,
                "xp": 10,
                "items": [
                    "hola",
                    "buenos_dias",
                    "buenas_tardes",
                    "buenas_noches",
                    "adios",
                    "hasta_luego",
                ],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hola",
                        "prompt": "Hola",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "buenos_dias",
                        "prompt": "Buenos días",
                        "answer": "Bom dia",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "adios",
                        "prompt": "Como se diz «tchau» em espanhol?",
                        "answer": "Adiós",
                        "options": ["Adiós", "Hola", "Gracias"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "hasta_luego",
                        "prompt": "Até logo",
                        "answer": "Hasta luego",
                        "options": None,
                        "order": 4,
                    },
                ],
            },
            {
                "slug": "agradecimentos",
                "title": "Agradecimentos",
                "order": 2,
                "xp": 10,
                "items": ["gracias", "de_nada"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "gracias",
                        "prompt": "Gracias",
                        "answer": "Obrigado",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "de_nada",
                        "prompt": "Resposta para «gracias»?",
                        "answer": "De nada",
                        "options": ["De nada", "Por favor", "Adiós"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "numeros-1-10",
        "title": "Números 1 a 10",
        "description": "Contar de um a dez.",
        "level": "A1",
        "order": 2,
        "prerequisite": "saudacoes",
        "lessons": [
            {
                "slug": "numeros-um-a-cinco",
                "title": "Números 1 a 5",
                "order": 1,
                "xp": 10,
                "items": ["uno", "dos", "tres", "cuatro", "cinco"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "uno",
                        "prompt": "Uno",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "dos",
                        "prompt": "Dos",
                        "answer": "Dois",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "tres",
                        "prompt": "Qual é «três»?",
                        "answer": "Tres",
                        "options": ["Tres", "Dos", "Cuatro"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "cuatro",
                        "prompt": "Quatro",
                        "answer": "Cuatro",
                        "options": None,
                        "order": 4,
                    },
                    {
                        "type": "flashcard",
                        "item": "cinco",
                        "prompt": "Cinco",
                        "answer": "Cinco",
                        "options": None,
                        "order": 5,
                    },
                ],
            },
            {
                "slug": "numeros-seis-a-dez",
                "title": "Números 6 a 10",
                "order": 2,
                "xp": 10,
                "items": ["seis", "siete", "ocho", "nueve", "diez"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "seis",
                        "prompt": "Seis",
                        "answer": "Seis",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "siete",
                        "prompt": "Siete",
                        "answer": "Sete",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "ocho",
                        "prompt": "Qual é «oito»?",
                        "answer": "Ocho",
                        "options": ["Ocho", "Nueve", "Siete"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "nueve",
                        "prompt": "Nove",
                        "answer": "Nueve",
                        "options": None,
                        "order": 4,
                    },
                    {
                        "type": "flashcard",
                        "item": "diez",
                        "prompt": "Diez",
                        "answer": "Dez",
                        "options": None,
                        "order": 5,
                    },
                ],
            },
        ],
    },
    {
        "slug": "apresentacoes",
        "title": "Apresentações",
        "description": "Dizer seu nome, idade e origem.",
        "level": "A1",
        "order": 3,
        "prerequisite": "numeros-1-10",
        "lessons": [
            {
                "slug": "nome-idade",
                "title": "Nome e idade",
                "order": 1,
                "xp": 10,
                "items": ["me_llamo", "soy_de", "tengo_anos"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "me_llamo",
                        "prompt": "Me llamo",
                        "answer": "Me chamo",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "soy_de",
                        "prompt": "Sou do Brasil",
                        "answer": "Soy de Brasil",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "tengo_anos",
                        "prompt": "Como diz «tenho 20 anos»?",
                        "answer": "Tengo veinte años",
                        "options": ["Tengo veinte años", "Soy veinte años", "Estoy veinte años"],
                        "order": 3,
                    },
                ],
            },
            {
                "slug": "cumprimentos-informais",
                "title": "Cumprimentos informais",
                "order": 2,
                "xp": 10,
                "items": ["como_estas", "mucho_gusto"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "como_estas",
                        "prompt": "¿Cómo estás?",
                        "answer": "Como você está?",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "mucho_gusto",
                        "prompt": "Mucho gusto",
                        "answer": "Prazer em conhecê-lo",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "cores",
        "title": "Cores",
        "description": "As cores básicas.",
        "level": "A1",
        "order": 4,
        "prerequisite": "apresentacoes",
        "lessons": [
            {
                "slug": "cores-basicas",
                "title": "Cores básicas",
                "order": 1,
                "xp": 10,
                "items": ["rojo", "azul", "verde", "amarillo", "negro", "blanco"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "rojo",
                        "prompt": "Rojo",
                        "answer": "Vermelho",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "azul",
                        "prompt": "Cor do céu?",
                        "answer": "Azul",
                        "options": ["Azul", "Verde", "Rojo"],
                        "order": 2,
                    },
                    {
                        "type": "translation",
                        "item": "verde",
                        "prompt": "Verde",
                        "answer": "Verde",
                        "options": None,
                        "order": 3,
                    },
                ],
            },
        ],
    },
    {
        "slug": "familia",
        "title": "Família",
        "description": "Membros da família.",
        "level": "A1",
        "order": 5,
        "prerequisite": "cores",
        "lessons": [
            {
                "slug": "pais-irmaos",
                "title": "Pais e irmãos",
                "order": 1,
                "xp": 10,
                "items": ["padre", "madre", "hermano", "hermana"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "padre",
                        "prompt": "Padre",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "madre",
                        "prompt": "Mãe em espanhol?",
                        "answer": "Madre",
                        "options": ["Madre", "Padre", "Hermana"],
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "avos",
                "title": "Avós",
                "order": 2,
                "xp": 10,
                "items": ["abuelo", "abuela"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "abuelo",
                        "prompt": "Abuelo",
                        "answer": "Avô",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "abuela",
                        "prompt": "Avó",
                        "answer": "Abuela",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    # A2
    {
        "slug": "verbos-basicos",
        "title": "Verboses Básicos",
        "description": "Os verbos mais usados no dia a dia.",
        "level": "A2",
        "order": 6,
        "prerequisite": "familia",
        "lessons": [
            {
                "slug": "ser-estar",
                "title": "Ser vs Estar",
                "order": 1,
                "xp": 15,
                "items": ["ser", "estar"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "ser",
                        "prompt": "Ser",
                        "answer": "Ser (essência)",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "estar",
                        "prompt": "Estar",
                        "answer": "Estar (estado)",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "ser",
                        "prompt": '"Eu sou brasileiro" usa:',
                        "answer": "Ser",
                        "options": ["Ser", "Estar", "Tener"],
                        "order": 3,
                    },
                ],
            },
            {
                "slug": "ter-fazer",
                "title": "Ter e Fazer",
                "order": 2,
                "xp": 15,
                "items": ["tener", "hacer"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "tener",
                        "prompt": "Tener",
                        "answer": "Ter",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "hacer",
                        "prompt": "Fazer",
                        "answer": "Hacer",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "ir-vir",
                "title": "Ir e Vir",
                "order": 3,
                "xp": 15,
                "items": ["ir", "venir"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "ir",
                        "prompt": "Ir",
                        "answer": "Ir",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "venir",
                        "prompt": "Oposto de ir?",
                        "answer": "Venir",
                        "options": ["Venir", "Ir", "Estar"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "verbos-acoes",
        "title": "Verbos de Ação",
        "description": "Comer, beber, dormir, trabalhar.",
        "level": "A2",
        "order": 7,
        "prerequisite": "verbos-basicos",
        "lessons": [
            {
                "slug": "comer-beber",
                "title": "Comer e Beber",
                "order": 1,
                "xp": 15,
                "items": ["comer", "beber"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "comer",
                        "prompt": "Comer",
                        "answer": "Comer",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "beber",
                        "prompt": "Beber",
                        "answer": "Beber",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "dormir-trabalhar",
                "title": "Dormir e Trabalhar",
                "order": 2,
                "xp": 15,
                "items": ["dormir", "trabajar"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "dormir",
                        "prompt": "Dormir",
                        "answer": "Dormir",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "trabajar",
                        "prompt": "Trabalhar",
                        "answer": "Trabajar",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "comida",
        "title": "Comida e Bebida",
        "description": "Alimentos básicos.",
        "level": "A2",
        "order": 8,
        "prerequisite": "verbos-acoes",
        "lessons": [
            {
                "slug": "basicos",
                "title": "Básicos",
                "order": 1,
                "xp": 15,
                "items": ["pan", "agua", "leche", "carne", "pescado"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "pan",
                        "prompt": "Pan",
                        "answer": "Pão",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "leche",
                        "prompt": "Branca, vem da vaca?",
                        "answer": "Leche",
                        "options": ["Leche", "Agua", "Carne"],
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "acompanhamentos",
                "title": "Acompanhamentos",
                "order": 2,
                "xp": 15,
                "items": ["arroz", "fruta", "verdura"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "arroz",
                        "prompt": "Arroz",
                        "answer": "Arroz",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "fruta",
                        "prompt": "Fruta",
                        "answer": "Fruta",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "lugares",
        "title": "Lugares",
        "description": "Locais do dia a dia.",
        "level": "A2",
        "order": 9,
        "prerequisite": "comida",
        "lessons": [
            {
                "slug": "cotidianos",
                "title": "Lugares cotidianos",
                "order": 1,
                "xp": 15,
                "items": ["casa", "escuela", "trabajo", "mercado", "parque", "playa"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "casa",
                        "prompt": "Casa",
                        "answer": "Casa",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "escuela",
                        "prompt": "Onde se estuda?",
                        "answer": "Escuela",
                        "options": ["Escuela", "Casa", "Mercado"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "tempo",
        "title": "Tempo e Datas",
        "description": "Dias, meses, anos.",
        "level": "A2",
        "order": 10,
        "prerequisite": "lugares",
        "lessons": [
            {
                "slug": "dias-meses",
                "title": "Dias e Meses",
                "order": 1,
                "xp": 15,
                "items": ["hoy", "manana", "ayer", "semana", "mes", "ano"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hoy",
                        "prompt": "Hoy",
                        "answer": "Hoje",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "manana",
                        "prompt": "Amanhã",
                        "answer": "Mañana",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "semana",
                        "prompt": "7 dias?",
                        "answer": "Semana",
                        "options": ["Semana", "Mes", "Año"],
                        "order": 3,
                    },
                ],
            },
        ],
    },
]

ES_DECKS: list[DeckSpec] = [
    {
        "slug": "essencial-a1",
        "title": "Espanhol A1 — Essencial",
        "description": "Saudações, números, apresentações, cores, família.",
        "level": "A1",
        "items": [
            item["key"]
            for item in ES_ITEMS
            if item["key"]
            in [
                "hola",
                "buenos_dias",
                "buenas_tardes",
                "buenas_noches",
                "como_estas",
                "mucho_gusto",
                "gracias",
                "de_nada",
                "adios",
                "hasta_luego",
                "uno",
                "dos",
                "tres",
                "cuatro",
                "cinco",
                "seis",
                "siete",
                "ocho",
                "nueve",
                "diez",
                "me_llamo",
                "soy_de",
                "tengo_anos",
                "rojo",
                "azul",
                "verde",
                "amarillo",
                "negro",
                "blanco",
                "padre",
                "madre",
                "hermano",
                "hermana",
                "abuelo",
                "abuela",
            ]
        ],
    },
    {
        "slug": "completo-a2",
        "title": "Espanhol A2 — Completo",
        "description": "Verbos, comida, lugares, tempo.",
        "level": "A2",
        "items": [
            item["key"]
            for item in ES_ITEMS
            if item["key"]
            in [
                "ser",
                "estar",
                "tener",
                "hacer",
                "ir",
                "venir",
                "comer",
                "beber",
                "dormir",
                "trabajar",
                "pan",
                "agua",
                "leche",
                "carne",
                "pescado",
                "arroz",
                "fruta",
                "verdura",
                "casa",
                "escuela",
                "trabajo",
                "mercado",
                "parque",
                "playa",
                "hoy",
                "manana",
                "ayer",
                "semana",
                "mes",
                "ano",
            ]
        ],
    },
]


# =============================================================================
# INGLÊS (en) - Português → Inglês
# =============================================================================

EN_ITEMS: list[ItemSpec] = [
    # A1 - Greetings
    {
        "key": "hello",
        "kind": "word",
        "front_text": "Hello",
        "example": "Hello, John.",
        "glosses": {"pt-BR": "Olá", "en-US": "Hello"},
    },
    {
        "key": "good_morning",
        "kind": "phrase",
        "front_text": "Good morning",
        "example": "Good morning, teacher.",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "good_afternoon",
        "kind": "phrase",
        "front_text": "Good afternoon",
        "example": "Good afternoon, how are you?",
        "glosses": {"pt-BR": "Boa tarde", "en-US": "Good afternoon"},
    },
    {
        "key": "good_night",
        "kind": "phrase",
        "front_text": "Good night",
        "example": "Good night, mom.",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good night"},
    },
    {
        "key": "how_are_you",
        "kind": "phrase",
        "front_text": "How are you?",
        "example": "How are you? — I'm fine, thanks.",
        "glosses": {"pt-BR": "Como você está?", "en-US": "How are you?"},
    },
    {
        "key": "nice_to_meet_you",
        "kind": "phrase",
        "front_text": "Nice to meet you",
        "example": "Nice to meet you.",
        "glosses": {"pt-BR": "Prazer em conhecê-lo", "en-US": "Nice to meet you"},
    },
    {
        "key": "thank_you",
        "kind": "word",
        "front_text": "Thank you",
        "example": "Thank you for your help.",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "youre_welcome",
        "kind": "phrase",
        "front_text": "You're welcome",
        "example": "— Thank you. — You're welcome.",
        "glosses": {"pt-BR": "De nada", "en-US": "You're welcome"},
    },
    {
        "key": "goodbye",
        "kind": "word",
        "front_text": "Goodbye",
        "example": "Goodbye, friends.",
        "glosses": {"pt-BR": "Tchau", "en-US": "Goodbye"},
    },
    {
        "key": "see_you_later",
        "kind": "phrase",
        "front_text": "See you later",
        "example": "See you later.",
        "glosses": {"pt-BR": "Até logo", "en-US": "See you later"},
    },
    # A1 - Numbers 1-10
    {
        "key": "one",
        "kind": "word",
        "front_text": "One",
        "example": "I have one.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "two",
        "kind": "word",
        "front_text": "Two",
        "example": "Two books.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "three",
        "kind": "word",
        "front_text": "Three",
        "example": "Three friends.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "four",
        "kind": "word",
        "front_text": "Four",
        "example": "Four chairs.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "five",
        "kind": "word",
        "front_text": "Five",
        "example": "Five fingers.",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "six",
        "kind": "word",
        "front_text": "Six",
        "example": "Six eggs.",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "seven",
        "kind": "word",
        "front_text": "Seven",
        "example": "Seven days.",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "eight",
        "kind": "word",
        "front_text": "Eight",
        "example": "Eight planets.",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "nine",
        "kind": "word",
        "front_text": "Nine",
        "example": "Nine lives.",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "ten",
        "kind": "word",
        "front_text": "Ten",
        "example": "Ten commandments.",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    # A1 - Introductions
    {
        "key": "my_name_is",
        "kind": "phrase",
        "front_text": "My name is",
        "example": "My name is John.",
        "glosses": {"pt-BR": "Me chamo", "en-US": "My name is"},
    },
    {
        "key": "im_from",
        "kind": "phrase",
        "front_text": "I'm from",
        "example": "I'm from Brazil.",
        "glosses": {"pt-BR": "Sou de", "en-US": "I'm from"},
    },
    {
        "key": "im_years_old",
        "kind": "phrase",
        "front_text": "I'm ... years old",
        "example": "I'm twenty years old.",
        "glosses": {"pt-BR": "Tenho ... anos", "en-US": "I'm ... years old"},
    },
    # A1 - Colors
    {
        "key": "red",
        "kind": "word",
        "front_text": "Red",
        "example": "The car is red.",
        "glosses": {"pt-BR": "Vermelho", "en-US": "Red"},
    },
    {
        "key": "blue",
        "kind": "word",
        "front_text": "Blue",
        "example": "The sky is blue.",
        "glosses": {"pt-BR": "Azul", "en-US": "Blue"},
    },
    {
        "key": "green",
        "kind": "word",
        "front_text": "Green",
        "example": "The grass is green.",
        "glosses": {"pt-BR": "Verde", "en-US": "Green"},
    },
    {
        "key": "yellow",
        "kind": "word",
        "front_text": "Yellow",
        "example": "The sun is yellow.",
        "glosses": {"pt-BR": "Amarelo", "en-US": "Yellow"},
    },
    {
        "key": "black",
        "kind": "word",
        "front_text": "Black",
        "example": "The cat is black.",
        "glosses": {"pt-BR": "Preto", "en-US": "Black"},
    },
    {
        "key": "white",
        "kind": "word",
        "front_text": "White",
        "example": "The snow is white.",
        "glosses": {"pt-BR": "Branco", "en-US": "White"},
    },
    # A1 - Family
    {
        "key": "father",
        "kind": "word",
        "front_text": "Father",
        "example": "My father works.",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "mother",
        "kind": "word",
        "front_text": "Mother",
        "example": "My mother cooks.",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "brother",
        "kind": "word",
        "front_text": "Brother",
        "example": "I have a brother.",
        "glosses": {"pt-BR": "Irmão", "en-US": "Brother"},
    },
    {
        "key": "sister",
        "kind": "word",
        "front_text": "Sister",
        "example": "My sister studies.",
        "glosses": {"pt-BR": "Irmã", "en-US": "Sister"},
    },
    {
        "key": "grandfather",
        "kind": "word",
        "front_text": "Grandfather",
        "example": "My grandfather is 80.",
        "glosses": {"pt-BR": "Avô", "en-US": "Grandfather"},
    },
    {
        "key": "grandmother",
        "kind": "word",
        "front_text": "Grandmother",
        "example": "My grandmother is sweet.",
        "glosses": {"pt-BR": "Avó", "en-US": "Grandmother"},
    },
    # A2 - Basic verbs
    {
        "key": "to_be",
        "kind": "word",
        "front_text": "To be",
        "example": "I am a student.",
        "glosses": {"pt-BR": "Ser/Estar", "en-US": "To be"},
    },
    {
        "key": "to_have",
        "kind": "word",
        "front_text": "To have",
        "example": "I have a dog.",
        "glosses": {"pt-BR": "Ter", "en-US": "To have"},
    },
    {
        "key": "to_do",
        "kind": "word",
        "front_text": "To do",
        "example": "I do my homework.",
        "glosses": {"pt-BR": "Fazer", "en-US": "To do"},
    },
    {
        "key": "to_make",
        "kind": "word",
        "front_text": "To make",
        "example": "I make a cake.",
        "glosses": {"pt-BR": "Fazer", "en-US": "To make"},
    },
    {
        "key": "to_go",
        "kind": "word",
        "front_text": "To go",
        "example": "I go to school.",
        "glosses": {"pt-BR": "Ir", "en-US": "To go"},
    },
    {
        "key": "to_come",
        "kind": "word",
        "front_text": "To come",
        "example": "He comes tomorrow.",
        "glosses": {"pt-BR": "Vir", "en-US": "To come"},
    },
    {
        "key": "to_eat",
        "kind": "word",
        "front_text": "To eat",
        "example": "I eat rice.",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "to_drink",
        "kind": "word",
        "front_text": "To drink",
        "example": "I drink water.",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
    {
        "key": "to_sleep",
        "kind": "word",
        "front_text": "To sleep",
        "example": "I sleep eight hours.",
        "glosses": {"pt-BR": "Dormir", "en-US": "To sleep"},
    },
    {
        "key": "to_work",
        "kind": "word",
        "front_text": "To work",
        "example": "I work in an office.",
        "glosses": {"pt-BR": "Trabalhar", "en-US": "To work"},
    },
    # A2 - Food
    {
        "key": "bread",
        "kind": "word",
        "front_text": "Bread",
        "example": "I eat bread.",
        "glosses": {"pt-BR": "Pão", "en-US": "Bread"},
    },
    {
        "key": "water",
        "kind": "word",
        "front_text": "Water",
        "example": "I drink water.",
        "glosses": {"pt-BR": "Água", "en-US": "Water"},
    },
    {
        "key": "milk",
        "kind": "word",
        "front_text": "Milk",
        "example": "Milk is white.",
        "glosses": {"pt-BR": "Leite", "en-US": "Milk"},
    },
    {
        "key": "meat",
        "kind": "word",
        "front_text": "Meat",
        "example": "I eat meat.",
        "glosses": {"pt-BR": "Carne", "en-US": "Meat"},
    },
    {
        "key": "fish",
        "kind": "word",
        "front_text": "Fish",
        "example": "Fish is good.",
        "glosses": {"pt-BR": "Peixe", "en-US": "Fish"},
    },
    {
        "key": "rice",
        "kind": "word",
        "front_text": "Rice",
        "example": "Chicken with rice.",
        "glosses": {"pt-BR": "Arroz", "en-US": "Rice"},
    },
    {
        "key": "fruit",
        "kind": "word",
        "front_text": "Fruit",
        "example": "I eat fruit.",
        "glosses": {"pt-BR": "Fruta", "en-US": "Fruit"},
    },
    {
        "key": "vegetable",
        "kind": "word",
        "front_text": "Vegetable",
        "example": "I eat vegetables.",
        "glosses": {"pt-BR": "Legume", "en-US": "Vegetable"},
    },
    # A2 - Places
    {
        "key": "house",
        "kind": "word",
        "front_text": "House",
        "example": "My house is big.",
        "glosses": {"pt-BR": "Casa", "en-US": "House"},
    },
    {
        "key": "school",
        "kind": "word",
        "front_text": "School",
        "example": "I go to school.",
        "glosses": {"pt-BR": "Escola", "en-US": "School"},
    },
    {
        "key": "work",
        "kind": "word",
        "front_text": "Work",
        "example": "My work is far.",
        "glosses": {"pt-BR": "Trabalho", "en-US": "Work"},
    },
    {
        "key": "market",
        "kind": "word",
        "front_text": "Market",
        "example": "I go to the market.",
        "glosses": {"pt-BR": "Mercado", "en-US": "Market"},
    },
    {
        "key": "park",
        "kind": "word",
        "front_text": "Park",
        "example": "I play in the park.",
        "glosses": {"pt-BR": "Parque", "en-US": "Park"},
    },
    {
        "key": "beach",
        "kind": "word",
        "front_text": "Beach",
        "example": "The beach is beautiful.",
        "glosses": {"pt-BR": "Praia", "en-US": "Beach"},
    },
    # A2 - Time
    {
        "key": "today",
        "kind": "word",
        "front_text": "Today",
        "example": "Today is Monday.",
        "glosses": {"pt-BR": "Hoje", "en-US": "Today"},
    },
    {
        "key": "tomorrow",
        "kind": "word",
        "front_text": "Tomorrow",
        "example": "Tomorrow is Tuesday.",
        "glosses": {"pt-BR": "Amanhã", "en-US": "Tomorrow"},
    },
    {
        "key": "yesterday",
        "kind": "word",
        "front_text": "Yesterday",
        "example": "Yesterday was Sunday.",
        "glosses": {"pt-BR": "Ontem", "en-US": "Yesterday"},
    },
    {
        "key": "week",
        "kind": "word",
        "front_text": "Week",
        "example": "A week has seven days.",
        "glosses": {"pt-BR": "Semana", "en-US": "Week"},
    },
    {
        "key": "month",
        "kind": "word",
        "front_text": "Month",
        "example": "January is a month.",
        "glosses": {"pt-BR": "Mês", "en-US": "Month"},
    },
    {
        "key": "year",
        "kind": "word",
        "front_text": "Year",
        "example": "The year has 12 months.",
        "glosses": {"pt-BR": "Ano", "en-US": "Year"},
    },
]

EN_UNITS: list[UnitSpec] = [
    # A1
    {
        "slug": "greetings",
        "title": "Greetings",
        "description": "Basic greetings and farewells.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "first-greetings",
                "title": "First greetings",
                "order": 1,
                "xp": 10,
                "items": [
                    "hello",
                    "good_morning",
                    "good_afternoon",
                    "good_night",
                    "goodbye",
                    "see_you_later",
                ],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hello",
                        "prompt": "Hello",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "good_morning",
                        "prompt": "Good morning",
                        "answer": "Bom dia",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "goodbye",
                        "prompt": "How to say «tchau»?",
                        "answer": "Goodbye",
                        "options": ["Goodbye", "Hello", "Thank you"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "see_you_later",
                        "prompt": "Até logo",
                        "answer": "See you later",
                        "options": None,
                        "order": 4,
                    },
                ],
            },
            {
                "slug": "thanks",
                "title": "Thank you",
                "order": 2,
                "xp": 10,
                "items": ["thank_you", "youre_welcome"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "thank_you",
                        "prompt": "Thank you",
                        "answer": "Obrigado",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "youre_welcome",
                        "prompt": "Response to «thank you»?",
                        "answer": "You're welcome",
                        "options": ["You're welcome", "Please", "Goodbye"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "numbers-1-10",
        "title": "Numbers 1-10",
        "description": "Counting from one to ten.",
        "level": "A1",
        "order": 2,
        "prerequisite": "greetings",
        "lessons": [
            {
                "slug": "numbers-one-five",
                "title": "Numbers 1-5",
                "order": 1,
                "xp": 10,
                "items": ["one", "two", "three", "four", "five"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "one",
                        "prompt": "One",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "two",
                        "prompt": "Two",
                        "answer": "Dois",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "three",
                        "prompt": "Which is «three»?",
                        "answer": "Three",
                        "options": ["Three", "Two", "Four"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "four",
                        "prompt": "Four",
                        "answer": "Four",
                        "options": None,
                        "order": 4,
                    },
                    {
                        "type": "flashcard",
                        "item": "five",
                        "prompt": "Five",
                        "answer": "Cinco",
                        "options": None,
                        "order": 5,
                    },
                ],
            },
            {
                "slug": "numbers-six-ten",
                "title": "Numbers 6-10",
                "order": 2,
                "xp": 10,
                "items": ["six", "seven", "eight", "nine", "ten"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "six",
                        "prompt": "Six",
                        "answer": "Seis",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "seven",
                        "prompt": "Seven",
                        "answer": "Sete",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "eight",
                        "prompt": "Which is «eight»?",
                        "answer": "Eight",
                        "options": ["Eight", "Nine", "Seven"],
                        "order": 3,
                    },
                    {
                        "type": "translation",
                        "item": "nine",
                        "prompt": "Nine",
                        "answer": "Nine",
                        "options": None,
                        "order": 4,
                    },
                    {
                        "type": "flashcard",
                        "item": "ten",
                        "prompt": "Ten",
                        "answer": "Dez",
                        "options": None,
                        "order": 5,
                    },
                ],
            },
        ],
    },
    {
        "slug": "introductions",
        "title": "Introductions",
        "description": "Say your name, age and origin.",
        "level": "A1",
        "order": 3,
        "prerequisite": "numbers-1-10",
        "lessons": [
            {
                "slug": "name-age",
                "title": "Name and age",
                "order": 1,
                "xp": 10,
                "items": ["my_name_is", "im_from", "im_years_old"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "my_name_is",
                        "prompt": "My name is",
                        "answer": "Me chamo",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "im_from",
                        "prompt": "I'm from Brazil",
                        "answer": "I'm from Brazil",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "im_years_old",
                        "prompt": "How to say «I'm 20 years old»?",
                        "answer": "I'm twenty years old",
                        "options": ["I'm twenty years old", "I have twenty years", "I am twenty"],
                        "order": 3,
                    },
                ],
            },
        ],
    },
    {
        "slug": "colors",
        "title": "Colors",
        "description": "Basic colors.",
        "level": "A1",
        "order": 4,
        "prerequisite": "introductions",
        "lessons": [
            {
                "slug": "basic-colors",
                "title": "Basic colors",
                "order": 1,
                "xp": 10,
                "items": ["red", "blue", "green", "yellow", "black", "white"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "red",
                        "prompt": "Red",
                        "answer": "Vermelho",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "blue",
                        "prompt": "Color of the sky?",
                        "answer": "Blue",
                        "options": ["Blue", "Green", "Red"],
                        "order": 2,
                    },
                    {
                        "type": "translation",
                        "item": "green",
                        "prompt": "Green",
                        "answer": "Verde",
                        "options": None,
                        "order": 3,
                    },
                ],
            },
        ],
    },
    {
        "slug": "family",
        "title": "Family",
        "description": "Family members.",
        "level": "A1",
        "order": 5,
        "prerequisite": "colors",
        "lessons": [
            {
                "slug": "parents-siblings",
                "title": "Parents and siblings",
                "order": 1,
                "xp": 10,
                "items": ["father", "mother", "brother", "sister"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "father",
                        "prompt": "Father",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "mother",
                        "prompt": "Mother in English?",
                        "answer": "Mother",
                        "options": ["Mother", "Father", "Sister"],
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "grandparents",
                "title": "Grandparents",
                "order": 2,
                "xp": 10,
                "items": ["grandfather", "grandmother"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "grandfather",
                        "prompt": "Grandfather",
                        "answer": "Avô",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "grandmother",
                        "prompt": "Grandmother",
                        "answer": "Grandmother",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    # A2
    {
        "slug": "basic-verbs",
        "title": "Basic Verbs",
        "description": "Most used verbs.",
        "level": "A2",
        "order": 6,
        "prerequisite": "family",
        "lessons": [
            {
                "slug": "be-have",
                "title": "To be & To have",
                "order": 1,
                "xp": 15,
                "items": ["to_be", "to_have"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "to_be",
                        "prompt": "To be",
                        "answer": "Ser/Estar",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "to_have",
                        "prompt": "To have",
                        "answer": "Ter",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "to_be",
                        "prompt": "«I am Brazilian» uses:",
                        "answer": "To be",
                        "options": ["To be", "To have", "To do"],
                        "order": 3,
                    },
                ],
            },
            {
                "slug": "do-make",
                "title": "To do & To make",
                "order": 2,
                "xp": 15,
                "items": ["to_do", "to_make"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "to_do",
                        "prompt": "To do",
                        "answer": "Fazer",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "to_make",
                        "prompt": "To make",
                        "answer": "To make",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "go-come",
                "title": "To go & To come",
                "order": 3,
                "xp": 15,
                "items": ["to_go", "to_come"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "to_go",
                        "prompt": "To go",
                        "answer": "Ir",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "to_come",
                        "prompt": "Opposite of to go?",
                        "answer": "To come",
                        "options": ["To come", "To go", "To be"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "action-verbs",
        "title": "Action Verbs",
        "description": "Eat, drink, sleep, work.",
        "level": "A2",
        "order": 7,
        "prerequisite": "basic-verbs",
        "lessons": [
            {
                "slug": "eat-drink",
                "title": "Eat & Drink",
                "order": 1,
                "xp": 15,
                "items": ["to_eat", "to_drink"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "to_eat",
                        "prompt": "To eat",
                        "answer": "Comer",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "to_drink",
                        "prompt": "To drink",
                        "answer": "Beber",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "sleep-work",
                "title": "Sleep & Work",
                "order": 2,
                "xp": 15,
                "items": ["to_sleep", "to_work"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "to_sleep",
                        "prompt": "To sleep",
                        "answer": "Dormir",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "to_work",
                        "prompt": "To work",
                        "answer": "To work",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "food-drink",
        "title": "Food & Drink",
        "description": "Basic foods.",
        "level": "A2",
        "order": 8,
        "prerequisite": "action-verbs",
        "lessons": [
            {
                "slug": "basics",
                "title": "Basics",
                "order": 1,
                "xp": 15,
                "items": ["bread", "water", "milk", "meat", "fish"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "bread",
                        "prompt": "Bread",
                        "answer": "Pão",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "milk",
                        "prompt": "White, from cow?",
                        "answer": "Milk",
                        "options": ["Milk", "Water", "Meat"],
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "sides",
                "title": "Sides",
                "order": 2,
                "xp": 15,
                "items": ["rice", "fruit", "vegetable"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "rice",
                        "prompt": "Rice",
                        "answer": "Arroz",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "fruit",
                        "prompt": "Fruit",
                        "answer": "Fruta",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "places",
        "title": "Places",
        "description": "Daily places.",
        "level": "A2",
        "order": 9,
        "prerequisite": "food-drink",
        "lessons": [
            {
                "slug": "daily-places",
                "title": "Daily places",
                "order": 1,
                "xp": 15,
                "items": ["house", "school", "work", "market", "park", "beach"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "house",
                        "prompt": "House",
                        "answer": "Casa",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "school",
                        "prompt": "Where to study?",
                        "answer": "School",
                        "options": ["School", "House", "Market"],
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "time-dates",
        "title": "Time & Dates",
        "description": "Days, months, years.",
        "level": "A2",
        "order": 10,
        "prerequisite": "places",
        "lessons": [
            {
                "slug": "days-months",
                "title": "Days & Months",
                "order": 1,
                "xp": 15,
                "items": ["today", "tomorrow", "yesterday", "week", "month", "year"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "today",
                        "prompt": "Today",
                        "answer": "Hoje",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "tomorrow",
                        "prompt": "Tomorrow",
                        "answer": "Amanhã",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "week",
                        "prompt": "7 days?",
                        "answer": "Week",
                        "options": ["Week", "Month", "Year"],
                        "order": 3,
                    },
                ],
            },
        ],
    },
]

EN_DECKS: list[DeckSpec] = [
    {
        "slug": "essential-a1",
        "title": "English A1 — Essential",
        "description": "Greetings, numbers, introductions, colors, family.",
        "level": "A1",
        "items": [
            item["key"]
            for item in EN_ITEMS
            if item["key"]
            in [
                "hello",
                "good_morning",
                "good_afternoon",
                "good_night",
                "how_are_you",
                "nice_to_meet_you",
                "thank_you",
                "youre_welcome",
                "goodbye",
                "see_you_later",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
                "my_name_is",
                "im_from",
                "im_years_old",
                "red",
                "blue",
                "green",
                "yellow",
                "black",
                "white",
                "father",
                "mother",
                "brother",
                "sister",
                "grandfather",
                "grandmother",
            ]
        ],
    },
    {
        "slug": "complete-a2",
        "title": "English A2 — Complete",
        "description": "Verbs, food, places, time.",
        "level": "A2",
        "items": [
            item["key"]
            for item in EN_ITEMS
            if item["key"]
            in [
                "to_be",
                "to_have",
                "to_do",
                "to_make",
                "to_go",
                "to_come",
                "to_eat",
                "to_drink",
                "to_sleep",
                "to_work",
                "bread",
                "water",
                "milk",
                "meat",
                "fish",
                "rice",
                "fruit",
                "vegetable",
                "house",
                "school",
                "work",
                "market",
                "park",
                "beach",
                "today",
                "tomorrow",
                "yesterday",
                "week",
                "month",
                "year",
            ]
        ],
    },
]


# =============================================================================
# FRANCÊS (fr) - Português → Francês
# =============================================================================

FR_ITEMS: list[ItemSpec] = [
    # A1
    {
        "key": "bonjour",
        "kind": "word",
        "front_text": "Bonjour",
        "example": "Bonjour, Marie.",
        "glosses": {"pt-BR": "Bom dia/Olá", "en-US": "Hello"},
    },
    {
        "key": "bonsoir",
        "kind": "word",
        "front_text": "Bonsoir",
        "example": "Bonsoir, monsieur.",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good evening"},
    },
    {
        "key": "salut",
        "kind": "word",
        "front_text": "Salut",
        "example": "Salut, ça va ?",
        "glosses": {"pt-BR": "Oi/Tchau", "en-US": "Hi/Bye"},
    },
    {
        "key": "au_revoir",
        "kind": "phrase",
        "front_text": "Au revoir",
        "example": "Au revoir, à demain.",
        "glosses": {"pt-BR": "Adeus/Tchau", "en-US": "Goodbye"},
    },
    {
        "key": "merci",
        "kind": "word",
        "front_text": "Merci",
        "example": "Merci beaucoup.",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "de_rien",
        "kind": "phrase",
        "front_text": "De rien",
        "example": "— Merci. — De rien.",
        "glosses": {"pt-BR": "De nada", "en-US": "You're welcome"},
    },
    {
        "key": "comment_ca_va",
        "kind": "phrase",
        "front_text": "Comment ça va ?",
        "example": "Comment ça va ? — Ça va bien.",
        "glosses": {"pt-BR": "Como vai?", "en-US": "How are you?"},
    },
    {
        "key": "je_mappelle",
        "kind": "phrase",
        "front_text": "Je m'appelle",
        "example": "Je m'appelle Pierre.",
        "glosses": {"pt-BR": "Me chamo", "en-US": "My name is"},
    },
    {
        "key": "un",
        "kind": "word",
        "front_text": "Un",
        "example": "Un livre.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "deux",
        "kind": "word",
        "front_text": "Deux",
        "example": "Deux pommes.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "trois",
        "kind": "word",
        "front_text": "Trois",
        "example": "Trois amis.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "quatre",
        "kind": "word",
        "front_text": "Quatre",
        "example": "Quatre chaises.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "cinq",
        "kind": "word",
        "front_text": "Cinq",
        "example": "Cinq doigts.",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "six",
        "kind": "word",
        "front_text": "Six",
        "example": "Six œufs.",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "sept",
        "kind": "word",
        "front_text": "Sept",
        "example": "Sept jours.",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "huit",
        "kind": "word",
        "front_text": "Huit",
        "example": "Huit planètes.",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "neuf",
        "kind": "word",
        "front_text": "Neuf",
        "example": "Neuf vies.",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "dix",
        "kind": "word",
        "front_text": "Dix",
        "example": "Dix commandements.",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    {
        "key": "pere",
        "kind": "word",
        "front_text": "Père",
        "example": "Mon père travaille.",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "mere",
        "kind": "word",
        "front_text": "Mère",
        "example": "Ma mère cuisine.",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "frere",
        "kind": "word",
        "front_text": "Frère",
        "example": "J'ai un frère.",
        "glosses": {"pt-BR": "Irmão", "en-US": "Brother"},
    },
    {
        "key": "soeur",
        "kind": "word",
        "front_text": "Sœur",
        "example": "Ma sœur étudie.",
        "glosses": {"pt-BR": "Irmã", "en-US": "Sister"},
    },
    {
        "key": "etre",
        "kind": "word",
        "front_text": "Être",
        "example": "Je suis étudiant.",
        "glosses": {"pt-BR": "Ser/Estar", "en-US": "To be"},
    },
    {
        "key": "avoir",
        "kind": "word",
        "front_text": "Avoir",
        "example": "J'ai un chat.",
        "glosses": {"pt-BR": "Ter", "en-US": "To have"},
    },
    {
        "key": "aller",
        "kind": "word",
        "front_text": "Aller",
        "example": "Je vais à l'école.",
        "glosses": {"pt-BR": "Ir", "en-US": "To go"},
    },
    {
        "key": "manger",
        "kind": "word",
        "front_text": "Manger",
        "example": "Je mange du pain.",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "boire",
        "kind": "word",
        "front_text": "Boire",
        "example": "Je bois de l'eau.",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
    {
        "key": "pain",
        "kind": "word",
        "front_text": "Pain",
        "example": "Je mange du pain.",
        "glosses": {"pt-BR": "Pão", "en-US": "Bread"},
    },
    {
        "key": "eau",
        "kind": "word",
        "front_text": "Eau",
        "example": "Je bois de l'eau.",
        "glosses": {"pt-BR": "Água", "en-US": "Water"},
    },
    {
        "key": "lait",
        "kind": "word",
        "front_text": "Lait",
        "example": "Le lait est blanc.",
        "glosses": {"pt-BR": "Leite", "en-US": "Milk"},
    },
    {
        "key": "viande",
        "kind": "word",
        "front_text": "Viande",
        "example": "Je mange de la viande.",
        "glosses": {"pt-BR": "Carne", "en-US": "Meat"},
    },
    {
        "key": "poisson",
        "kind": "word",
        "front_text": "Poisson",
        "example": "Le poisson est bon.",
        "glosses": {"pt-BR": "Peixe", "en-US": "Fish"},
    },
    {
        "key": "riz",
        "kind": "word",
        "front_text": "Riz",
        "example": "Riz au poulet.",
        "glosses": {"pt-BR": "Arroz", "en-US": "Rice"},
    },
    {
        "key": "fruit",
        "kind": "word",
        "front_text": "Fruit",
        "example": "Je mange un fruit.",
        "glosses": {"pt-BR": "Fruta", "en-US": "Fruit"},
    },
    {
        "key": "legume",
        "kind": "word",
        "front_text": "Légume",
        "example": "Je mange des légumes.",
        "glosses": {"pt-BR": "Legume", "en-US": "Vegetable"},
    },
    {
        "key": "maison",
        "kind": "word",
        "front_text": "Maison",
        "example": "Ma maison est grande.",
        "glosses": {"pt-BR": "Casa", "en-US": "House"},
    },
    {
        "key": "ecole",
        "kind": "word",
        "front_text": "École",
        "example": "Je vais à l'école.",
        "glosses": {"pt-BR": "Escola", "en-US": "School"},
    },
    {
        "key": "travail",
        "kind": "word",
        "front_text": "Travail",
        "example": "Mon travail est loin.",
        "glosses": {"pt-BR": "Trabalho", "en-US": "Work"},
    },
    {
        "key": "aujourdhui",
        "kind": "word",
        "front_text": "Aujourd'hui",
        "example": "Aujourd'hui c'est lundi.",
        "glosses": {"pt-BR": "Hoje", "en-US": "Today"},
    },
    {
        "key": "demain",
        "kind": "word",
        "front_text": "Demain",
        "example": "Demain c'est mardi.",
        "glosses": {"pt-BR": "Amanhã", "en-US": "Tomorrow"},
    },
    {
        "key": "hier",
        "kind": "word",
        "front_text": "Hier",
        "example": "Hier c'était dimanche.",
        "glosses": {"pt-BR": "Ontem", "en-US": "Yesterday"},
    },
]

FR_UNITS: list[UnitSpec] = [
    {
        "slug": "salutations",
        "title": "Saudações",
        "description": "Cumprimentos básicos.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "bonjour-au-revoir",
                "title": "Bonjour / Au revoir",
                "order": 1,
                "xp": 10,
                "items": ["bonjour", "bonsoir", "salut", "au_revoir"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "bonjour",
                        "prompt": "Bonjour",
                        "answer": "Bom dia",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "au_revoir",
                        "prompt": "Au revoir",
                        "answer": "Adeus",
                        "options": None,
                        "order": 2,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "salut",
                        "prompt": "Informal hi/bye?",
                        "answer": "Salut",
                        "options": ["Salut", "Bonjour", "Merci"],
                        "order": 3,
                    },
                ],
            }
        ],
    },
    {
        "slug": "nombres",
        "title": "Números 1-10",
        "description": "Compter jusqu'à dix.",
        "level": "A1",
        "order": 2,
        "prerequisite": "salutations",
        "lessons": [
            {
                "slug": "un-a-cinq",
                "title": "Un à cinq",
                "order": 1,
                "xp": 10,
                "items": ["un", "deux", "trois", "quatre", "cinq"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "un",
                        "prompt": "Un",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "trois",
                        "prompt": "Quel est «trois»?",
                        "answer": "Trois",
                        "options": ["Trois", "Deux", "Quatre"],
                        "order": 2,
                    },
                ],
            },
            {
                "slug": "six-a-dix",
                "title": "Six à dix",
                "order": 2,
                "xp": 10,
                "items": ["six", "sept", "huit", "neuf", "dix"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "six",
                        "prompt": "Six",
                        "answer": "Seis",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "translation",
                        "item": "dix",
                        "prompt": "Dez",
                        "answer": "Dix",
                        "options": None,
                        "order": 2,
                    },
                ],
            },
        ],
    },
    {
        "slug": "famille",
        "title": "Famille",
        "description": "Membres de la famille.",
        "level": "A1",
        "order": 3,
        "prerequisite": "nombres",
        "lessons": [
            {
                "slug": "parents",
                "title": "Parents",
                "order": 1,
                "xp": 10,
                "items": ["pere", "mere", "frere", "soeur"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "pere",
                        "prompt": "Père",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "mere",
                        "prompt": "Mère em português?",
                        "answer": "Mãe",
                        "options": ["Mère", "Père", "Sœur"],
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "verbes",
        "title": "Verbes essentiels",
        "description": "Être, avoir, aller, manger.",
        "level": "A2",
        "order": 4,
        "prerequisite": "famille",
        "lessons": [
            {
                "slug": "etre-avoir",
                "title": "Être & Avoir",
                "order": 1,
                "xp": 15,
                "items": ["etre", "avoir"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "etre",
                        "prompt": "Être",
                        "answer": "Ser/Estar",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "avoir",
                        "prompt": "J'ai un chat = ?",
                        "answer": "Tenho um gato",
                        "options": ["Tenho um gato", "Sou um gato", "Vou um gato"],
                        "order": 2,
                    },
                ],
            }
        ],
    },
]

FR_DECKS: list[DeckSpec] = [
    {
        "slug": "essentiel-a1",
        "title": "Français A1 — Essentiel",
        "description": "Saudações, números, família.",
        "level": "A1",
        "items": [
            item["key"]
            for item in FR_ITEMS
            if item["key"]
            in [
                "bonjour",
                "bonsoir",
                "salut",
                "au_revoir",
                "merci",
                "de_rien",
                "comment_ca_va",
                "je_mappelle",
                "un",
                "deux",
                "trois",
                "quatre",
                "cinq",
                "six",
                "sept",
                "huit",
                "neuf",
                "dix",
                "pere",
                "mere",
                "frere",
                "soeur",
            ]
        ],
    },
    {
        "slug": "verbes-a2",
        "title": "Français A2 — Verbos",
        "description": "Être, avoir, aller, manger.",
        "level": "A2",
        "items": [
            item["key"]
            for item in FR_ITEMS
            if item["key"]
            in [
                "etre",
                "avoir",
                "aller",
                "manger",
                "boire",
                "pain",
                "eau",
                "lait",
                "viande",
                "poisson",
                "riz",
                "fruit",
                "legume",
                "maison",
                "ecole",
                "travail",
                "aujourdhui",
                "demain",
                "hier",
            ]
        ],
    },
]


# =============================================================================
# ALEMÃO (de) - Português → Alemão
# =============================================================================

DE_ITEMS: list[ItemSpec] = [
    {
        "key": "hallo",
        "kind": "word",
        "front_text": "Hallo",
        "example": "Hallo, Maria.",
        "glosses": {"pt-BR": "Olá", "en-US": "Hello"},
    },
    {
        "key": "guten_morgen",
        "kind": "phrase",
        "front_text": "Guten Morgen",
        "example": "Guten Morgen, Lehrer.",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "guten_tag",
        "kind": "phrase",
        "front_text": "Guten Tag",
        "example": "Guten Tag, wie geht's?",
        "glosses": {"pt-BR": "Boa tarde", "en-US": "Good day"},
    },
    {
        "key": "gute_nacht",
        "kind": "phrase",
        "front_text": "Gute Nacht",
        "example": "Gute Nacht, Mama.",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good night"},
    },
    {
        "key": "tschuss",
        "kind": "word",
        "front_text": "Tschüss",
        "example": "Tschüss, Freunde.",
        "glosses": {"pt-BR": "Tchau", "en-US": "Bye"},
    },
    {
        "key": "danke",
        "kind": "word",
        "front_text": "Danke",
        "example": "Danke für deine Hilfe.",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "bitte",
        "kind": "word",
        "front_text": "Bitte",
        "example": "— Danke. — Bitte.",
        "glosses": {"pt-BR": "De nada/Por favor", "en-US": "You're welcome/Please"},
    },
    {
        "key": "wie_gehts",
        "kind": "phrase",
        "front_text": "Wie geht's?",
        "example": "Wie geht's? — Gut, danke.",
        "glosses": {"pt-BR": "Como vai?", "en-US": "How are you?"},
    },
    {
        "key": "ich_heisse",
        "kind": "phrase",
        "front_text": "Ich heiße",
        "example": "Ich heiße Hans.",
        "glosses": {"pt-BR": "Me chamo", "en-US": "My name is"},
    },
    {
        "key": "eins",
        "kind": "word",
        "front_text": "Eins",
        "example": "Ich habe eins.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "zwei",
        "kind": "word",
        "front_text": "Zwei",
        "example": "Zwei Bücher.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "drei",
        "kind": "word",
        "front_text": "Drei",
        "example": "Drei Freunde.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "vier",
        "kind": "word",
        "front_text": "Vier",
        "example": "Vier Stühle.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "funf",
        "kind": "word",
        "front_text": "Fünf",
        "example": "Fünf Finger.",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "sechs",
        "kind": "word",
        "front_text": "Sechs",
        "example": "Sechs Eier.",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "sieben",
        "kind": "word",
        "front_text": "Sieben",
        "example": "Sieben Tage.",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "acht",
        "kind": "word",
        "front_text": "Acht",
        "example": "Acht Planeten.",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "neun",
        "kind": "word",
        "front_text": "Neun",
        "example": "Neun Leben.",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "zehn",
        "kind": "word",
        "front_text": "Zehn",
        "example": "Zehn Gebote.",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    {
        "key": "vater",
        "kind": "word",
        "front_text": "Vater",
        "example": "Mein Vater arbeitet.",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "mutter",
        "kind": "word",
        "front_text": "Mutter",
        "example": "Meine Mutter kocht.",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "bruder",
        "kind": "word",
        "front_text": "Bruder",
        "example": "Ich habe einen Bruder.",
        "glosses": {"pt-BR": "Irmão", "en-US": "Brother"},
    },
    {
        "key": "schwester",
        "kind": "word",
        "front_text": "Schwester",
        "example": "Meine Schwester lernt.",
        "glosses": {"pt-BR": "Irmã", "en-US": "Sister"},
    },
    {
        "key": "sein",
        "kind": "word",
        "front_text": "Sein",
        "example": "Ich bin Student.",
        "glosses": {"pt-BR": "Ser/Estar", "en-US": "To be"},
    },
    {
        "key": "haben",
        "kind": "word",
        "front_text": "Haben",
        "example": "Ich habe einen Hund.",
        "glosses": {"pt-BR": "Ter", "en-US": "To have"},
    },
    {
        "key": "gehen",
        "kind": "word",
        "front_text": "Gehen",
        "example": "Ich gehe zur Schule.",
        "glosses": {"pt-BR": "Ir", "en-US": "To go"},
    },
    {
        "key": "essen",
        "kind": "word",
        "front_text": "Essen",
        "example": "Ich esse Brot.",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "trinken",
        "kind": "word",
        "front_text": "Trinken",
        "example": "Ich trinke Wasser.",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
]

DE_UNITS: list[UnitSpec] = [
    {
        "slug": "begruessung",
        "title": "Begrüßung",
        "description": "Grußformeln.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "hallo-tschuss",
                "title": "Hallo / Tschüss",
                "order": 1,
                "xp": 10,
                "items": ["hallo", "guten_morgen", "guten_tag", "gute_nacht", "tschuss"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hallo",
                        "prompt": "Hallo",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "tschuss",
                        "prompt": "Tschüss",
                        "answer": "Tchau",
                        "options": None,
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "zahlen",
        "title": "Zahlen 1-10",
        "description": "Zählen bis zehn.",
        "level": "A1",
        "order": 2,
        "prerequisite": "begruessung",
        "lessons": [
            {
                "slug": "eins-bis-funf",
                "title": "Eins bis fünf",
                "order": 1,
                "xp": 10,
                "items": ["eins", "zwei", "drei", "vier", "funf"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "eins",
                        "prompt": "Eins",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "drei",
                        "prompt": "Was ist «drei»?",
                        "answer": "Drei",
                        "options": ["Drei", "Zwei", "Vier"],
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "familie",
        "title": "Familie",
        "description": "Familienmitglieder.",
        "level": "A1",
        "order": 3,
        "prerequisite": "zahlen",
        "lessons": [
            {
                "slug": "eltern-geschwister",
                "title": "Eltern & Geschwister",
                "order": 1,
                "xp": 10,
                "items": ["vater", "mutter", "bruder", "schwester"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "vater",
                        "prompt": "Vater",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "verben",
        "title": "Verben",
        "description": "Sein, haben, gehen, essen.",
        "level": "A2",
        "order": 4,
        "prerequisite": "familie",
        "lessons": [
            {
                "slug": "sein-haben",
                "title": "Sein & Haben",
                "order": 1,
                "xp": 15,
                "items": ["sein", "haben"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "sein",
                        "prompt": "Sein",
                        "answer": "Ser/Estar",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
]

DE_DECKS: list[DeckSpec] = [
    {
        "slug": "essentiel-a1",
        "title": "Deutsch A1 — Essentiel",
        "description": "Begrüßung, Zahlen, Familie.",
        "level": "A1",
        "items": [
            item["key"]
            for item in DE_ITEMS
            if item["key"]
            in [
                "hallo",
                "guten_morgen",
                "guten_tag",
                "gute_nacht",
                "tschuss",
                "danke",
                "bitte",
                "wie_gehts",
                "ich_heisse",
                "eins",
                "zwei",
                "drei",
                "vier",
                "funf",
                "sechs",
                "sieben",
                "acht",
                "neun",
                "zehn",
                "vater",
                "mutter",
                "bruder",
                "schwester",
            ]
        ],
    },
    {
        "slug": "verben-a2",
        "title": "Deutsch A2 — Verben",
        "description": "Sein, haben, gehen, essen.",
        "level": "A2",
        "items": [
            item["key"]
            for item in DE_ITEMS
            if item["key"]
            in [
                "sein",
                "haben",
                "gehen",
                "essen",
                "trinken",
                "brot",
                "wasser",
                "milch",
                "fleisch",
                "fisch",
                "reis",
                "obst",
                "gemuse",
                "haus",
                "schule",
                "arbeit",
                "markt",
                "park",
                "strand",
                "heute",
                "morgen",
                "gestern",
            ]
        ],
    },
]


# =============================================================================
# JAPONÊS (ja) - Português → Japonês
# =============================================================================

JA_ITEMS: list[ItemSpec] = [
    {
        "key": "konnichiwa",
        "kind": "word",
        "front_text": "こんにちは",
        "example": "こんにちは、マリアさん。",
        "glosses": {"pt-BR": "Olá/Bom dia", "en-US": "Hello/Good afternoon"},
    },
    {
        "key": "ohayou",
        "kind": "word",
        "front_text": "おはよう",
        "example": "おはよう、先生。",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "konbanwa",
        "kind": "word",
        "front_text": "こんばんは",
        "example": "こんばんは、お母さん。",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good evening"},
    },
    {
        "key": "sayonara",
        "kind": "word",
        "front_text": "さようなら",
        "example": "さようなら、友達。",
        "glosses": {"pt-BR": "Adeus/Tchau", "en-US": "Goodbye"},
    },
    {
        "key": "arigatou",
        "kind": "word",
        "front_text": "ありがとう",
        "example": "ありがとう、先生。",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "sumimasen",
        "kind": "word",
        "front_text": "すみません",
        "example": "すみません、水をください。",
        "glosses": {"pt-BR": "Com licença/Desculpe", "en-US": "Excuse me/Sorry"},
    },
    {
        "key": "ogenki",
        "kind": "phrase",
        "front_text": "お元気ですか？",
        "example": "お元気ですか？ — はい、元気です。",
        "glosses": {"pt-BR": "Como vai?", "en-US": "How are you?"},
    },
    {
        "key": "watashi_wa",
        "kind": "phrase",
        "front_text": "私は",
        "example": "私はマリアです。",
        "glosses": {"pt-BR": "Eu sou / Me chamo", "en-US": "I am / My name is"},
    },
    {
        "key": "ichi",
        "kind": "word",
        "front_text": "一",
        "example": "一冊。",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "ni",
        "kind": "word",
        "front_text": "二",
        "example": "二冊。",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "san",
        "kind": "word",
        "front_text": "三",
        "example": "三人。",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "yon",
        "kind": "word",
        "front_text": "四",
        "example": "四脚。",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "go",
        "kind": "word",
        "front_text": "五",
        "example": "五本。",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "roku",
        "kind": "word",
        "front_text": "六",
        "example": "六個。",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "nana",
        "kind": "word",
        "front_text": "七",
        "example": "七日。",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "hachi",
        "kind": "word",
        "front_text": "八",
        "example": "八個。",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "kyuu",
        "kind": "word",
        "front_text": "九",
        "example": "九人。",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "juu",
        "kind": "word",
        "front_text": "十",
        "example": "十個。",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    {
        "key": "chichi",
        "kind": "word",
        "front_text": "父",
        "example": "父は働いています。",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "haha",
        "kind": "word",
        "front_text": "母",
        "example": "母は料理をします。",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "ani",
        "kind": "word",
        "front_text": "兄",
        "example": "兄がいます。",
        "glosses": {"pt-BR": "Irmão mais velho", "en-US": "Older brother"},
    },
    {
        "key": "ane",
        "kind": "word",
        "front_text": "姉",
        "example": "姉は勉強します。",
        "glosses": {"pt-BR": "Irmã mais velha", "en-US": "Older sister"},
    },
    {
        "key": "desu",
        "kind": "word",
        "front_text": "です",
        "example": "学生です。",
        "glosses": {"pt-BR": "Ser/Estar (formal)", "en-US": "To be (polite)"},
    },
    {
        "key": "imasu",
        "kind": "word",
        "front_text": "います",
        "example": "犬がいます。",
        "glosses": {"pt-BR": "Ter/Existir (animados)", "en-US": "To have/exist (animate)"},
    },
    {
        "key": "arimasu",
        "kind": "word",
        "front_text": "あります",
        "example": "本があります。",
        "glosses": {"pt-BR": "Ter/Existir (inanimados)", "en-US": "To have/exist (inanimate)"},
    },
    {
        "key": "tabemasu",
        "kind": "word",
        "front_text": "食べます",
        "example": "パンを食べます。",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "nomimasu",
        "kind": "word",
        "front_text": "飲みます",
        "example": "水を飲みます。",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
]

JA_UNITS: list[UnitSpec] = [
    {
        "slug": "aisatsu",
        "title": "挨拶",
        "description": "基本の挨拶。",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "konnichiwa-sayonara",
                "title": "こんにちは / さようなら",
                "order": 1,
                "xp": 10,
                "items": ["konnichiwa", "ohayou", "konbanwa", "sayonara"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "konnichiwa",
                        "prompt": "こんにちは",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "sayonara",
                        "prompt": "さようなら",
                        "answer": "Tchau",
                        "options": None,
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "suuji",
        "title": "数字 1-10",
        "description": "数を数える。",
        "level": "A1",
        "order": 2,
        "prerequisite": "aisatsu",
        "lessons": [
            {
                "slug": "ichi-go",
                "title": "一〜五",
                "order": 1,
                "xp": 10,
                "items": ["ichi", "ni", "san", "yon", "go"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "ichi",
                        "prompt": "一",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "san",
                        "prompt": "「三」は？",
                        "answer": "三",
                        "options": ["三", "二", "四"],
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "kazoku",
        "title": "家族",
        "description": "家族の呼び方。",
        "level": "A1",
        "order": 3,
        "prerequisite": "suuji",
        "lessons": [
            {
                "slug": "oya-kyoudai",
                "title": "親と兄弟",
                "order": 1,
                "xp": 10,
                "items": ["chichi", "haha", "ani", "ane"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "chichi",
                        "prompt": "父",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "doushi",
        "title": "動詞",
        "description": "基本動詞。",
        "level": "A2",
        "order": 4,
        "prerequisite": "kazoku",
        "lessons": [
            {
                "slug": "desu-imasu",
                "title": "です / います",
                "order": 1,
                "xp": 15,
                "items": ["desu", "imasu", "arimasu"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "desu",
                        "prompt": "です",
                        "answer": "Ser/Estar (formal)",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
]

JA_DECKS: list[DeckSpec] = [
    {
        "slug": "essentiel-a1",
        "title": "日本語 A1 — Essentiel",
        "description": "挨拶、数字、家族。",
        "level": "A1",
        "items": [
            item["key"]
            for item in JA_ITEMS
            if item["key"]
            in [
                "konnichiwa",
                "ohayou",
                "konbanwa",
                "sayonara",
                "arigatou",
                "sumimasen",
                "ogenki",
                "watashi_wa",
                "ichi",
                "ni",
                "san",
                "yon",
                "go",
                "roku",
                "nana",
                "hachi",
                "kyuu",
                "juu",
                "chichi",
                "haha",
                "ani",
                "ane",
            ]
        ],
    },
    {
        "slug": "doushi-a2",
        "title": "日本語 A2 — 動詞",
        "description": "です、います、あります、食べます、飲みます。",
        "level": "A2",
        "items": [
            item["key"]
            for item in JA_ITEMS
            if item["key"] in ["desu", "imasu", "arimasu", "tabemasu", "nomimasu"]
        ],
    },
]


# =============================================================================
# COREANO (ko) - Português → Coreano
# =============================================================================

KO_ITEMS: list[ItemSpec] = [
    {
        "key": "annyeonghaseyo",
        "kind": "word",
        "front_text": "안녕하세요",
        "example": "안녕하세요, 마리아 씨.",
        "glosses": {"pt-BR": "Olá/Bom dia", "en-US": "Hello"},
    },
    {
        "key": "annyeong",
        "kind": "word",
        "front_text": "안녕",
        "example": "안녕, 잘 가.",
        "glosses": {"pt-BR": "Oi/Tchau (informal)", "en-US": "Hi/Bye (casual)"},
    },
    {
        "key": "gamsahamnida",
        "kind": "word",
        "front_text": "감사합니다",
        "example": "감사합니다, 선생님.",
        "glosses": {"pt-BR": "Obrigado (formal)", "en-US": "Thank you (polite)"},
    },
    {
        "key": "mianhamnida",
        "kind": "word",
        "front_text": "미안합니다",
        "example": "미안합니다, 늦었어요.",
        "glosses": {"pt-BR": "Desculpe (formal)", "en-US": "Sorry (polite)"},
    },
    {
        "key": "jeoneun",
        "kind": "phrase",
        "front_text": "저는",
        "example": "저는 마리아예요.",
        "glosses": {"pt-BR": "Eu sou / Me chamo", "en-US": "I am / My name is"},
    },
    {
        "key": "hana",
        "kind": "word",
        "front_text": "하나",
        "example": "하나, 둘, 셋.",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "dul",
        "kind": "word",
        "front_text": "둘",
        "example": "둘이 왔어요.",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "set",
        "kind": "word",
        "front_text": "셋",
        "example": "셋이 친구예요.",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "net",
        "kind": "word",
        "front_text": "넷",
        "example": "넷이 가족이에요.",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "daseot",
        "kind": "word",
        "front_text": "다섯",
        "example": "다섯 손가락.",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "yeoseot",
        "kind": "word",
        "front_text": "여섯",
        "example": "여섯 시예요.",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "ilgop",
        "kind": "word",
        "front_text": "일곱",
        "example": "일곱 마리.",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "yeodeol",
        "kind": "word",
        "front_text": "여덟",
        "example": "여덟 시.",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "ahop",
        "kind": "word",
        "front_text": "아홉",
        "example": "아홉 명.",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "yeol",
        "kind": "word",
        "front_text": "열",
        "example": "열 개.",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    {
        "key": "abeoji",
        "kind": "word",
        "front_text": "아버지",
        "example": "아버지가 일하세요.",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "eomeoni",
        "kind": "word",
        "front_text": "어머니",
        "example": "어머니가 요리하세요.",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "hyeong",
        "kind": "word",
        "front_text": "형",
        "example": "형이 있어요.",
        "glosses": {
            "pt-BR": "Irmão mais velho (homem fala)",
            "en-US": "Older brother (male speaker)",
        },
    },
    {
        "key": "nuna",
        "kind": "word",
        "front_text": "누나",
        "example": "누나가 예뻐요.",
        "glosses": {
            "pt-BR": "Irmã mais velha (homem fala)",
            "en-US": "Older sister (male speaker)",
        },
    },
    {
        "key": "isseoyo",
        "kind": "word",
        "front_text": "있어요",
        "example": "책이 있어요.",
        "glosses": {"pt-BR": "Ter/Existir", "en-US": "To have/exist"},
    },
    {
        "key": "meogeoyo",
        "kind": "word",
        "front_text": "먹어요",
        "example": "밥을 먹어요.",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "masyeoyo",
        "kind": "word",
        "front_text": "마셔요",
        "example": "물을 마셔요.",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
]

KO_UNITS: list[UnitSpec] = [
    {
        "slug": "insagye",
        "title": "인사",
        "description": "기본 인사말.",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "annyeong",
                "title": "안녕하세요 / 안녕",
                "order": 1,
                "xp": 10,
                "items": ["annyeonghaseyo", "annyeong"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "annyeonghaseyo",
                        "prompt": "안녕하세요",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "sutja",
        "title": "숫자 1-10",
        "description": "숫자 세기.",
        "level": "A1",
        "order": 2,
        "prerequisite": "insagye",
        "lessons": [
            {
                "slug": "hana-daseot",
                "title": "하나〜다섯",
                "order": 1,
                "xp": 10,
                "items": ["hana", "dul", "set", "net", "daseot"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "hana",
                        "prompt": "하나",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "gajok",
        "title": "가족",
        "description": "가족 호칭.",
        "level": "A1",
        "order": 3,
        "prerequisite": "sutja",
        "lessons": [
            {
                "slug": "bumo-hyeongje",
                "title": "부모 & 형제",
                "order": 1,
                "xp": 10,
                "items": ["abeoji", "eomeoni", "hyeong", "nuna"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "abeoji",
                        "prompt": "아버지",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "dongsa",
        "title": "동사",
        "description": "기본 동사.",
        "level": "A2",
        "order": 4,
        "prerequisite": "gajok",
        "lessons": [
            {
                "slug": "iss-eobs",
                "title": "있어요 / 없어요",
                "order": 1,
                "xp": 15,
                "items": ["isseoyo"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "isseoyo",
                        "prompt": "있어요",
                        "answer": "Ter/Existir",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
]

KO_DECKS: list[DeckSpec] = [
    {
        "slug": "essentiel-a1",
        "title": "한국어 A1 — Essentiel",
        "description": "인사, 숫자, 가족.",
        "level": "A1",
        "items": [
            item["key"]
            for item in KO_ITEMS
            if item["key"]
            in [
                "annyeonghaseyo",
                "annyeong",
                "gamsahamnida",
                "mianhamnida",
                "jeoneun",
                "hana",
                "dul",
                "set",
                "net",
                "daseot",
                "yeoseot",
                "ilgop",
                "yeodeol",
                "ahop",
                "yeol",
                "abeoji",
                "eomeoni",
                "hyeong",
                "nuna",
            ]
        ],
    },
    {
        "slug": "dongsa-a2",
        "title": "한국어 A2 — 동사",
        "description": "있어요, 먹어요, 마셔요.",
        "level": "A2",
        "items": [
            item["key"] for item in KO_ITEMS if item["key"] in ["isseoyo", "meogeoyo", "masyeoyo"]
        ],
    },
]


# =============================================================================
# CHINÊS (zh) - Português → Chinês (Mandarim)
# =============================================================================

ZH_ITEMS: list[ItemSpec] = [
    {
        "key": "nihao",
        "kind": "word",
        "front_text": "你好",
        "example": "你好，玛丽亚。",
        "glosses": {"pt-BR": "Olá", "en-US": "Hello"},
    },
    {
        "key": "zaoshang_hao",
        "kind": "phrase",
        "front_text": "早上好",
        "example": "早上好，老师。",
        "glosses": {"pt-BR": "Bom dia", "en-US": "Good morning"},
    },
    {
        "key": "wanan",
        "kind": "phrase",
        "front_text": "晚安",
        "example": "晚安，妈妈。",
        "glosses": {"pt-BR": "Boa noite", "en-US": "Good night"},
    },
    {
        "key": "zaijian",
        "kind": "word",
        "front_text": "再见",
        "example": "再见，朋友。",
        "glosses": {"pt-BR": "Tchau", "en-US": "Goodbye"},
    },
    {
        "key": "xiexie",
        "kind": "word",
        "front_text": "谢谢",
        "example": "谢谢您的帮助。",
        "glosses": {"pt-BR": "Obrigado", "en-US": "Thank you"},
    },
    {
        "key": "bukeqi",
        "kind": "phrase",
        "front_text": "不客气",
        "example": "— 谢谢。— 不客气。",
        "glosses": {"pt-BR": "De nada", "en-US": "You're welcome"},
    },
    {
        "key": "nihao_ma",
        "kind": "phrase",
        "front_text": "你好吗？",
        "example": "你好吗？— 我很好。",
        "glosses": {"pt-BR": "Como você está?", "en-US": "How are you?"},
    },
    {
        "key": "wo_jiao",
        "kind": "phrase",
        "front_text": "我叫",
        "example": "我叫玛丽亚。",
        "glosses": {"pt-BR": "Me chamo", "en-US": "My name is"},
    },
    {
        "key": "yi",
        "kind": "word",
        "front_text": "一",
        "example": "一本书。",
        "glosses": {"pt-BR": "Um", "en-US": "One"},
    },
    {
        "key": "er",
        "kind": "word",
        "front_text": "二",
        "example": "两个苹果。",
        "glosses": {"pt-BR": "Dois", "en-US": "Two"},
    },
    {
        "key": "san",
        "kind": "word",
        "front_text": "三",
        "example": "三个朋友。",
        "glosses": {"pt-BR": "Três", "en-US": "Three"},
    },
    {
        "key": "si",
        "kind": "word",
        "front_text": "四",
        "example": "四把椅子。",
        "glosses": {"pt-BR": "Quatro", "en-US": "Four"},
    },
    {
        "key": "wu",
        "kind": "word",
        "front_text": "五",
        "example": "五个手指。",
        "glosses": {"pt-BR": "Cinco", "en-US": "Five"},
    },
    {
        "key": "liu",
        "kind": "word",
        "front_text": "六",
        "example": "六个鸡蛋。",
        "glosses": {"pt-BR": "Seis", "en-US": "Six"},
    },
    {
        "key": "qi",
        "kind": "word",
        "front_text": "七",
        "example": "七天。",
        "glosses": {"pt-BR": "Sete", "en-US": "Seven"},
    },
    {
        "key": "ba",
        "kind": "word",
        "front_text": "八",
        "example": "八颗行星。",
        "glosses": {"pt-BR": "Oito", "en-US": "Eight"},
    },
    {
        "key": "jiu",
        "kind": "word",
        "front_text": "九",
        "example": "九条命。",
        "glosses": {"pt-BR": "Nove", "en-US": "Nine"},
    },
    {
        "key": "shi",
        "kind": "word",
        "front_text": "十",
        "example": "十诫。",
        "glosses": {"pt-BR": "Dez", "en-US": "Ten"},
    },
    {
        "key": "baba",
        "kind": "word",
        "front_text": "爸爸",
        "example": "爸爸在工作。",
        "glosses": {"pt-BR": "Pai", "en-US": "Father"},
    },
    {
        "key": "mama",
        "kind": "word",
        "front_text": "妈妈",
        "example": "妈妈在做饭。",
        "glosses": {"pt-BR": "Mãe", "en-US": "Mother"},
    },
    {
        "key": "gege",
        "kind": "word",
        "front_text": "哥哥",
        "example": "我有哥哥。",
        "glosses": {"pt-BR": "Irmão mais velho", "en-US": "Older brother"},
    },
    {
        "key": "jiejie",
        "kind": "word",
        "front_text": "姐姐",
        "example": "姐姐在学习。",
        "glosses": {"pt-BR": "Irmã mais velha", "en-US": "Older sister"},
    },
    {
        "key": "shi_copula",
        "kind": "word",
        "front_text": "是",
        "example": "我是学生。",
        "glosses": {"pt-BR": "Ser (verbo ligar)", "en-US": "To be (copula)"},
    },
    {
        "key": "you",
        "kind": "word",
        "front_text": "有",
        "example": "我有一只狗。",
        "glosses": {"pt-BR": "Ter", "en-US": "To have"},
    },
    {
        "key": "qu",
        "kind": "word",
        "front_text": "去",
        "example": "我去学校。",
        "glosses": {"pt-BR": "Ir", "en-US": "To go"},
    },
    {
        "key": "chi",
        "kind": "word",
        "front_text": "吃",
        "example": "我吃面包。",
        "glosses": {"pt-BR": "Comer", "en-US": "To eat"},
    },
    {
        "key": "he",
        "kind": "word",
        "front_text": "喝",
        "example": "喝水。",
        "glosses": {"pt-BR": "Beber", "en-US": "To drink"},
    },
]

ZH_UNITS: list[UnitSpec] = [
    {
        "slug": "zhaohu",
        "title": "问候",
        "description": "基本问候语。",
        "level": "A1",
        "order": 1,
        "prerequisite": None,
        "lessons": [
            {
                "slug": "nihao-zaijian",
                "title": "你好 / 再见",
                "order": 1,
                "xp": 10,
                "items": ["nihao", "zaoshang_hao", "wanan", "zaijian"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "nihao",
                        "prompt": "你好",
                        "answer": "Olá",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "flashcard",
                        "item": "zaijian",
                        "prompt": "再见",
                        "answer": "Tchau",
                        "options": None,
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "shuzi",
        "title": "数字 1-10",
        "description": "数数。",
        "level": "A1",
        "order": 2,
        "prerequisite": "zhaohu",
        "lessons": [
            {
                "slug": "yi-wu",
                "title": "一〜五",
                "order": 1,
                "xp": 10,
                "items": ["yi", "er", "san", "si", "wu"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "yi",
                        "prompt": "一",
                        "answer": "Um",
                        "options": None,
                        "order": 1,
                    },
                    {
                        "type": "multiple_choice",
                        "item": "san",
                        "prompt": "「三」é?",
                        "answer": "三",
                        "options": ["三", "二", "四"],
                        "order": 2,
                    },
                ],
            }
        ],
    },
    {
        "slug": "jiating",
        "title": "家庭",
        "description": "家庭成员。",
        "level": "A1",
        "order": 3,
        "prerequisite": "shuzi",
        "lessons": [
            {
                "slug": "fumu-xiongdi",
                "title": "父母 & 兄弟姐妹",
                "order": 1,
                "xp": 10,
                "items": ["baba", "mama", "gege", "jiejie"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "baba",
                        "prompt": "爸爸",
                        "answer": "Pai",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
    {
        "slug": "dongci",
        "title": "动词",
        "description": "基本动词。",
        "level": "A2",
        "order": 4,
        "prerequisite": "jiating",
        "lessons": [
            {
                "slug": "shi-you",
                "title": "是 / 有",
                "order": 1,
                "xp": 15,
                "items": ["shi_copula", "you"],
                "exercises": [
                    {
                        "type": "flashcard",
                        "item": "shi_copula",
                        "prompt": "是",
                        "answer": "Ser (verbo ligar)",
                        "options": None,
                        "order": 1,
                    }
                ],
            }
        ],
    },
]

ZH_DECKS: list[DeckSpec] = [
    {
        "slug": "essentiel-a1",
        "title": "中文 A1 — Essentiel",
        "description": "问候、数字、家庭。",
        "level": "A1",
        "items": [
            item["key"]
            for item in ZH_ITEMS
            if item["key"]
            in [
                "nihao",
                "zaoshang_hao",
                "wanan",
                "zaijian",
                "xiexie",
                "bukeqi",
                "nihao_ma",
                "wo_jiao",
                "yi",
                "er",
                "san",
                "si",
                "wu",
                "liu",
                "qi",
                "ba",
                "jiu",
                "shi",
                "baba",
                "mama",
                "gege",
                "jiejie",
            ]
        ],
    },
    {
        "slug": "dongci-a2",
        "title": "中文 A2 — 动词",
        "description": "是、有、去、吃、喝。",
        "level": "A2",
        "items": [
            item["key"]
            for item in ZH_ITEMS
            if item["key"] in ["shi_copula", "you", "qu", "chi", "he"]
        ],
    },
]


# =============================================================================
# AGREGAÇÃO POR IDIOMA ALVO
# =============================================================================

CONTENT_BY_LANG: dict[str, dict[str, list[Any]]] = {
    "es": {"items": ES_ITEMS, "units": ES_UNITS, "decks": ES_DECKS},
    "en": {"items": EN_ITEMS, "units": EN_UNITS, "decks": EN_DECKS},
    "fr": {"items": FR_ITEMS, "units": FR_UNITS, "decks": FR_DECKS},
    "de": {"items": DE_ITEMS, "units": DE_UNITS, "decks": DE_DECKS},
    "ja": {"items": JA_ITEMS, "units": JA_UNITS, "decks": JA_DECKS},
    "ko": {"items": KO_ITEMS, "units": KO_UNITS, "decks": KO_DECKS},
    "zh": {"items": ZH_ITEMS, "units": ZH_UNITS, "decks": ZH_DECKS},
}

TARGET_LANGUAGES = list(CONTENT_BY_LANG.keys())


async def seed_content(
    session: AsyncSession, *, target_language: str | None = None
) -> dict[str, int]:
    """Cria o conteúdo oficial para todos os idiomas (ou um específico)."""
    langs = [target_language] if target_language else TARGET_LANGUAGES
    total_overall = {"units": 0, "lessons": 0, "items": 0, "exercises": 0, "decks": 0}

    for lang in langs:
        if lang not in CONTENT_BY_LANG:
            continue

        existing = await session.scalar(
            select(Unit.id).where(Unit.target_language == lang).limit(1)
        )
        if existing is not None:
            continue

        data = CONTENT_BY_LANG[lang]
        ITEMS = data["items"]
        UNITS = data["units"]
        DECKS = data["decks"]

        total = {"units": 0, "lessons": 0, "items": 0, "exercises": 0, "decks": 0}
        unit_by_slug: dict[str, Unit] = {}
        lesson_by_slug: dict[str, Lesson] = {}

        # 1. Unidades
        for unit_spec in UNITS:
            unit = Unit(
                id=uuid7(),
                target_language=lang,
                level=unit_spec["level"],
                slug=unit_spec["slug"],
                title=unit_spec["title"],
                description=unit_spec["description"],
                order_index=unit_spec["order"],
                is_published=True,
            )
            session.add(unit)
            unit_by_slug[unit.slug] = unit
            total["units"] += 1
        await session.flush()

        for unit_spec in UNITS:
            prerequisite = unit_spec["prerequisite"]
            if prerequisite is not None:
                unit_by_slug[unit_spec["slug"]].prerequisite_id = unit_by_slug[prerequisite].id
        await session.flush()

        # 2. Lições
        for unit_spec in UNITS:
            unit = unit_by_slug[unit_spec["slug"]]
            for lesson_spec in unit_spec["lessons"]:
                lesson = Lesson(
                    id=uuid7(),
                    unit_id=unit.id,
                    slug=lesson_spec["slug"],
                    title=lesson_spec["title"],
                    order_index=lesson_spec["order"],
                    kind="lesson",
                    xp_reward=lesson_spec["xp"],
                    is_published=True,
                )
                session.add(lesson)
                lesson_by_slug[lesson.slug] = lesson
                total["lessons"] += 1
        await session.flush()

        # 3. Itens e glossas
        item_lesson: dict[str, tuple[Lesson, int]] = {}
        for unit_spec in UNITS:
            for lesson_spec in unit_spec["lessons"]:
                lesson = lesson_by_slug[lesson_spec["slug"]]
                for index, key in enumerate(lesson_spec["items"], start=1):
                    item_lesson[key] = (lesson, index)

        items_by_key: dict[str, Item] = {}
        for item_spec in ITEMS:
            lesson, index = item_lesson[item_spec["key"]]
            item = Item(
                id=uuid7(),
                lesson_id=lesson.id,
                kind=item_spec["kind"],
                front_text=item_spec["front_text"],
                example=item_spec["example"],
                order_index=index,
            )
            items_by_key[item_spec["key"]] = item
            session.add(item)
            total["items"] += 1
            for locale, gloss in item_spec["glosses"].items():
                session.add(ItemTranslation(item_id=item.id, locale=locale, gloss=gloss))
        await session.flush()

        # 4. Exercícios e baralhos
        for unit_spec in UNITS:
            for lesson_spec in unit_spec["lessons"]:
                lesson = lesson_by_slug[lesson_spec["slug"]]
                for exercise_spec in lesson_spec["exercises"]:
                    session.add(
                        Exercise(
                            id=uuid7(),
                            lesson_id=lesson.id,
                            item_id=items_by_key[exercise_spec["item"]].id,
                            type=exercise_spec["type"],
                            prompt=exercise_spec["prompt"],
                            answer=exercise_spec["answer"],
                            options=exercise_spec["options"],
                            order_index=exercise_spec["order"],
                        )
                    )
                    total["exercises"] += 1

        for deck_spec in DECKS:
            deck = Deck(
                id=uuid7(),
                target_language=lang,
                level=deck_spec["level"],
                slug=deck_spec["slug"],
                title=deck_spec["title"],
                description=deck_spec["description"],
                is_official=True,
            )
            session.add(deck)
            for key in deck_spec["items"]:
                session.add(DeckItem(deck_id=deck.id, item_id=items_by_key[key].id))
            total["decks"] += 1

        await session.commit()

        for k, v in total.items():
            total_overall[k] += v

    return total_overall
