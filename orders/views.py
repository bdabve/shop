from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created

# for pdf
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from django.contrib.admin.views.decorators import staff_member_required


# the staff_member_required checks that both the is_active and is_staff fields of the user
# requisting the page are set to True
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response, stylesheet=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
    return response


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # Validate the data; than
        # create a new order in the database usig the form.save()
        # iterate over the cart items and create an OrderItem for each item.
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'])
            # clear the cart
            cart.clear()
            # launch asynchronous task
            # delay to execute it async. the task will be added to the queue
            # and will be executed by a worker as soon as possible.
            #
            order_created.delay(order.id)
            return render(request, 'orders/order/created.html', {'order': order})
    else:
        # GET request: instantiates the OrderCreateForm
        form = OrderCreateForm()
    context = {'cart': cart, 'form': form}
    return render(request, 'orders/order/create.html', context)
