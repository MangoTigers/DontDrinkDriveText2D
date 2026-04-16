from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .config import Difficulty


class Language(Enum):
    NORWEGIAN = "nb"
    ENGLISH = "en"


@dataclass(frozen=True)
class PhoneTaskTemplate:
    sender: str
    message: str
    accepted_replies: tuple[str, ...]


LANGUAGE_NAMES = {
    Language.NORWEGIAN: "Norsk",
    Language.ENGLISH: "English",
}

TEXTS = {
    Language.NORWEGIAN: {
        "app_title": "Dont Drink & Drive & Text",
        "main_subtitle": "Hold deg trygg i trafikken",
        "menu_start_game": "Start spill",
        "menu_settings": "Innstillinger",
        "menu_exit": "Avslutt",
        "main_instructions": "OPP/NED: meny | VENSTRE/HØYRE: bil | ENTER: velg",
        "settings_title": "Innstillinger",
        "select_difficulty": "Velg vanskelighet:",
        "choose_car": "Velg bil:",
        "audio_settings": "Lydinnstillinger:",
        "sound_effects": "Lydeffekter (D for å slå av/på)",
        "music": "Musikk (M for å slå av/på)",
        "credits_button": "Kreditering (C)",
        "back_to_menu": "← Tilbake til menyen",
        "settings_instructions": "Bruk VENSTRE/HØYRE for bil, og ESC for å gå tilbake",
        "credits_title": "Kreditering",
        "credits_attribution": "Bil-sprites er hentet fra:",
        "credits_helper": "Klikk på lenken eller trykk C for å åpne i nettleser",
        "credits_back": "Tilbake",
        "credits_tip": "ESC eller Backspace går tilbake til Innstillinger",
        "language_label": "Språk:",
        "paused_title": "PAUSE",
        "pause_settings_title": "Pauseinnstillinger",
        "pause_audio_settings": "Lydinnstillinger:",
        "pause_sound_effects": "Lydeffekter (D)",
        "pause_music": "Musikk (M)",
        "pause_back": "← Tilbake",
        "pause_resume": "Fortsett",
        "pause_main_menu": "Hovedmeny",
        "pause_instructions": "ESC eller Backspace går tilbake til Innstillinger",
        "phone_title": "Telefon",
        "phone_from_prefix": "Fra:",
        "phone_reply_prompt": "Trykk svar på tastaturet:",
        "phone_objective_prefix": "Mål:",
        "phone_objective_suffix": "meldinger sendt",
        "phone_sent": "Sendt",
        "phone_feedback_title": "Hæ? Mente du å si",
        "phone_swipe_hint": "↑ Sveip opp for å lukke",
        "phone_drag_label": "Slipp når den er dratt opp",
        "phone_drag_tip": "Trekk denne opp",
        "phone_space_label": "MELLOMROM",
        "phone_backspace_label": "SLETT",
        "phone_send_label": "SEND",
        "difficulty_easy_label": "Lett",
        "difficulty_medium_label": "Middels",
        "difficulty_hard_label": "Vanskelig",
        "difficulty_easy_info": "Saktere trafikk, lengre reaksjonstid",
        "difficulty_medium_info": "Standard vanskelighetsgrad, balansert utfordring",
        "difficulty_hard_info": "Aggressiv trafikk, minimal reaksjonstid",
        "game_difficulty": "Vanskelighet:",
        "game_speed": "Fart:",
        "game_time": "Tid:",
        "game_dodged": "Unngåtte biler:",
        "game_drunk": "Beruselse",
        "game_controls": "Styr: A/D eller piler | Drikk: Mellomrom",
        "game_drink_prompt": "Feststemning! Trykk SPACE for å drikke",
        "crash_title": "Krasj",
        "crash_difficulty": "Vanskelighet:",
        "crash_reason_collision": "Du kolliderte med en annen bil.",
        "crash_reason_drunk": "Sterk beruselse førte til total kontrollsvikt.",
        "crash_reason_time": "Tretthet og beruselse endte i en uunngåelig ulykke.",
        "crash_line_1": "Konsekvenser kan være skader, straffesak,",
        "crash_line_2": "økonomisk belastning, traumer og tapt tillit.",
        "crash_line_3": "Ingen melding eller drink er verdt et liv.",
        "crash_stats": "Du holdt ut {seconds:.1f}s, sendte {texts} meldinger og unngikk {cars} biler.",
        "crash_reminder": "R: Prøv igjen | M: Hovedmeny | ESC: Avslutt",
    },
    Language.ENGLISH: {
        "app_title": "Dont Drink & Drive & Text",
        "main_subtitle": "Stay safe on the road",
        "menu_start_game": "Start Game",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "main_instructions": "UP/DOWN: menu | LEFT/RIGHT: car | ENTER: select",
        "settings_title": "Settings",
        "select_difficulty": "Select Difficulty:",
        "choose_car": "Choose Car:",
        "audio_settings": "Audio Settings:",
        "sound_effects": "Sound Effects (D to toggle)",
        "music": "Music (M to toggle)",
        "credits_button": "Credits (C)",
        "back_to_menu": "← Back to Menu",
        "settings_instructions": "Use LEFT/RIGHT to choose car, and ESC to return",
        "credits_title": "Credits",
        "credits_attribution": "Car sprite attribution:",
        "credits_helper": "Click the link box or press C to open in browser",
        "credits_back": "Back",
        "credits_tip": "ESC or Backspace returns to Settings",
        "language_label": "Language:",
        "paused_title": "PAUSED",
        "pause_settings_title": "Pause Settings",
        "pause_audio_settings": "Audio Settings:",
        "pause_sound_effects": "Sound Effects (D)",
        "pause_music": "Music (M)",
        "pause_back": "← Back",
        "pause_resume": "Resume",
        "pause_main_menu": "Main Menu",
        "pause_instructions": "ESC or Backspace returns to Settings",
        "phone_title": "Phone",
        "phone_from_prefix": "From:",
        "phone_reply_prompt": "Type a reply on the keyboard:",
        "phone_objective_prefix": "Goal:",
        "phone_objective_suffix": "messages sent",
        "phone_sent": "Sent",
        "phone_feedback_title": "Huh? Did you mean",
        "phone_swipe_hint": "↑ Swipe up to close",
        "phone_drag_label": "Release when dragged up",
        "phone_drag_tip": "Pull this up",
        "phone_space_label": "SPACE",
        "phone_backspace_label": "DELETE",
        "phone_send_label": "SEND",
        "difficulty_easy_label": "Easy",
        "difficulty_medium_label": "Medium",
        "difficulty_hard_label": "Hard",
        "difficulty_easy_info": "Slower traffic, longer reaction time",
        "difficulty_medium_info": "Standard difficulty, balanced challenge",
        "difficulty_hard_info": "Aggressive traffic, minimal reaction time",
        "game_difficulty": "Difficulty:",
        "game_speed": "Speed:",
        "game_time": "Time:",
        "game_dodged": "Dodged cars:",
        "game_drunk": "Intoxication",
        "game_controls": "Controls: A/D or arrows | Drink: Space",
        "game_drink_prompt": "Party mood! Press SPACE to drink",
        "crash_title": "Crash",
        "crash_difficulty": "Difficulty:",
        "crash_reason_collision": "You collided with another car.",
        "crash_reason_drunk": "Severe intoxication caused total loss of control.",
        "crash_reason_time": "Fatigue and intoxication ended in an unavoidable crash.",
        "crash_line_1": "Consequences can include injury, charges,",
        "crash_line_2": "financial strain, trauma, and broken trust.",
        "crash_line_3": "No message or drink is worth a life.",
        "crash_stats": "You lasted {seconds:.1f}s, sent {texts} messages, and dodged {cars} cars.",
        "crash_reminder": "R: Try again | M: Main Menu | ESC: Quit",
    },
}

DIFFICULTY_LABELS = {
    Language.NORWEGIAN: {
        Difficulty.EASY: "Lett",
        Difficulty.MEDIUM: "Middels",
        Difficulty.HARD: "Vanskelig",
    },
    Language.ENGLISH: {
        Difficulty.EASY: "Easy",
        Difficulty.MEDIUM: "Medium",
        Difficulty.HARD: "Hard",
    },
}

DIFFICULTY_INFOS = {
    Language.NORWEGIAN: {
        Difficulty.EASY: "Saktere trafikk, lengre reaksjonstid",
        Difficulty.MEDIUM: "Standard vanskelighetsgrad, balansert utfordring",
        Difficulty.HARD: "Aggressiv trafikk, minimal reaksjonstid",
    },
    Language.ENGLISH: {
        Difficulty.EASY: "Slower traffic, longer reaction time",
        Difficulty.MEDIUM: "Standard difficulty, balanced challenge",
        Difficulty.HARD: "Aggressive traffic, minimal reaction time",
    },
}

PHONE_TASKS = {
    Language.NORWEGIAN: (
        PhoneTaskTemplate("Mamma", "Kommer du hjem til middag klokka 8?", ("ja", "kommer snart")),
        PhoneTaskTemplate("Sjef", "Trenger statusoppdatering nå", ("jobber med det", "på saken")),
        PhoneTaskTemplate("Venn", "Hvor er du nå?", ("på vei", "nesten fremme")),
        PhoneTaskTemplate("Lagchat", "Kan du bekrefte at du kommer?", ("bekreftet", "jeg kommer")),
        PhoneTaskTemplate("Trener", "Kommer du på trening i morgen?", ("ja jeg må", "ja")),
        PhoneTaskTemplate("Nabo", "Kan du kjøpe melk?", ("klart det", "ok")),
        PhoneTaskTemplate("Partner", "Ring meg når du er ledig", ("kjører nå", "ringer snart")),
        PhoneTaskTemplate("Klassen", "Har du levert oppgaven?", ("levert", "ja levert")),
        PhoneTaskTemplate("Storesøster", "Kan du svare når du er hjemme?", ("jeg er hjemme nå", "hjemme nå")),
        PhoneTaskTemplate("Pappa", "Hvor skal du etterpå?", ("hjem", "til en fest")),
    ),
    Language.ENGLISH: (
        PhoneTaskTemplate("Mom", "Are you coming home for dinner at 8?", ("yes", "soon")),
        PhoneTaskTemplate("Boss", "Need an update now", ("working on it", "on it")),
        PhoneTaskTemplate("Friend", "Where are you now?", ("on my way", "almost there")),
        PhoneTaskTemplate("Group chat", "Can you confirm you're coming?", ("confirmed", "i'm coming")),
        PhoneTaskTemplate("Coach", "Are you coming to practice tomorrow?", ("yes i have to", "yes")),
        PhoneTaskTemplate("Neighbor", "Can you buy milk?", ("sure", "ok")),
        PhoneTaskTemplate("Partner", "Call me when you're free", ("driving now", "calling soon")),
        PhoneTaskTemplate("Class chat", "Did you hand in the assignment?", ("submitted", "yes submitted")),
        PhoneTaskTemplate("Big sister", "Can you reply when you're home?", ("i'm home now", "home now")),
        PhoneTaskTemplate("Dad", "Where are you going after this?", ("home", "to a party")),
    ),
}


def t(language: Language, key: str) -> str:
    return TEXTS[language][key]


def language_name(language: Language) -> str:
    return LANGUAGE_NAMES[language]


def difficulty_label(language: Language, difficulty: Difficulty) -> str:
    return DIFFICULTY_LABELS[language][difficulty]


def difficulty_info(language: Language, difficulty: Difficulty) -> str:
    return DIFFICULTY_INFOS[language][difficulty]


def phone_task_templates(language: Language) -> tuple[PhoneTaskTemplate, ...]:
    return PHONE_TASKS[language]


def crash_reason(language: Language, key: str) -> str:
    return TEXTS[language][key]


def crash_consequence_lines(language: Language) -> tuple[str, str, str]:
    return (
        TEXTS[language]["crash_line_1"],
        TEXTS[language]["crash_line_2"],
        TEXTS[language]["crash_line_3"],
    )
