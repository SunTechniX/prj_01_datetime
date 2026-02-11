import sys
import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Добавляем текущую директорию в PATH для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_data import (
    DATA_VARIANT_1, EXPECTED_VARIANT_1,
    DATA_VARIANT_2, EXPECTED_VARIANT_2,
    DATA_VARIANT_3, EXPECTED_VARIANT_3,
    DATA_VARIANT_4, EXPECTED_VARIANT_4,
    DATA_VARIANT_5, CURRENT_DATE
)


class TaskTester:
    """Запуск тестов для задачи сортировки транзакций"""
    
    def __init__(self):
        self.results = []
        self.score = 0
        self.max_score = 60  # 60 баллов за функциональные тесты
    
    def import_student_solution(self):
        """Импорт решения студента с обработкой ошибок"""
        try:
            import task
            return task.sort_transactions
        except Exception as e:
            self.results.append({
                "name": "Импорт решения студента",
                "status": "❌",
                "score": 0,
                "max_score": self.max_score,
                "details": f"Ошибка импорта модуля task.py: {type(e).__name__}: {e}"
            })
            return None
    
    def run_test_variant(self, name: str, data: List[Dict], expected: List[str], points: int):
        """Запуск одного варианта тестовых данных"""
        try:
            # Импортируем свежую версию функции (для изоляции тестов)
            import importlib
            import task
            importlib.reload(task)
            sort_func = task.sort_transactions
            
            # Запускаем сортировку
            result = sort_func(data)
            
            # Проверка типа результата
            if not isinstance(result, list):
                self.results.append({
                    "name": f"Тест {name}",
                    "status": "❌",
                    "score": 0,
                    "max_score": points,
                    "details": f"Функция вернула {type(result).__name__}, ожидался list"
                })
                return
            
            # Проверка количества элементов
            if len(result) != len(expected):
                self.results.append({
                    "name": f"Тест {name}",
                    "status": "❌",
                    "score": 0,
                    "max_score": points,
                    "details": f"Неверное количество элементов: {len(result)} вместо {len(expected)}"
                })
                return
            
            # Проверка порядка (допускаем небольшие вариации для одинаковых дат)
            mismatches = []
            for i, (actual, expected_op) in enumerate(zip(result, expected)):
                if actual != expected_op:
                    mismatches.append(f"Позиция {i+1}: '{actual}' вместо '{expected_op}'")
            
            if mismatches:
                # Частичный балл за частичное совпадение
                match_ratio = 1 - len(mismatches) / len(expected)
                earned = max(0, int(points * match_ratio * 0.7))  # 70% от потенциала за частичное совпадение
                
                details = f"Частичное совпадение ({len(expected) - len(mismatches)}/{len(expected)} позиций):\n" + \
                         "\n".join([f"  • {m}" for m in mismatches[:5]])
                
                self.results.append({
                    "name": f"Тест {name}",
                    "status": "⚠️",
                    "score": earned,
                    "max_score": points,
                    "details": details
                })
                self.score += earned
            else:
                self.results.append({
                    "name": f"Тест {name}",
                    "status": "✅",
                    "score": points,
                    "max_score": points,
                    "details": f"Полное совпадение порядка для {len(data)} транзакций"
                })
                self.score += points
                
        except Exception as e:
            self.results.append({
                "name": f"Тест {name}",
                "status": "❌",
                "score": 0,
                "max_score": points,
                "details": f"Исключение при выполнении: {type(e).__name__}: {e}"
            })
    
    def run_all_tests(self):
        """Запуск всех тестовых вариантов"""
        sort_func = self.import_student_solution()
        if sort_func is None:
            return self.results, 0, self.max_score
        
        # Тесты с разным весом (сложные наборы = больше баллов)
        self.run_test_variant("Вариант 1: Базовый", DATA_VARIANT_1, EXPECTED_VARIANT_1, 15)
        self.run_test_variant("Вариант 2: Граничные даты", DATA_VARIANT_2, EXPECTED_VARIANT_2, 15)
        self.run_test_variant("Вариант 3: Разный регистр и мусор", DATA_VARIANT_3, EXPECTED_VARIANT_3, 10)
        self.run_test_variant("Вариант 4: Только относительные даты", DATA_VARIANT_4, EXPECTED_VARIANT_4, 10)
        self.run_test_variant("Вариант 5: Максимальный набор", DATA_VARIANT_5[:15], EXPECTED_VARIANT_1 + EXPECTED_VARIANT_2[:5], 10)
        
        return self.results, self.score, self.max_score


if __name__ == "__main__":
    tester = TaskTester()
    results, score, max_score = tester.run_all_tests()
    
    print(f"\nФункциональное тестирование: {score}/{max_score} баллов")
    for r in results:
        print(f"\n{r['status']} {r['name']}: {r['score']}/{r['max_score']}")
        print(f"   {r['details']}")