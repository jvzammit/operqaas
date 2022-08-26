from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import reverse
from django.utils.safestring import mark_safe

from quizzes.models import Quiz, QuizQuestion, QuizQuestionAnswer

TEXTFIELD_CONFIG = {
    models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 40})},
}


class QuizQuestionAnswerInline(admin.TabularInline):
    extra = 1
    formfield_overrides = TEXTFIELD_CONFIG
    model = QuizQuestionAnswer


class QuizQuestionAdmin(admin.ModelAdmin):
    formfield_overrides = TEXTFIELD_CONFIG
    model = QuizQuestion
    inlines = [QuizQuestionAnswerInline]
    raw_id_fields = ["quiz"]


class QuizQuestionInline(admin.TabularInline):
    extra = 1
    fields = ["text", "edit_url", "position"]
    model = QuizQuestion
    readonly_fields = ["text", "edit_url"]

    @admin.display(description="Change")
    def edit_url(self, instance):
        pattern = "admin:{0}_{1}_change".format(
            instance._meta.app_label, instance._meta.model_name
        )
        changeform_url = reverse(pattern, args=[instance.id])
        return mark_safe(
            '<a href="{0}" target="_blank">Edit</a>'.format(changeform_url)
        )


class QuizAdmin(admin.ModelAdmin):
    model = Quiz
    search_fields = ["name", "owner"]
    list_display = ["name", "owner"]
    raw_id_fields = ["owner"]
    inlines = [QuizQuestionInline]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
