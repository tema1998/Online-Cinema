from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork


class MoviesApiMixin:
    """
    Mixin for Filmwork model implementing get_queryset and render_to_response methods. Only for get requests.
    """

    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            self.model.objects.all()
            .values()
            .annotate(
                genres=ArrayAgg("genres__name", distinct=True),
                actors=ArrayAgg(
                    "person__full_name",
                    distinct=True,
                    filter=Q(person__personfilmwork__role="actor"),
                    default=[],
                ),
                directors=ArrayAgg(
                    "person__full_name",
                    distinct=True,
                    filter=Q(person__personfilmwork__role="director"),
                    default=[],
                ),
                writers=ArrayAgg(
                    "person__full_name",
                    distinct=True,
                    filter=Q(person__personfilmwork__role="writer"),
                    default=[],
                ),
            )
            .order_by("creation_date")
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    """
    View to display a list of movies by `paginate_by` number per page.
    """

    model = Filmwork
    paginate_by = 50
    http_method_names = ["get"]  # Список методов, которые реализует обработчик

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
        }

        if page.has_next():
            context["next"] = page.next_page_number()
        else:
            context["next"] = None

        if page.has_previous():
            context["prev"] = page.previous_page_number()
        else:
            context["prev"] = None

        context["results"] = list(queryset)

        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """
    View to display movie data by movie ID.
    """

    def get_context_data(self, **kwargs):
        return self.object
