STAGE_NAMES = {
    "dns": "DNS-запрос",
    "tcp": "TCP-подключение",
    "server": "Обработка на сервере",
    "transfer": "Передача данных",
    "render": "Рендеринг на клиенте",
}

measurements = {
    "dns": 0.05,
    "tcp": 0.20,
    "server": 2.50,
    "transfer": 0.80,
    "render": 0.45,
}

RECOMMENDATIONS = {
    "dns": "Использовать DNS-кэш и проверить DNS-провайдера.",
    "tcp": "Переиспользовать соединения и использовать HTTP/2.",
    "server": "Проверить SQL-запросы, кэш и внешние API.",
    "transfer": "Уменьшить ответ, добавить сжатие и пагинацию.",
    "render": "Упростить интерфейс и использовать ленивую загрузку.",
}


def report(stages):
    total_time = sum(stages.values())
    if total_time == 0:
        print("Данные для анализа отсутствуют.")
        return
    print(f"Общее время загрузки: {total_time:.2f} сек.")

    for stage, duration in stages.items():
        name = STAGE_NAMES[stage]
        percentage = duration / total_time * 100
        print(f"{name}: {duration:.2f} сек. ({percentage:.1f}%)")

    slowest_stage = max(stages, key=stages.get)
    slowest_duration = stages[slowest_stage]
    slowest_name = STAGE_NAMES[slowest_stage]
    recommendation = RECOMMENDATIONS[slowest_stage]
    print(f"Узкое место: {slowest_name} ({slowest_duration:.2f} сек)")
    print(f"Рекомендация: {recommendation}")


report(measurements)
