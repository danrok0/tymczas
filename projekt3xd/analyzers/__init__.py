"""
Moduł analizy danych tekstowych dla systemu rekomendacji tras turystycznych.
Zawiera klasy do przetwarzania opisów tras i analizy recenzji użytkowników.
"""

from .text_processor import TextProcessor
from .review_analyzer import ReviewAnalyzer

__all__ = ['TextProcessor', 'ReviewAnalyzer'] 