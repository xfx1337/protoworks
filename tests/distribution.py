import random
class Printer:
    """Класс для представления 3D-принтера"""

    def __init__(self, max_size, speed):
        self.max_size = max_size
        self.speed = speed  # Скорость печати в см3/час
        self.queue = []  # Очередь печати
        self.total_print_time = 0  # Общее время печати очереди

    def can_print(self, detail_size):
        """Проверяет, может ли принтер напечатать деталь заданного размера"""
        return all(detail_size[i] <= self.max_size[i] for i in range(3))

    def add_detail(self, detail):
        """Добавляет деталь в очередь печати"""
        self.queue.append(detail)
        self.total_print_time += detail.volume / self.speed

class Detail:
    """Класс для представления детали"""

    def __init__(self, size):
        self.size = size
        self.volume = size[0]*size[1]*size[2]

def get_printers_from_user():
    """Получает информацию о принтерах от пользователя"""
    printers = []
    num_printers = int(input("Введите количество принтеров: "))
    for i in range(num_printers):
        size_speed = input(f"Введите характеристики принтера {i+1} (размер,размер,размер,скорость): ")
        values = [int(x) for x in size_speed.split(',')]
        size = values[:3]
        speed = values[3]
        printers.append(Printer(size, speed))
    return printers

def get_details_from_user():
    """Получает информацию о деталях от пользователя"""
    num_details = int(input("Введите количество деталей: "))
    details = []
    for _ in range(num_details):
        size = [random.randint(0, 400) for _ in range(3)]
        details.append(Detail(size))
    return details

def distribute_details(printers, details):
    """Распределяет детали по принтерам, оптимизируя время печати"""
    details.sort(key=lambda x: x.volume, reverse=True)  # Сортируем детали по объему

    for detail in details:
        suitable_printers = [printer for printer in printers if printer.can_print(detail.size)]
        if suitable_printers:
            # Выбираем принтер с наименьшим временем печати
            suitable_printers.sort(key=lambda x: x.total_print_time)
            chosen_printer = suitable_printers[0]
            chosen_printer.add_detail(detail)

def print_queue(printers):
    """Выводит на экран очереди печати для каждого принтера"""
    for i, printer in enumerate(printers):
        print(f"Принтер {i+1}:")
        if printer.queue:
            for j, detail in enumerate(printer.queue):
                print(f"  Деталь {j+1}: Размер: {detail.size}, Объем: {detail.volume} см3, Время печати: {detail.volume / printer.speed:.2f} часов")
        else:
            print("  Очередь пуста")
        print(f"  Общее время печати: {printer.total_print_time:.2f} часов\n")

if __name__ == "__main__":
    printers = get_printers_from_user()
    details = get_details_from_user()
    distribute_details(printers, details)
    print_queue(printers)

    # Добавление новых деталей
    while True:
        new_detail_data = input("Введите характеристики новой детали (размер,размер,размер), или 'q' для выхода: ")
        if new_detail_data == 'q':
            break
        values = [int(x) for x in new_detail_data.split(',')]
        size = values[:3]
        volume = values[3]
        new_detail = Detail(size)
        distribute_details(printers, [new_detail])
        print_queue(printers)