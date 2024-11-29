import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedCreatedMixin(models.Model):
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedUpdatedMixin(models.Model):
    modified = models.DateTimeField(_("created"), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedCreatedMixin, TimeStampedUpdatedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["name"], name="genre_name_idx")]
        # db_table = "content\".\"genre"
        db_table = "genre"
        verbose_name = _("genre")
        verbose_name_plural = _("genres")

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedCreatedMixin, TimeStampedUpdatedMixin):
    full_name = models.CharField(_("full_name"), max_length=255)

    class Meta:
        indexes = [models.Index(fields=["full_name"], name="person_full_name_idx")]
        db_table = "person"
        verbose_name = _("person")
        verbose_name_plural = _("persons")

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedCreatedMixin, TimeStampedUpdatedMixin):
    class TypeOfFilmwork(models.TextChoices):
        MOVIE = "movie", _("movie")
        TV = "tv_show", _("tv_show")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation_date"), blank=True, null=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_("type"), choices=TypeOfFilmwork.choices, max_length=7)
    genres = models.ManyToManyField(Genre, _("genres"), through="GenreFilmwork")
    person = models.ManyToManyField(Person, _("persons"), through="PersonFilmwork")
    certificate = models.CharField(
        _("certificate"), max_length=512, blank=True, null=True
    )
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")
    premium = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["title"], name="film_work_title_idx")]
        db_table = "film_work"
        verbose_name = _("filmwork")
        verbose_name_plural = _("filmworks")

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin, TimeStampedCreatedMixin):
    film_work = models.ForeignKey(
        Filmwork, on_delete=models.CASCADE, verbose_name=_("film_work")
    )
    genre = models.ForeignKey(Genre, verbose_name=_("genre"), on_delete=models.CASCADE)

    class Meta:
        unique_together = ["film_work", "genre"]
        db_table = "genre_film_work"
        verbose_name = _("genre_of_filmwork")
        verbose_name_plural = _("genres_of_filmworks")


class PersonFilmwork(UUIDMixin, TimeStampedCreatedMixin):
    class RoleTextChoices(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    film_work = models.ForeignKey(
        Filmwork, verbose_name=_("film_work"), on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        Person, verbose_name=_("person"), on_delete=models.CASCADE
    )
    role = models.CharField(
        verbose_name=_("role"), choices=RoleTextChoices.choices, max_length=8
    )

    class Meta:
        unique_together = ["film_work", "person", "role"]
        db_table = "person_film_work"
        verbose_name = _("persons_of_filmwork")
        verbose_name_plural = _("persons_of_filmworks")
