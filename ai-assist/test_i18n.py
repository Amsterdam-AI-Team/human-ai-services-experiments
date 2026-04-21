#!/usr/bin/env python3
"""
Simple test script to verify that the i18n system is working correctly.
"""

import json
from i18n import (
    get_supported_languages,
    normalize_language_code,
    get_translation,
    get_system_prompt,
    get_intents,
    get_language_suffix
)

def test_basic_functionality():
    """Test basic i18n functionality."""
    print("Testing i18n system...")
    
    # Test supported languages
    languages = get_supported_languages()
    print(f"Supported languages: {languages}")
    assert "nl" in languages
    assert "en" in languages  
    assert "fr" in languages
    
    # Test language normalization
    assert normalize_language_code("en") == "en"
    assert normalize_language_code("EN") == "en"
    assert normalize_language_code("en-US") == "en"
    assert normalize_language_code("invalid") == "nl"
    assert normalize_language_code(None) == "nl"
    print("✓ Language normalization works")
    
    # Test translations
    for lang in languages:
        error_msg = get_translation(lang, "responses.error_audio_required", "fallback")
        print(f"Audio error message ({lang}): {error_msg}")
        assert error_msg != "fallback"  # Should find translation
    print("✓ Basic translations work")
    
    # Test system prompts
    for lang in languages:
        burger_prompt = get_system_prompt(lang, "burger_system")
        print(f"Burger system context ({lang}): {burger_prompt['context'][:50]}...")
        assert "context" in burger_prompt
        assert "objective" in burger_prompt
    print("✓ System prompts work")
    
    # Test intents
    for lang in languages:
        intents = get_intents(lang)
        print(f"Number of intents ({lang}): {len(intents)}")
        assert len(intents) > 0
        assert "intent" in intents[0]
        assert "intentcode" in intents[0]
    print("✓ Intent translations work")
    
    # Test language suffixes
    for lang in languages:
        suffix = get_language_suffix(lang)
        print(f"Language suffix ({lang}): {suffix}")
        assert len(suffix) > 0
    print("✓ Language suffixes work")
    
    print("\n🎉 All i18n tests passed!")

def test_translation_consistency():
    """Test that all languages have consistent translation keys."""
    print("\nTesting translation consistency...")
    
    languages = get_supported_languages()
    base_lang = "nl"
    
    # Load base language translations to get all keys
    from i18n import load_translations
    base_translations = load_translations(base_lang)
    
    def get_all_keys(d, prefix=""):
        """Recursively get all translation keys."""
        keys = []
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(get_all_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys
    
    base_keys = set(get_all_keys(base_translations))
    print(f"Base language ({base_lang}) has {len(base_keys)} translation keys")
    
    for lang in languages:
        if lang == base_lang:
            continue
            
        lang_translations = load_translations(lang)
        lang_keys = set(get_all_keys(lang_translations))
        
        missing_keys = base_keys - lang_keys
        extra_keys = lang_keys - base_keys
        
        print(f"Language {lang}: {len(lang_keys)} keys")
        if missing_keys:
            print(f"  Missing keys: {missing_keys}")
        if extra_keys:
            print(f"  Extra keys: {extra_keys}")
        
        # Allow some flexibility, but most keys should be present
        coverage = len(lang_keys & base_keys) / len(base_keys)
        print(f"  Coverage: {coverage:.1%}")
        assert coverage > 0.8  # At least 80% coverage
    
    print("✓ Translation consistency check passed")

if __name__ == "__main__":
    test_basic_functionality()
    test_translation_consistency()
    print("\n✅ All tests completed successfully!")