import streamlit as st
from googletrans import Translator
from typing import Dict, Any

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

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language."""
    if target_lang == 'en':
        return text
        
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        st.warning(f"Translation error: {str(e)}")
        return text

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
