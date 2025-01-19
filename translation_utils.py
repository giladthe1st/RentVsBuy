import streamlit as st
from googletrans import Translator
from typing import Dict, Any
from functools import lru_cache

# Create a single translator instance
translator = Translator()

# Cache for translations
translation_cache: Dict[str, Dict[str, str]] = {}

def get_translations() -> Dict[str, Dict[str, str]]:
    """Get translations for all supported languages."""
    return {
        'en': {'name': 'English', 'code': 'en'},
        'he': {'name': 'עברית', 'code': 'he'},
        'ru': {'name': 'Русский', 'code': 'ru'}
    }

def create_language_selector():
    """Create a language selector in the sidebar."""
    translations = get_translations()
    
    # Create a container in the top right
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col2:
            current_lang = st.selectbox(
                '',
                options=list(translations.keys()),
                format_func=lambda x: translations[x]['name'],
                key='language_selector'
            )
    
    return current_lang

@lru_cache(maxsize=1000)
def cached_translate(text: str, target_lang: str) -> str:
    """Cached translation function."""
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception:
        return text

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language using cache."""
    if target_lang == 'en':
        return text
    
    # Create cache key
    cache_key = f"{text}:{target_lang}"
    
    # Check cache first
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    # Translate and cache result
    translated = cached_translate(text, target_lang)
    translation_cache[cache_key] = translated
    return translated

def translate_number_input(text: str, target_lang: str, **kwargs) -> Any:
    """Create a translated number input."""
    translated_label = translate_text(text, target_lang)
    translated_help = translate_text(kwargs.get('help', ''), target_lang) if 'help' in kwargs else None
    
    if 'help' in kwargs:
        kwargs['help'] = translated_help
    
    return st.number_input(translated_label, **kwargs)

def translate_slider(text: str, target_lang: str, **kwargs) -> Any:
    """Create a translated slider."""
    translated_label = translate_text(text, target_lang)
    translated_help = translate_text(kwargs.get('help', ''), target_lang) if 'help' in kwargs else None
    
    if 'help' in kwargs:
        kwargs['help'] = translated_help
    
    return st.slider(translated_label, **kwargs)
