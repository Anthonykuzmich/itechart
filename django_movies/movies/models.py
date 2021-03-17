from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Genre(TimeStampedModel):
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

        def __str__(self):
            return self.name


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class Filmwork(TimeStampedModel):
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания фильма'),
                                     blank=True)
    certificate = models.TextField(_('сертификат'), blank=True)
    file_path = models.FileField(_('файл'),
                                 upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'),
                               validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_('тип'), max_length=20,
                            choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre)

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

        def __str__(self):
            return self.title
