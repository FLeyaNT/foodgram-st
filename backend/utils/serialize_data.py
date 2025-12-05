import json


def main():
    with open(
        'D:/Dev/final/foodgram-st/data/ingredients.json', 
        'r', encoding='utf-8'
    ) as f:
        data = json.load(f)

    converted_data = []
    for i, item in enumerate(data, 1):
        converted_data.append({
            "model": "ingredients.Ingredient",
            "pk": i,
            "fields": {
                "name": item["name"],
                "measurement_unit": item["measurement_unit"]
            }
        })


    with open('ingredients_converted.json', 'w', encoding='utf-8') as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)

    print("Файл преобразован успешно!")


if __name__ == '__main__':
    main()
