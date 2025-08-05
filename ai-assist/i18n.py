"""
Internationalization utilities for the AI assistant backend.
Handles translation loading and text retrieval for supported languages.
"""

import json
import os
from typing import Dict, Any, Optional
from functools import lru_cache

# Supported languages
SUPPORTED_LANGUAGES = ["nl", "en", "fr"]
DEFAULT_LANGUAGE = "nl"

# Cache for loaded translations
_translations_cache: Dict[str, Dict[str, Any]] = {}

def get_supported_languages() -> list[str]:
    """Return list of supported language codes."""
    return SUPPORTED_LANGUAGES.copy()

def is_language_supported(lang_code: str) -> bool:
    """Check if a language code is supported."""
    return lang_code in SUPPORTED_LANGUAGES

def normalize_language_code(lang_code: Optional[str]) -> str:
    """
    Normalize and validate language code.
    Returns default language if code is invalid or None.
    """
    if not lang_code:
        return DEFAULT_LANGUAGE
    
    # Handle common variations
    lang_code = lang_code.lower().strip()
    if lang_code in SUPPORTED_LANGUAGES:
        return lang_code
    
    # Handle language-country codes (e.g., "en-US" -> "en")
    if "-" in lang_code:
        base_lang = lang_code.split("-")[0]
        if base_lang in SUPPORTED_LANGUAGES:
            return base_lang
    
    return DEFAULT_LANGUAGE

@lru_cache(maxsize=10)
def load_translations(lang_code: str) -> Dict[str, Any]:
    """
    Load translations for a specific language.
    Returns cached translations if already loaded.
    """
    if lang_code in _translations_cache:
        return _translations_cache[lang_code]
    
    lang_code = normalize_language_code(lang_code)
    
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    translations_path = os.path.join(current_dir, "translations", f"{lang_code}.json")
    
    try:
        with open(translations_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
            _translations_cache[lang_code] = translations
            return translations
    except FileNotFoundError:
        # Fallback to default language
        if lang_code != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        raise RuntimeError(f"Translation file not found: {translations_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in translation file {translations_path}: {e}")

def get_translation(lang_code: str, key_path: str, default: Optional[str] = None) -> str:
    """
    Get a translation by dot-notation key path.
    
    Args:
        lang_code: Language code (e.g., "en", "nl", "fr")
        key_path: Dot-notation path to the translation (e.g., "responses.all_steps_completed")
        default: Default value if translation not found
    
    Returns:
        Translated string or default value
    """
    lang_code = normalize_language_code(lang_code)
    translations = load_translations(lang_code)
    
    # Navigate through nested dictionary using dot notation
    current = translations
    for key in key_path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            if default is not None:
                return default
            # Fallback to default language if available
            if lang_code != DEFAULT_LANGUAGE:
                return get_translation(DEFAULT_LANGUAGE, key_path, default)
            raise KeyError(f"Translation key not found: {key_path} for language {lang_code}")
    
    return str(current)

def get_system_prompt(lang_code: str, prompt_type: str) -> Dict[str, str]:
    """
    Get system prompt components for a specific language.
    
    Args:
        lang_code: Language code
        prompt_type: Type of prompt ("juridisch_medewerker", "burger_system", "gemeente_system")
    
    Returns:
        Dictionary with prompt components
    """
    lang_code = normalize_language_code(lang_code)
    translations = load_translations(lang_code)
    
    prompt_data = translations.get("system_prompts", {}).get(prompt_type, {})
    if not prompt_data:
        # Fallback to default language
        if lang_code != DEFAULT_LANGUAGE:
            return get_system_prompt(DEFAULT_LANGUAGE, prompt_type)
        raise KeyError(f"System prompt not found: {prompt_type} for language {lang_code}")
    
    return prompt_data

def get_intents(lang_code: str) -> list[Dict[str, Any]]:
    """
    Get translated intent definitions for a specific language.
    
    Args:
        lang_code: Language code
    
    Returns:
        List of intent dictionaries with translated content
    """
    lang_code = normalize_language_code(lang_code)
    translations = load_translations(lang_code)
    
    intents = translations.get("intents", [])
    if not intents and lang_code != DEFAULT_LANGUAGE:
        # Fallback to default language
        return get_intents(DEFAULT_LANGUAGE)
    
    return intents

def get_language_suffix(lang_code: str) -> str:
    """
    Get the language-specific suffix for prompts (e.g., "Answer strictly in English").
    
    Args:
        lang_code: Language code
    
    Returns:
        Language suffix string
    """
    return get_translation(lang_code, "language_suffix", "Answer strictly in Dutch")

def get_language_name(lang_code: str) -> str:
    """
    Get the full language name for a language code.
    
    Args:
        lang_code: Language code
        
    Returns:
        Full language name
    """
    language_names = {
        "nl": "Dutch",
        "en": "English", 
        "fr": "French"
    }
    return language_names.get(normalize_language_code(lang_code), "Dutch")

def extract_language_from_request(request_data: Dict[str, Any]) -> str:
    """
    Extract language parameter from request data.
    Looks for 'language' key in various formats.
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Normalized language code
    """
    # Look for language in various possible locations
    lang_code = request_data.get("language")
    
    if not lang_code:
        # Check for common alternative keys
        lang_code = request_data.get("lang") or request_data.get("locale")
    
    return normalize_language_code(lang_code)