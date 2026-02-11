import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple


class CodeAnalyzer:
    """Анализ качества кода в task.py через AST"""
    
    def __init__(self, filepath: str = "task.py"):
        self.filepath = Path(filepath)
        self.tree = None
        self.source = ""
        self.results = []
        self.score = 0
        self.max_score = 40  # Максимум баллов за качество кода
    
    def load_code(self) -> bool:
        """Загрузка и парсинг кода"""
        try:
            self.source = self.filepath.read_text(encoding="utf-8")
            self.tree = ast.parse(self.source)
            return True
        except Exception as e:
            self.results.append({
                "name": "Загрузка кода",
                "status": "❌",
                "score": 0,
                "max_score": self.max_score,
                "details": f"Ошибка парсинга Python кода: {e}"
            })
            return False
    
    def check_function_exists(self) -> Dict:
        """Проверка наличия функции sort_transactions с правильной сигнатурой"""
        has_function = False
        correct_signature = False
        line_no = None
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) and node.name == "sort_transactions":
                has_function = True
                line_no = node.lineno
                
                # Проверка аргументов: должен быть один аргумент transactions
                if len(node.args.args) == 1 and node.args.args[0].arg == "transactions":
                    correct_signature = True
                
                break
        
        if not has_function:
            return {
                "name": "Наличие функции sort_transactions",
                "status": "❌",
                "score": 0,
                "max_score": 10,
                "details": "Функция sort_transactions не найдена в коде"
            }
        
        if not correct_signature:
            return {
                "name": "Корректная сигнатура функции",
                "status": "⚠️",
                "score": 5,
                "max_score": 10,
                "details": f"Функция найдена на строке {line_no}, но сигнатура не соответствует требованиям (ожидается: def sort_transactions(transactions: List[Dict[str, str]]) -> List[str])"
            }
        
        self.score += 10
        return {
            "name": "Наличие и сигнатура функции sort_transactions",
            "status": "✅",
            "score": 10,
            "max_score": 10,
            "details": f"Функция найдена на строке {line_no} с корректной сигнатурой"
        }
    
    def check_naming_conventions(self) -> Dict:
        """Проверка стиля именования (snake_case)"""
        violations = []
        
        # Проверка переменных и функций внутри функции sort_transactions
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and node.name != "sort_transactions":
                    violations.append(f"Функция '{node.name}' на строке {node.lineno} должна быть в snake_case")
            
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.id):
                    violations.append(f"Переменная '{node.id}' на строке {node.lineno} должна быть в snake_case")
        
        if violations:
            details = "\n".join([f"  • {v}" for v in violations[:5]])  # Первые 5 нарушений
            if len(violations) > 5:
                details += f"\n  ... и ещё {len(violations) - 5} нарушений"
            return {
                "name": "Стиль именования (snake_case)",
                "status": "⚠️",
                "score": max(0, 5 - len(violations)),
                "max_score": 5,
                "details": details
            }
        
        self.score += 5
        return {
            "name": "Стиль именования (snake_case)",
            "status": "✅",
            "score": 5,
            "max_score": 5,
            "details": "Все имена переменных и функций соответствуют стилю snake_case"
        }
    
    def check_no_hardcoded_magic_values(self) -> Dict:
        """Проверка отсутствия "магических" значений (лучше использовать константы)"""
        # Ищем числа > 12 (возможно месяцы) или специфичные строки
        magic_strings = ["январь", "февраль", "января", "февраля", "сегодня", "вчера", "прошлом месяце"]
        found_magic = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Str) or (hasattr(ast, "Constant") and isinstance(node, ast.Constant) and isinstance(node.value, str)):
                value = node.s if isinstance(node, ast.Str) else node.value
                if any(m in value.lower() for m in magic_strings):
                    found_magic.append((value, node.lineno))
        
        # Допустимо иметь словарь месяцев, но не цепочку if/elif с месяцами
        if len(found_magic) > 8:  # Эвристика: много вхождений = вероятно цепочка сравнений
            details = f"Обнаружено {len(found_magic)} вхождений названий месяцев/дат в коде. Рекомендуется использовать словарь для хранения месяцев вместо цепочки сравнений."
            return {
                "name": "Отсутствие магических значений",
                "status": "⚠️",
                "score": 3,
                "max_score": 5,
                "details": details
            }
        
        self.score += 5
        return {
            "name": "Отсутствие магических значений",
            "status": "✅",
            "score": 5,
            "max_score": 5,
            "details": "Код использует структурированный подход (словари/константы) вместо магических строк"
        }
    
    def check_error_handling(self) -> Dict:
        """Проверка наличия обработки ошибок (try/except)"""
        has_try_except = False
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Try):
                has_try_except = True
                break
        
        if not has_try_except:
            return {
                "name": "Обработка ошибок (try/except)",
                "status": "⚠️",
                "score": 3,
                "max_score": 5,
                "details": "В коде отсутствуют блоки try/except. Рекомендуется обрабатывать ошибки парсинга дат для повышения надёжности."
            }
        
        self.score += 5
        return {
            "name": "Обработка ошибок (try/except)",
            "status": "✅",
            "score": 5,
            "max_score": 5,
            "details": "Код содержит обработку исключений для надёжной работы с некорректными данными"
        }
    
    def check_code_duplication(self) -> Dict:
        """Простая проверка дублирования кода через анализ строк"""
        lines = self.source.splitlines()
        cleaned_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        
        # Находим повторяющиеся строки (игнорируем короткие)
        duplicates = {}
        for i, line in enumerate(cleaned_lines):
            if len(line) > 20:  # Игнорируем короткие строки
                count = cleaned_lines.count(line)
                if count > 1 and line not in duplicates:
                    duplicates[line] = count
        
        if len(duplicates) > 2:
            details = "\n".join([f"  • `{line[:50]}...` (повторений: {count})" for line, count in list(duplicates.items())[:3]])
            return {
                "name": "Отсутствие дублирования кода",
                "status": "⚠️",
                "score": max(0, 5 - len(duplicates)),
                "max_score": 5,
                "details": f"Обнаружено дублирование кода:\n{details}"
            }
        
        self.score += 5
        return {
            "name": "Отсутствие дублирования кода",
            "status": "✅",
            "score": 5,
            "max_score": 5,
            "details": "Дублирование кода не обнаружено"
        }
    
    def check_implementation_quality(self) -> Dict:
        """Проверка качества реализации (регулярки, словари для месяцев)"""
        has_regex = bool(re.search(r"import re|from re import", self.source))
        has_month_dict = bool(re.search(r"dict.*[а-яё]", self.source, re.IGNORECASE)) or \
                         bool(re.search(r"\{.*('январь'|'февраль'|'января')", self.source, re.IGNORECASE))
        
        details = []
        score = 0
        
        if has_regex:
            details.append("✅ Используются регулярные выражения для парсинга")
            score += 3
        else:
            details.append("⚠️ Регулярные выражения не используются (рекомендуется для надёжного парсинга)")
        
        if has_month_dict:
            details.append("✅ Используется словарь для хранения месяцев")
            score += 2
        else:
            details.append("⚠️ Словарь месяцев не обнаружен (рекомендуется вместо цепочки if/elif)")
        
        self.score += score
        return {
            "name": "Качество реализации (регулярки, словари)",
            "status": "✅" if score >= 4 else "⚠️",
            "score": score,
            "max_score": 5,
            "details": "\n".join(details)
        }
    
    def check_no_notimplemented(self) -> Dict:
        """Проверка отсутствия заглушки raise NotImplementedError"""
        if "raise NotImplementedError" in self.source:
            return {
                "name": "Отсутствие заглушки NotImplementedError",
                "status": "❌",
                "score": 0,
                "max_score": 5,
                "details": "В коде обнаружена заглушка 'raise NotImplementedError'. Задача не реализована."
            }
        
        self.score += 5
        return {
            "name": "Отсутствие заглушки NotImplementedError",
            "status": "✅",
            "score": 5,
            "max_score": 5,
            "details": "Заглушка удалена, код реализован"
        }
    
    def analyze(self) -> Tuple[List[Dict], int, int]:
        """Запуск полного анализа кода"""
        self.results = []
        self.score = 0
        
        if not self.load_code():
            return self.results, 0, self.max_score
        
        checks = [
            self.check_function_exists,
            self.check_no_notimplemented,
            self.check_naming_conventions,
            self.check_no_hardcoded_magic_values,
            self.check_error_handling,
            self.check_code_duplication,
            self.check_implementation_quality
        ]
        
        for check in checks:
            result = check()
            self.results.append(result)
        
        return self.results, self.score, self.max_score


if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    results, score, max_score = analyzer.analyze()
    
    print(f"Анализ качества кода: {score}/{max_score} баллов")
    for r in results:
        print(f"\n{r['status']} {r['name']}: {r['score']}/{r['max_score']}")
        print(f"   {r['details']}")