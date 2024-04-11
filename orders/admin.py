from django.contrib import admin
from .models import Order, OrderItem
import csv
import datetime
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = 'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')        # tell the browser that the response has to be a CSV file
    response['Content-Disposition'] = content_disposition   #
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
        return response
    export_to_csv.short_description = 'Export to CSV'


class OrderItemInline(admin.TabularInline):
    # An inline allows you to include a model in the same edit page as its related model
    # we use this to include it as an inline in the OrderAdmin class
    model = OrderItem
    raw_id_field = ['product']


def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    url = reverse('orders:admin_order_pdf', args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')
order_pdf.short_description = 'Invoice'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid',
        'paid', 'created', 'updated', order_detail, order_pdf,
    ]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]
