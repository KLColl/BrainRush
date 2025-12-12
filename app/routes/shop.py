from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.db.models import (
    get_all_shop_items, 
    get_shop_item, 
    purchase_item, 
    user_has_purchased,
    get_user_purchases,
    get_user_coins
)

# Створення blueprint магазину з URL префіксом
shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

@shop_bp.route("/")
@login_required
def shop_list():
    # Отримання всіх активних товарів магазину з бази даних
    items = get_all_shop_items()
    
    # Отримання поточного балансу монет користувача
    user_coins = get_user_coins(current_user.id)
    
    # Отримання списку товарів, які користувач вже купив
    user_purchases = get_user_purchases(current_user.id)
    purchased_ids = [p["id"] for p in user_purchases]
    
    return render_template(
        "shop/list.html", 
        items=items, 
        user_coins=user_coins,
        purchased_ids=purchased_ids
    )

@shop_bp.route("/purchase/<int:item_id>", methods=["POST"])
@login_required
def purchase(item_id):
    # Перевіряє баланс та виконує транзакцію
    success, message = purchase_item(current_user.id, item_id)
    
    # Відображення відповідного повідомлення на основі результату покупки
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    
    # Перенаправлення назад на сторінку магазину
    return redirect(url_for("shop.shop_list"))

@shop_bp.route("/api/check_access/<game_name>", methods=["GET"])
@login_required
def check_game_access(game_name):
    # Список ігор, які доступні безкоштовно
    free_games = ["arithmetic", "sequence_recall"]
    
    # Перевірка чи запитана гра знаходиться у списку безкоштовних ігор
    if game_name.lower() in free_games:
        return jsonify({
            "has_access": True, 
            "is_free": True,
            "message": "This game is free to play!"
        })
    
    # Для платних ігор перевірка чи користувач придбав її
    shop_items = get_all_shop_items()
    game_item = None
    
    # Пошук товару гри в магазині
    for item in shop_items:
        if item["item_type"] == "game" and item["name"].lower().replace(" ", "_") == game_name.lower():
            game_item = item
            break
    
    # Гра не знайдена в магазині
    if not game_item:
        return jsonify({
            "has_access": False, 
            "error": "Game not found in shop"
        }), 404
    
    # Перевірка чи користувач придбав цю гру
    has_purchased = user_has_purchased(current_user.id, game_item["id"])
    
    return jsonify({
        "has_access": has_purchased,
        "is_free": False,
        "item_id": game_item["id"],
        "price": game_item["price"] if not has_purchased else None,
        "message": "You own this game!" if has_purchased else f"Purchase required: {game_item['price']} coins"
    })

@shop_bp.route("/my-purchases")
@login_required
def my_purchases():
    # Отримання всіх товарів, придбаних поточним користувачем
    purchases = get_user_purchases(current_user.id)
    
    return render_template(
        "shop/purchases.html",
        purchases=purchases
    )