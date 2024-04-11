from datetime import datetime, timedelta
import configparser

def find_wednesdays(year):
    wednesdays = []
    # Перебираем все месяцы в году
    for month in range(1, 13):
        # Начальная дата месяца
        start_date = datetime(year, month, 1)
        # Находим первую среду месяца
        wednesday = start_date + timedelta(days=(7 - start_date.weekday() + 3) % 7)
        # Выводим каждую вторую и каждую четвёртую среду
        while wednesday.month == month:
            wednesdays.append(wednesday.isoformat()[:10]) # Добавляем дату в список
            wednesday += timedelta(days=14) # Переходим к следующей среде через 14 дней
    return wednesdays

# Пример использования для текущего года
current_year = datetime.now().year
wednesdays = find_wednesdays(current_year)

# Создаем экземпляр ConfigParser
config = configparser.ConfigParser()

# Читаем существующие настройки из файла
config.read('settings.ini')

# Добавляем найденные среды в секцию deadlines
for i, wednesday in enumerate(wednesdays, start=1):
    config.set('deadlines', f'deadline{i}', wednesday)

# Сохраняем обновленные настройки обратно в файл
with open('settings.ini', 'w') as configfile:
    config.write(configfile)
