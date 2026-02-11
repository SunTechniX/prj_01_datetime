import sys
from pathlib import Path
from datetime import datetime

# Добавляем tools в PATH
sys.path.insert(0, str(Path(__file__).parent))

from code_analysis import CodeAnalyzer
from run_task_tests import TaskTester


def generate_summary():
    """Генерация красивого отчёта для GitHub Actions Summary"""
    
    # Заголовок отчёта
    summary = f"""
# 📊 Автопроверка: Сортировка транзакций по дате

**Дата проверки:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
**Задача:** Реализовать сортировку транзакций от новых к старым с поддержкой 7 форматов дат

---

## 🧪 Функциональное тестирование (60 баллов)

"""
    
    # Запуск функциональных тестов
    tester = TaskTester()
    test_results, test_score, test_max = tester.run_all_tests()
    
    for res in test_results:
        icon = res['status']
        summary += f"{icon} **{res['name']}** — `{res['score']}/{res['max_score']}`\n"
        if res['details']:
            # Форматируем детали с отступом
            details = res['details'].replace('\n', '\n  > ')
            summary += f"  > {details}\n"
        summary += "\n"
    
    summary += f"**Итого за тесты:** `{test_score}/{test_max}` баллов\n\n---\n\n"
    
    # Анализ качества кода
    summary += "## 🔍 Анализ качества кода (40 баллов)\n\n"
    
    analyzer = CodeAnalyzer()
    code_results, code_score, code_max = analyzer.analyze()
    
    for res in code_results:
        icon = res['status']
        summary += f"{icon} **{res['name']}** — `{res['score']}/{res['max_score']}`\n"
        if res['details']:
            details = res['details'].replace('\n', '\n  > ')
            summary += f"  > {details}\n"
        summary += "\n"
    
    summary += f"**Итого за качество кода:** `{code_score}/{code_max}` баллов\n\n---\n\n"
    
    # Итоговый результат
    total_score = test_score + code_score
    total_max = test_max + code_max
    percent = (total_score / total_max) * 100
    
    # Определение статуса
    if total_score >= 85:
        status_emoji = "🟢"
        status_text = "Отлично"
        status_desc = "Решение полностью соответствует требованиям"
    elif total_score >= 70:
        status_emoji = "🟡"
        status_text = "Хорошо"
        status_desc = "Решение проходит базовые требования, есть незначительные замечания"
    elif total_score >= 50:
        status_emoji = "🟠"
        status_text = "Удовлетворительно"
        status_desc = "Решение частично работает, требуется доработка"
    else:
        status_emoji = "🔴"
        status_text = "Неудовлетворительно"
        status_desc = "Решение не проходит основные тесты или не реализовано"
    
    summary += f"""## 📈 Итоговый результат

{status_emoji} **{status_text}** — {status_desc}

| Критерий | Баллы | Максимум |
|----------|-------|----------|
| Функциональные тесты | {test_score} | {test_max} |
| Качество кода | {code_score} | {code_max} |
| **Итого** | **{total_score}** | **{total_max}** |

**Процент выполнения:** {percent:.1f}%

"""
    
    # Рекомендации
    summary += "## 💡 Рекомендации для улучшения\n\n"
    
    if test_score < test_max:
        summary += "- Улучшите обработку граничных случаев (високосные годы, 31-е числа)\n"
        summary += "- Проверьте корректность сортировки при одинаковых датах\n"
    
    if code_score < code_max:
        low_scores = [r for r in code_results if r['score'] < r['max_score'] * 0.7]
        if low_scores:
            summary += "- Улучшите качество кода:\n"
            for r in low_scores[:3]:
                summary += f"  • {r['name'].lower()}\n"
    
    if total_score < 70:
        summary += "\n⚠️ **Для прохождения требуется минимум 70 баллов.** Доработайте решение согласно рекомендациям выше.\n"
    else:
        summary += "\n✅ **Поздравляем! Решение проходит проверку.**\n"
    
    # Сохранение в SUMMARY.md для GitHub Actions
    summary_path = Path(os.getenv("GITHUB_STEP_SUMMARY", "SUMMARY.md"))
    summary_path.write_text(summary, encoding="utf-8")
    
    # Также выводим в консоль для локальной отладки
    print(summary)
    
    # Устанавливаем выходной код для GitHub Actions
    sys.exit(0 if total_score >= 70 else 1)


if __name__ == "__main__":
    import os
    generate_summary()