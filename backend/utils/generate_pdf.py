from io import BytesIO


def get_ingredients_dict(ingredients: list):
    ingredients_dict = {}

    for ingredient in ingredients:
        ingredient_name = ingredient.get('recipe_through__ingredient__name')
        measurement_unit = ingredient.get(
            'recipe_through__ingredient__measurement_unit'
        )
        amount = ingredient.get('recipe_through__amount')

        if ingredient_name in ingredients_dict:
            current_amount = int(ingredients_dict[ingredient_name]['amount'])
            new_amount = int(amount)
            ingredients_dict[ingredient_name]['amount'] = str(
                current_amount + new_amount
            )
        else:
            ingredients_dict[ingredient_name] = {
                'measurement_unit': measurement_unit,
                'amount': str(amount)
            }

    return ingredients_dict


def generate_txt(ingredients: list):
    """Генерация текстового файла со списком покупок"""
    buffer = BytesIO()

    # Собираем текст
    text_content = []
    text_content.append("Список покупок")
    text_content.append("=" * 50)

    ingredients_dict = get_ingredients_dict(ingredients)

    if ingredients_dict:
        for name, value in ingredients_dict.items():
            amount = value.get('amount', '0')
            unit = value.get('measurement_unit', '')
            ingredient_text = f"{name} - {amount} {unit}"
            text_content.append(ingredient_text)
    else:
        text_content.append("Список покупок пуст")

    full_text = "\n".join(text_content)

    buffer.write(full_text.encode('utf-8'))

    txt_content = buffer.getvalue()
    buffer.close()

    return txt_content
