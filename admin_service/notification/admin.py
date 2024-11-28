from django.contrib import admin

from notification.models import PersonalNotification


@admin.register(PersonalNotification)
class NotificationAdmin(admin.ModelAdmin):
    model = PersonalNotification
    extra = 0
    # raw_id_fields = ("user",)
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"
    actions = ("send_notification",)

    @admin.action(description="Отправить уведомление пользователям")
    def send_notification(self, request, queryset):
        print('send notification')
        # for notification in queryset:
        #     status_code = notification.send()
