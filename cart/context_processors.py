from .cart import Cart


def cart(request):
    """
    context processors is a Python function that takes the request object as argument
    and return a dict that gets added to the request context
    they are handy when you need to make something available globaly to all templates
    NOTE: you must add the function to the settings file under templates['context_processors']
    """
    return {'cart': Cart(request)}
