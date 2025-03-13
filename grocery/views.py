from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, Category, Order, Transaction, Comment
import uuid

# Home Page - Display All Products
def home(request):
    categories = Category.objects.all()
    category_products = {
        category: Product.objects.filter(category=category)[:5] for category in categories
    }
    
    cart_items =[]
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    cart_info = {}
    
    for item in cart_items:
        cart_info[item.product_id] = item.quantity
    
    return render(request, 'grocery/home.html', {'products': category_products, 'cart_info': cart_info})

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    cart_items =[]
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    cart_info = {}
    for item in cart_items:
        cart_info[item.product_id] = item.quantity
    return render(request, 'grocery/category_products.html', {'category': category, 'products': products, 'cart_info': cart_info})

# Product Detail Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_items = []
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    comments = product.reviews.all().order_by('-created_at')  # Order by newest first
    cart_info = {}
    for item in cart_items:
        cart_info[item.product_id] = item.quantity
    return render(request, 'grocery/product_detail.html', {
        'product': product,
        'cart_info': cart_info,
        'comments': comments
    })

@login_required(login_url='/account/login/')
def submit_comment(request, product_id):
    if request.method == "POST":
        data = json.loads(request.body)
        comment_text = data.get('comment_text')
        rating = data.get('rating')
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse({"error": "Invalid rating. Please provide a rating between 1 and 5."}, status=400)
            
        product = get_object_or_404(Product, id=product_id)

        if comment_text:
            comment = Comment.objects.create(
                product=product,
                user=request.user,
                comment=comment_text,
                rating=rating
            )
            return JsonResponse({
                "user": request.user.username,
                "comment": comment.comment,
                "rating": comment.rating,
                "created_at": comment.created_at.strftime("%B %d, %Y"),
                "product_rating": float(product.rating),
                "total_ratings": product.total_ratings,
                "star_rating": product.get_star_rating()  
            }, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)

def product_search(request):
    query = request.GET.get('q', '')
    cart_items = Cart.objects.filter(user=request.user)
    categories = Category.objects.all()
    cart_info = {}
    for item in cart_items:
        cart_info[item.product_id] = item.quantity
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    category_products={}
    for category in categories:
        product = products.filter(category=category)[:5]
        if len(product):
            category_products[category] = product

    return render(request, 'grocery/home.html', {'products': category_products, 'cart_info': cart_info})


@login_required(login_url='/account/login/')
def update_cart_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
        print(created)
        if created:
            cart_item.save()
        elif action == "increase":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "decrease":
            cart_item.quantity -= 1
            if cart_item.quantity > 0:
                cart_item.save()
            else:
                cart_item.delete()
                return JsonResponse({"quantity": 0})

        return JsonResponse({"quantity": cart_item.quantity})
    cart_item.delete()    
    return redirect('home')


@login_required(login_url='/account/login/')
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'grocery/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='/account/login/')
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if cart_item.user == request.user:
        cart_item.delete()
        messages.success(request, "Item removed from your cart!")
    else:
        messages.error(request, "You are not authorized to remove this item.")

    return redirect('view_cart')


@login_required(login_url='/account/login/')
def checkout(request, messages=None):
    cart_items = Cart.objects.filter(user=request.user)
    print("+++++++++++++++++++++++++++++++++++++++++",messages, "---------------------------")
    if not cart_items.exists():
        return redirect('home')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'grocery/checkout.html', {'total_price': total_price, 'messages': messages})

@login_required(login_url='/account/login/')
def place_order(request):
    total_price = 0
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        cvv = request.POST.get("cvv")
        expiry = request.POST.get("expiry")

        valid_card_number = "5555444433331111"
        valid_cvv = "737"
        valid_expiry = "03/30"
        if card_number == valid_card_number and cvv == valid_cvv and expiry == valid_expiry:
            order = Order.objects.create(user=request.user, total_price=total_price)
            Transaction.objects.create(
                order=order,
                payment_status="Success",
                transaction_id=str(uuid.uuid4()),
                amount=total_price
            )
            return redirect('order_success', order_id=order.id)
        else:
            Transaction.objects.create(
                order=None,
                payment_status="Failed",
                transaction_id=str(uuid.uuid4()),
                amount=total_price
            )
            print("Error ++++++++++++++++++++++++++++++")
            return redirect('checkout', messages='Invalid card details. Please try again.')

    return redirect('checkout')

@login_required(login_url='/account/login/')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "grocery/order_success.html", {"order": order})
