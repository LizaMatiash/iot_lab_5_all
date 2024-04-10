import csv

def remove_missing_lines(csv_file_path):
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    cleaned_rows = []

    for row in rows:
        # Рахуємо кількість чисел у рядку
        values_count = len(row)
        if values_count >= 3:  # Якщо чисел у рядку не менше трьох, додаємо рядок
            cleaned_rows.append(row)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(cleaned_rows)

csv_file_path = "data.csv"  # Замініть "data.csv" на шлях до вашого CSV-файлу
remove_missing_lines(csv_file_path)
