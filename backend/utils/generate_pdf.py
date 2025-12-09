from io import BytesIO
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


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


def generate_pdf(ingredients: list):
    buffer = BytesIO()

    styles = getSampleStyleSheet()

    styles['Normal'].fontName = 'Helvetica'
    styles['Heading1'].fontName = 'Helvetica-Bold'

    doc = SimpleDocTemplate(buffer, pagesize=A4, title='Shopping List')
    flowables = []

    flowables.append(Paragraph('Список покупок', styles['Heading1']))

    ingredients_dict = get_ingredients_dict(ingredients)

    if ingredients_dict:
        for name, value in ingredients_dict.items():
            amount = value.get('amount', '0')
            unit = value.get('measurement_unit', '')
            ingredient_text = f"{name} - {amount} {unit}"

            flowables.append(Paragraph(ingredient_text, styles["Normal"]))
    else:
        flowables.append(Paragraph("Список покупок пуст", styles["Normal"]))

    doc.build(flowables)

    pdf_content = buffer.getvalue()
    buffer.close()

    return pdf_content
