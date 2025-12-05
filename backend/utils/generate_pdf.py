from io import BytesIO
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_ingredients_dict(ingredients: list):
    ingredients_dict = {}
    
    for ingredient in ingredients:
        ingredient_name = ingredient.get('recipe_through__ingredient__name')
        measurement_unit = ingredient.get('recipe_through__ingredient__measurement_unit')
        amount = ingredient.get('recipe_through__amount')
            
        if ingredient_name in ingredients_dict:
            current_amount = int(ingredients_dict[ingredient_name]['amount'])
            new_amount = int(amount)
            ingredients_dict[ingredient_name]['amount'] = str(current_amount + new_amount)
        else:
            ingredients_dict[ingredient_name] = {
                'measurement_unit': measurement_unit,
                'amount': str(amount)
            }
    
    print("Processed ingredients:", ingredients_dict)
    return ingredients_dict


def generate_pdf(ingredients: list):
    buffer = BytesIO()
    
    styles = getSampleStyleSheet()
    
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
    styles['Normal'].fontName = 'DejaVuSerif'
    styles['Heading1'].fontName = 'DejaVuSerif'

    doc = SimpleDocTemplate(buffer, pagesize=A4, title='Shopping List')
    story = []

    story.append(Paragraph('Список покупок', styles['Heading1']))
    
    ingredients_dict = get_ingredients_dict(ingredients)

    if ingredients_dict:
        for name, value in ingredients_dict.items():
            amount = value.get('amount', '0')
            unit = value.get('measurement_unit', '')
            text = f"{name} - {amount} {unit}"
            
            story.append(Paragraph(text, styles["Normal"]))
    else:
        story.append(Paragraph("Список покупок пуст", styles["Normal"]))

    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()

    return pdf_content