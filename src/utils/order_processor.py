# 1. Работа со строками и файлами
# создаем функцию для чтения файла
def load_orders_from_file(filename):
    # создаем список заказов из файла
    try:
        orders = []
        # открываем файл в режиме чтения
        with open(filename, 'r', encoding='utf-8') as file:
            # создаем переменную lines, которая читает файл построчно
            lines = file.readlines()
            # проходимся циклом по строкам
            for line in lines:
                # создаем переменную которая убирает лишние пробелы и перенос строки и разбивает данные по ':'
                line_1 = line.strip()
                # добавляем отредактированные данные в список
                orders.append(line_1)
        # возвращаем результат работы функции - готовый список
        return orders
    except FileNotFoundError:
        print(f'Ошибка: файл {filename} не найден')
        return []

# 2. Работа с числами и условными операторами

# создаем функцию, которая принимает цену и скидку и возвращает итоговую стоимость с округлением до 2 знаков
def calculate_order_total(price, discount_rate):
    return round(price * (1  - discount_rate), 2)

# создаем функцию, которая вычисляет размер скидки в зависимости от суммы заказа
def get_discount_by_total(total):
    # проверяем сумму заказа и в зависимости от этого назначаем скидку
    if total > 10000:
        discount_rate = 0.15
    elif total > 5000:
        discount_rate = 0.1
    else:
        discount_rate = 0.05
    # отдельная проверка - если total <= 0, возвращаем 0
    if total <= 0:
        return 0
    # возвращаем результат работы функции - скидку
    return discount_rate

# 3. Работа со списками и циклами
def process_orders(orders_data):
    processed = []
    for order_line in orders_data:
        try:
            parts = order_line.split(':')

            if len(parts) == 4:
                order_id = parts[0].strip()
                order_sum = int(parts[1].strip())
                order_status = parts[2].strip()
                order_user = parts[3].strip()

                discount_rate = get_discount_by_total(order_sum)
                order_total = calculate_order_total(order_sum, discount_rate)

                processed.append({
                    'order_id' : order_id,
                    'total' : order_total,
                    'status' : order_status,
                    'user' : order_user
                })
            else:
                print(f'Ошибка: неверный формат строки: {order_line}')
        except ValueError:
            print(f'Ошибка: неверный формат числа в строке: {order_line}')
    return processed



def analyze_orders(processed_orders):
    stats = {
        'total_orders' : 0,
        'total_sum' : 0,
        'by_status' : {},
        'unique_users' : set()
    }
    for order in processed_orders:
        stats['total_orders'] = stats['total_orders'] + 1
        stats['total_sum'] = stats['total_sum'] + order['total']

        status = order['status']
        if status in stats['by_status']:
            stats['by_status'][status] = stats['by_status'][status] + 1
        else:
            stats['by_status'][status] =  1

        stats['unique_users'].add(order['user'])

    stats['unique_users'] = list(stats['unique_users'])

    return stats


def process_order_file(input_file, output_file):
    orders_data = load_orders_from_file(input_file)

    if not orders_data:
        print('Нет данных для обработки')
        return

    processed_orders = process_orders(orders_data)
    stats = analyze_orders(processed_orders)

    status_lines = []
    for status, count in stats['by_status'].items():
        status_lines.append(status + ': ' + str(count))
    status_string = ', '.join(status_lines)

    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"Обработано заказов: {stats['total_orders']}\n")
            file.write(f"Общая сумма: {stats['total_sum']} руб.\n")
            file.write(f"По статусам: {status_string}\n")
            file.write(f"Уникальных пользователей: {len(stats['unique_users'])}\n")
        print(f'Отчет создан: {output_file}')
    except Exception as e:
        print(f'Ошибка при записи файла: {e}')