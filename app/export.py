from io import BytesIO

from django.http import HttpResponse
from xhtml2pdf import pisa


class Export:
    @staticmethod
    def export_csv(template, context, filename):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(template.render(context))
        return response

    @staticmethod
    def export_xlsx(template, context, filename):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(template.render(context))
        return response

    @staticmethod
    def export_pdf(template, context, filename):
        html = template.render(context)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

    @staticmethod
    def export_docx(template, context, filename):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(template.render(context))
        return response
