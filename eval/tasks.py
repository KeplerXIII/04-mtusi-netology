from dataclasses import dataclass
from typing import Callable


@dataclass
class EvalTask:
    id: str
    category: str
    prompt: str
    check: Callable[[str], bool]


def contains_all(*items: str):
    def checker(answer: str) -> bool:
        text = answer.lower()
        return all(item.lower() in text for item in items)
    return checker


def contains_any(*items: str):
    def checker(answer: str) -> bool:
        text = answer.lower()
        return any(item.lower() in text for item in items)
    return checker


def not_contains_any(*items: str):
    def checker(answer: str) -> bool:
        text = answer.lower()
        return not any(item.lower() in text for item in items)
    return checker


TASKS = [
    EvalTask(
        id="rag_001",
        category="rag_answer",
        prompt="""
Контекст:
Документ № А-15 от 12.03.2026 устанавливает, что заявки на доработку ПО
должны содержать основание, описание текущего функционала, требуемые изменения,
нефункциональные требования и критерии приемки.

Вопрос:
Какие разделы должна содержать заявка на доработку ПО?
Ответь кратко списком.
""",
        check=contains_all(
            "основание",
            "текущего функционала",
            "требуемые изменения",
            "нефункциональные",
            "критерии приемки",
        ),
    ),

    EvalTask(
        id="rag_002",
        category="source_grounding",
        prompt="""
Контекст:
Документ № Р-7 описывает порядок резервного копирования.
Документ № Р-8 описывает порядок восстановления из резервной копии.

Вопрос:
Какой документ отвечает за восстановление из резервной копии?
""",
        check=contains_all("р-8"),
    ),

    EvalTask(
        id="rag_003",
        category="anti_hallucination",
        prompt="""
Контекст:
В документе указано только то, что сервер должен быть доступен в рабочее время.

Вопрос:
Какой точный SLA в процентах установлен документом?
Если информации нет, так и скажи.
""",
        check=contains_any(
            "информации нет",
            "не указано",
            "нет данных",
            "в контексте не указано",
        ),
    ),

    EvalTask(
        id="extract_001",
        category="extraction",
        prompt="""
Извлеки номер, дату и тему документа.

Текст:
Служебная записка № 44/ИТ от 05.04.2026
О необходимости приобретения сетевого оборудования для создания резерва ЗИП.
Ответ верни в JSON с полями number, date, topic.
""",
        check=contains_all("44/ИТ", "05.04.2026", "сетевого оборудования"),
    ),

    EvalTask(
        id="extract_002",
        category="dates",
        prompt="""
Найди все даты в тексте.

Текст:
Тестовый режим действует до 30.09.2026. Рабочий режим начинается с 01.10.2026.
""",
        check=contains_all("30.09.2026", "01.10.2026"),
    ),

    EvalTask(
        id="extract_003",
        category="responsible",
        prompt="""
Извлеки исполнителя и контролирующее лицо.

Текст:
Исполнитель: Иванов И.И. Контроль исполнения возложить на Петрова П.П.
""",
        check=contains_all("Иванов", "Петров"),
    ),

    EvalTask(
        id="summary_001",
        category="summary",
        prompt="""
Сократи текст до 2 предложений.

Текст:
В подразделении вводится обязательная система постановки и контроля задач в Redmine.
Все задачи должны фиксироваться в системе. Исполнители обязаны менять статус задач,
а также ежедневно вносить фактические трудозатраты.
""",
        check=contains_all("Redmine", "трудозатрат"),
    ),

    EvalTask(
        id="summary_002",
        category="official_summary",
        prompt="""
Сделай краткую официально-деловую выжимку.

Текст:
Нужно оплатить счет ООО «Хедхантер» на 25 400 рублей, потому что подразделению
необходимо искать и оценивать кандидатов через специализированный ресурс.
""",
        check=contains_all("ООО", "Хедхантер", "25 400", "подбор"),
    ),

    EvalTask(
        id="classification_001",
        category="classification",
        prompt="""
Определи тип документа: служебная записка, акт, регламент, заявка.

Текст:
Настоящий документ устанавливает порядок взаимодействия подразделений при разработке,
тестировании, приемке и сопровождении программного обеспечения.
""",
        check=contains_all("регламент"),
    ),

    EvalTask(
        id="classification_002",
        category="classification",
        prompt="""
Определи тип документа.

Текст:
Комиссия провела осмотр оборудования, установила его техническое состояние
и пришла к выводу о необходимости списания.
""",
        check=contains_all("акт"),
    ),

    EvalTask(
        id="json_001",
        category="structured_output",
        prompt="""
Верни строго JSON без пояснений.

Текст:
Задача №125: обновить pgAdmin4 на Astra Linux. Приоритет высокий. Исполнитель Сидоров.

Формат:
{
  "task_number": "",
  "title": "",
  "priority": "",
  "assignee": ""
}
""",
        check=contains_all("125", "pgAdmin4", "высок", "Сидоров"),
    ),

    EvalTask(
        id="style_001",
        category="official_style",
        prompt="""
Перепиши в официально-деловом стиле:

Надо оплатить интернет, потому что без него сайт и сервисы могут отвалиться.
""",
        check=contains_all("в связи", "необходим", "оплат"),
    ),

    EvalTask(
        id="style_002",
        category="official_style",
        prompt="""
Сделай текст более сухим и официальным:

Мы посмотрели железки, часть уже старая, предлагаю списать, а рабочее оставить в ЗИП.
""",
        check=contains_any("комиссия", "оборудование", "ЗИП", "списан"),
    ),

    EvalTask(
        id="translation_001",
        category="translation",
        prompt="""
Переведи на русский технически точно:

The system shall extract text from uploaded PDF files and pass the extracted content
to the retrieval pipeline for further semantic search.
""",
        check=contains_all("извлек", "PDF", "семантическ"),
    ),

    EvalTask(
        id="comparison_001",
        category="comparison",
        prompt="""
Сравни два требования и скажи, есть ли противоречие.

Требование 1: документы должны храниться не менее 5 лет.
Требование 2: документы должны удаляться через 1 год после создания.
""",
        check=contains_any("противореч", "конфликт"),
    ),

    EvalTask(
        id="comparison_002",
        category="comparison",
        prompt="""
Сравни два требования.

Требование 1: резервное копирование выполняется ежедневно.
Требование 2: резервные копии создаются каждый день.
""",
        check=contains_any("не противореч", "эквивалент", "одно и то же"),
    ),

    EvalTask(
        id="risk_001",
        category="risk_analysis",
        prompt="""
Выдели основной риск.

Текст:
В системе отсутствует резервный канал связи. При отказе основного провайдера
доступ к внешним сервисам будет невозможен.
""",
        check=contains_all("отказ", "основного", "доступ"),
    ),

    EvalTask(
        id="tasklist_001",
        category="action_items",
        prompt="""
Выдели поручения из текста.

Текст:
Иванову подготовить проект регламента. Петрову проверить настройки прав доступа.
Сидорову до 15.05.2026 подготовить отчет.
""",
        check=contains_all("Иванов", "Петров", "Сидоров", "15.05.2026"),
    ),

    EvalTask(
        id="number_001",
        category="document_number",
        prompt="""
Проверь, соответствует ли номер формату X-C-YY-F-NNNNN.

Номер:
A-B-26-D-00015
""",
        check=contains_any("соответствует", "коррект"),
    ),

    EvalTask(
        id="number_002",
        category="document_number",
        prompt="""
Проверь, соответствует ли номер формату X-C-YY-F-NNNNN.

Номер:
AB-2026-15
""",
        check=contains_any("не соответствует", "некоррект"),
    ),

    EvalTask(
        id="ocr_001",
        category="ocr_cleanup",
        prompt="""
Исправь OCR-текст, сохрани смысл.

Текст:
Служебная запнска о необходнмости прнобретення серверного оборудовання.
""",
        check=contains_all("Служебная записка", "необходимости", "приобретения", "оборудования"),
    ),

    EvalTask(
        id="recommendation_001",
        category="recommendation",
        prompt="""
На основе данных выбери лучший вариант.

Вариант А: дешевле, но accuracy 62%.
Вариант Б: дороже, но accuracy 84%.
Вариант В: средняя цена, accuracy 81%, быстрее остальных.

Нужно выбрать модель для рабочего RAG-ассистента.
""",
        check=contains_any("Вариант В", "вариант в"),
    ),
]
