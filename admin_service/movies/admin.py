from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Genre, Filmwork, GenreFilmwork, PersonFilmwork, Person


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name", "description")


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ("genre",)


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ("person",)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = (
        "title",
        "type",
        "get_genres",
        "creation_date",
        "rating",
    )
    list_filter = ("type",)
    list_prefetch_related = ("genres",)
    search_fields = ("title", "description", "id")

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        )
        return queryset

    def get_genres(self, obj):
        return ",".join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = _("genres_of_filmworks")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("full_name",)
