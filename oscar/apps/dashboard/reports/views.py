from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from oscar.core.loading import get_class
ReportForm = get_class('dashboard.reports.forms', 'ReportForm')
GeneratorRepository = get_class('dashboard.reports.utils', 'GeneratorRepository')


class IndexView(TemplateView):
    template_name = 'dashboard/reports/index.html'
    
    def get(self, request, *args, **kwargs):
        if 'report_type' in request.GET:
            form = ReportForm(request.GET)
            if form.is_valid():
                generator = _get_generator(form)
                if not generator.is_available_to(request.user):
                    return HttpResponseForbidden("You do not have access to this report")
                
                response = HttpResponse(mimetype=generator.mimetype)
                response['Content-Disposition'] = 'attachment; filename=%s' % generator.filename()
                generator.generate(response)
                return response
        else:
            form = ReportForm()
        return TemplateResponse(request, self.template_name, {'form': form})


def _get_generator(form):
    code = form.cleaned_data['report_type']

    repo = GeneratorRepository()
    generator_cls = repo.get_generator(code)
    if not generator_cls:
        raise Http404()
    return generator_cls(start_date=form.cleaned_data['date_from'], 
                         end_date=form.cleaned_data['date_to'])
