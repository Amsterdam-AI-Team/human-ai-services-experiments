#!/usr/bin/env python3
"""
Simple integration test to verify API endpoints work with language parameter.
This is a smoke test - doesn't require the full server to be running.
"""

import json
from unittest.mock import Mock, patch
from models import (
    build_step_model, 
    create_burger_turn_model, 
    create_gemeente_turn_model,
    YapStartRequest
)
from intents import get_intents_for_language
from i18n import normalize_language_code, get_translation

def test_model_creation():
    """Test that models can be created with different languages."""
    print("Testing model creation with different languages...")
    
    # Test intent data structure
    test_intent = {
        "intent": "Test Intent",
        "intentcode": "test_intent",
        "steps": [
            {"title": "Step 1", "description": "Description 1"},
            {"title": "Step 2", "description": "Description 2"}
        ]
    }
    
    for lang in ["nl", "en", "fr"]:
        print(f"Testing {lang}...")
        
        # Test step model creation
        StepModel = build_step_model(test_intent, lang)
        print(f"  ✓ StepModel created for {lang}")
        
        # Test creating instances
        instance = StepModel()
        assert hasattr(instance, 'draft')
        assert hasattr(instance, 'vragen')
        print(f"  ✓ StepModel instance works for {lang}")
        
        # Test Burger and Gemeente models
        BurgerModel = create_burger_turn_model(lang)
        GemeenteModel = create_gemeente_turn_model(lang)
        
        burger_instance = BurgerModel(message="Test message")
        gemeente_instance = GemeenteModel(message="Test message", finished=False)
        
        assert burger_instance.message == "Test message"
        assert gemeente_instance.finished == False
        print(f"  ✓ Turn models work for {lang}")
    
    print("✓ All model creation tests passed")

def test_intent_localization():
    """Test that intents are properly localized."""
    print("\nTesting intent localization...")
    
    for lang in ["nl", "en", "fr"]:
        intents = get_intents_for_language(lang)
        
        # Check structure
        assert len(intents) > 0
        first_intent = intents[0]
        assert "intent" in first_intent
        assert "intentcode" in first_intent
        assert "steps" in first_intent
        
        # Check that content is localized (not just structure)
        intent_text = first_intent["intent"]
        if lang == "en":
            # Should contain English words
            assert any(word in intent_text.lower() for word in ["parking", "objection", "fine"])
        elif lang == "fr":
            # Should contain French words  
            assert any(word in intent_text.lower() for word in ["objection", "amende", "stationnement"])
        
        print(f"  ✓ Intents properly localized for {lang}")
    
    print("✓ Intent localization tests passed")

def test_yap_start_request():
    """Test YapStartRequest with language parameter."""
    print("\nTesting YapStartRequest with language...")
    
    # Test with different languages
    for lang in ["nl", "en", "fr"]:
        request = YapStartRequest(
            text="Test transcript",
            language=lang
        )
        
        assert request.text == "Test transcript"
        assert request.language == lang
        
        # Test normalization
        normalized = normalize_language_code(request.language)
        assert normalized == lang
        print(f"  ✓ YapStartRequest works for {lang}")
    
    # Test language normalization edge cases
    test_cases = [
        ("EN", "en"),
        ("en-US", "en"),
        ("fr-CA", "fr"),
        ("invalid", "nl"),
        (None, "nl")
    ]
    
    for input_lang, expected in test_cases:
        request = YapStartRequest(text="Test", language=input_lang)
        normalized = normalize_language_code(request.language)
        assert normalized == expected, f"Expected {expected}, got {normalized} for input {input_lang}"
        print(f"  ✓ Language normalization: {input_lang} -> {expected}")
    
    print("✓ YapStartRequest tests passed")

def test_translation_fallbacks():
    """Test that translation fallbacks work correctly."""
    print("\nTesting translation fallbacks...")
    
    # Test with valid keys
    for lang in ["nl", "en", "fr"]:
        result = get_translation(lang, "responses.all_steps_completed", "fallback")
        assert result != "fallback"  # Should find the translation
        print(f"  ✓ Translation found for {lang}")
    
    # Test with invalid key (should use default)
    result = get_translation("en", "invalid.key.path", "my_default")
    assert result == "my_default"
    print("  ✓ Fallback to default works")
    
    # Test with invalid language (should fallback to Dutch)
    result = get_translation("invalid_lang", "responses.all_steps_completed", "fallback")
    assert result != "fallback"  # Should find Dutch translation
    print("  ✓ Language fallback works")
    
    print("✓ Translation fallback tests passed")

if __name__ == "__main__":
    test_model_creation()
    test_intent_localization()
    test_yap_start_request()
    test_translation_fallbacks()
    print("\n🎉 All API i18n integration tests passed!")