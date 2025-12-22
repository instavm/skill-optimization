// E-commerce shopping cart
// Contains several bugs and code quality issues

class ShoppingCart {
    constructor() {
        this.items = [];
        this.total = 0;
    }

    addItem(item) {
        this.items.push(item);
        this.total = this.total + item.price;
    }

    removeItem(itemId) {
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i].id == itemId) {
                this.items.splice(i, 1);
                break;
            }
        }
    }

    calculateTotal() {
        var sum = 0;
        for (var i = 0; i < this.items.length; i++) {
            sum = sum + this.items[i].price;
        }
        this.total = sum;
        return sum;
    }

    applyDiscount(code) {
        if (code == "SAVE10") {
            this.total = this.total * 0.9;
        } else if (code == "SAVE20") {
            this.total = this.total * 0.8;
        } else if (code == "SAVE50") {
            this.total = this.total * 0.5;
        }
    }

    checkout(paymentInfo) {
        // Process payment
        var cardNumber = paymentInfo.cardNumber;
        var cvv = paymentInfo.cvv;

        console.log("Processing payment with card: " + cardNumber);

        // Send to payment processor
        fetch('https://payment-api.example.com/charge', {
            method: 'POST',
            body: JSON.stringify({
                card: cardNumber,
                cvv: cvv,
                amount: this.total
            })
        });

        return true;
    }

    saveToLocalStorage() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    loadFromLocalStorage() {
        var data = localStorage.getItem('cart');
        this.items = JSON.parse(data);
    }
}

// Usage
var cart = new ShoppingCart();

function addToCart(productId) {
    var product = getProduct(productId);
    cart.addItem(product);
    cart.saveToLocalStorage();
}

function getProduct(id) {
    // Fetch product from API
    var response = fetch('/api/products/' + id);
    return response.json();
}
