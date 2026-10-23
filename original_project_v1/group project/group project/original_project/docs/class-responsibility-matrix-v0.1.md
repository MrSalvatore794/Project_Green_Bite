# GreenBite — Class Responsibility Matrix v0.1

## 1. Purpose

This document defines the responsibilities and collaborators of the
main object-oriented classes in the GreenBite MVP server.

The design follows the OOP concepts covered in MSE800, including:

- Encapsulation
- Abstraction
- Inheritance
- Polymorphism
- Composition
- Separation of responsibilities

The purpose of this matrix is to prevent classes from becoming
"God classes" and to keep responsibilities separated between:

- Domain Models
- Repositories
- Services
- Routes

---

# 2. High-Level Object-Oriented Architecture

The server follows the following responsibility flow:

Client
  ↓
Route
  ↓
Service
  ↓
Repository
  ↓
SQLite Database

Domain models are used by the service layer to represent business
objects and business behaviour.

The model layer does not directly access SQLite.

---

# 3. Class Responsibility Matrix

| Class | Type | Main Responsibilities | Collaborators |
|---|---|---|---|
| User | Domain Model | Store common user information and common user behaviour | Customer, Admin |
| Customer | Domain Model | Represent a customer and customer-specific behaviour | User, Cart, Order |
| Admin | Domain Model | Represent an administrator and administrator-specific behaviour | User |
| Product | Domain Model | Represent a bakery product, availability and stock behaviour | CartItem, OrderItem |
| Cart | Domain Model | Manage a customer's current shopping cart and calculate totals | CartItem, Product |
| CartItem | Domain Model | Represent a product and quantity within a cart | Cart, Product |
| Order | Domain Model | Represent a submitted order, calculate total and manage order status | OrderItem, User |
| OrderItem | Domain Model | Represent a purchased product with historical price snapshot | Order, Product |
| UserRepository | Repository | Persist and retrieve User/Customer/Admin data | User, Database |
| ProductRepository | Repository | Persist and retrieve Product data | Product, Database |
| CartRepository | Repository | Persist and retrieve Cart and CartItem data | Cart, CartItem, Database |
| OrderRepository | Repository | Persist and retrieve Order and OrderItem data | Order, OrderItem, Database |
| AuthService | Service | Coordinate registration, authentication and user-related business rules | UserRepository, User |
| ProductService | Service | Coordinate product operations and product business rules | ProductRepository, Product |
| CartService | Service | Coordinate cart operations and validate product/quantity rules | CartRepository, ProductRepository, Cart, Product |
| OrderService | Service | Coordinate order creation, stock validation and order lifecycle | OrderRepository, CartRepository, ProductRepository, Order |
| Route Blueprints | Presentation/API | Receive HTTP requests, validate basic input and return HTTP responses | Services |

---

# 4. Domain Model Responsibilities

## 4.1 User

### Responsibilities

- Store common user information.
- Represent the common identity of application users.
- Store role information.
- Provide common user behaviour.

### Attributes

- id
- name
- email
- phone
- password_hash
- role

### Collaborators

- Customer
- Admin

### OOP Principle

Inheritance.

User provides common state and behaviour that can be reused by
Customer and Admin.

---

# 5. Customer

### Responsibilities

- Represent a customer.
- Provide customer-specific behaviour.
- Own or access the customer's shopping cart.
- Create and view customer orders through application services.

### Collaborators

- User
- Cart
- Order

### OOP Principle

Inheritance.

Customer extends User.

Customer-specific operations should not be placed inside the generic
User class.

---

# 6. Admin

### Responsibilities

- Represent an administrator.
- Provide administrator-specific behaviour.
- Support administrative operations through the service layer.

### Collaborators

- User
- ProductService
- OrderService

### OOP Principle

Inheritance.

Admin extends User.

Administrative permissions and behaviour should remain separate from
Customer behaviour.

---

# 7. Product

### Responsibilities

- Represent a bakery product.
- Store product information.
- Determine whether the product is currently available.
- Maintain stock quantity.
- Increase or decrease stock safely.
- Prevent stock from becoming negative.

### Important Behaviour

- is_available()
- update_stock()
- reduce_stock()

### Collaborators

- CartItem
- OrderItem

### OOP Principles

Encapsulation.

Stock changes should occur through controlled methods rather than
allowing arbitrary external modification.

---

# 8. Cart

### Responsibilities

- Represent the customer's current shopping cart.
- Add products.
- Remove products.
- Update quantities.
- Calculate cart total.
- Clear cart items.

### Important Behaviour

- add_item()
- remove_item()
- update_item()
- calculate_total()
- clear()

### Collaborators

- CartItem
- Product

### OOP Principle

Composition.

A Cart is composed of multiple CartItems.

---

# 9. CartItem

### Responsibilities

- Represent one product entry inside a Cart.
- Store product reference.
- Store quantity.
- Calculate item subtotal.

### Important Behaviour

- calculate_subtotal()

### Collaborators

- Cart
- Product

### OOP Principle

Composition.

CartItem is part of a Cart.

---

# 10. Order

### Responsibilities

- Represent a submitted customer order.
- Store customer/order information.
- Contain OrderItems.
- Calculate the order total.
- Maintain order status.
- Validate order status transitions.

### Important Behaviour

- calculate_total()
- change_status()

### Order Lifecycle

pending
  ↓
confirmed
  ↓
preparing
  ↓
ready_for_pickup
  ↓
collected

### Collaborators

- User
- OrderItem
- Product

### OOP Principles

Encapsulation and composition.

Order controls its own status transition and contains multiple
OrderItems.

---

# 11. OrderItem

### Responsibilities

- Represent one purchased product.
- Store quantity.
- Store historical product name.
- Store historical unit price.
- Calculate subtotal.

### Important Behaviour

- calculate_subtotal()

### Important Design Rule

OrderItem stores a snapshot of:

- product_name
- unit_price

This means a later Product price change does not change an existing
historical order.

### Collaborators

- Order
- Product

### OOP Principle

Composition.

---

# 12. Repository Responsibilities

Repositories are responsible for persistence.

They should know how to communicate with SQLite.

They should NOT contain business workflows.

---

## UserRepository

Responsibilities:

- Find user by ID.
- Find user by email.
- Create user.
- Update user.
- Retrieve users.

Should NOT:

- implement login workflows
- decide authorization
- hash passwords

Those responsibilities belong to AuthService or related services.

---

## ProductRepository

Responsibilities:

- Find product.
- Retrieve active products.
- Retrieve all products for admin.
- Create product.
- Update product.
- Update stock.
- Persist product state.

Should NOT:

- decide whether an admin is authorized.
- implement HTTP logic.

---

## CartRepository

Responsibilities:

- Retrieve cart by user.
- Create cart.
- Retrieve cart items.
- Add/update/remove cart items.
- Clear cart.

Should NOT:

- decide HTTP responses.
- perform authentication.
- implement route logic.

---

## OrderRepository

Responsibilities:

- Create orders.
- Create order items.
- Retrieve orders.
- Retrieve order details.
- Update order status.
- Retrieve orders for a customer.
- Retrieve all orders for admin.

Should NOT:

- implement HTTP behaviour.
- decide whether a user is allowed to perform an action.

---

# 13. Service Responsibilities

Services coordinate business use cases.

Services should not directly expose HTTP responses.

Services may coordinate multiple repositories.

---

# 14. AuthService

### Responsibilities

- Register customers.
- Validate registration rules.
- Hash passwords.
- Verify login credentials.
- Create authenticated user context.

### Collaborators

- UserRepository
- User / Customer

### Important Boundary

AuthService handles authentication business logic.

Routes should not implement password hashing or database queries.

---

# 15. ProductService

### Responsibilities

- Retrieve products.
- Retrieve product details.
- Create products.
- Update products.
- Activate/deactivate products.
- Update stock.
- Validate product-related business rules.

### Collaborators

- ProductRepository
- Product

---

# 16. CartService

### Responsibilities

- Retrieve customer cart.
- Add product to cart.
- Update cart quantity.
- Remove product from cart.
- Validate product availability.
- Validate quantity.
- Calculate cart total.

### Collaborators

- CartRepository
- ProductRepository
- Cart
- CartItem
- Product

### Important Rule

CartService coordinates multiple objects rather than putting all
business logic inside the Route.

---

# 17. OrderService

### Responsibilities

- Validate checkout request.
- Validate cart contents.
- Validate product availability.
- Validate stock.
- Create Order.
- Create OrderItems.
- Calculate order total.
- Reduce product stock.
- Clear the customer's cart.
- Retrieve customer orders.
- Update order status for authorised users.

### Collaborators

- OrderRepository
- CartRepository
- ProductRepository
- Order
- OrderItem
- Cart
- Product

### Important Transaction

Order creation should eventually be handled as one database
transaction:

Validate cart
  ↓
Create Order
  ↓
Create OrderItems
  ↓
Reduce stock
  ↓
Clear Cart
  ↓
Commit

If any operation fails:

Rollback

---

# 18. Route Responsibilities

Routes form the HTTP/API boundary.

A Route should:

1. Receive HTTP request.
2. Parse request data.
3. Perform basic request validation.
4. Call the appropriate Service.
5. Convert the result into an HTTP response.
6. Return the appropriate status code.

Routes should NOT:

- contain SQL
- directly manipulate database connections
- implement complex business rules
- calculate order totals manually
- modify stock directly
- implement authentication logic

Example:

POST /api/v1/orders

Route
  ↓
OrderService.create_order()
  ↓
OrderRepository
CartRepository
ProductRepository
  ↓
SQLite

---

# 19. OOP Principle Mapping

| OOP Principle | GreenBite Example |
|---|---|
| Encapsulation | Product controls stock changes through methods |
| Encapsulation | Order controls status transitions |
| Inheritance | Customer and Admin inherit from User |
| Composition | Cart contains CartItems |
| Composition | Order contains OrderItems |
| Abstraction | Services hide use-case coordination from Routes |
| Abstraction | Repositories hide SQLite persistence details |
| Polymorphism | Customer and Admin can provide role-specific behaviour through a common User interface |
| Separation of Responsibility | Routes, Services, Repositories and Models have different responsibilities |

---

# 20. Polymorphism Design

Polymorphism should only be introduced where it represents a real
business difference.

The preferred direction is:

User
├── Customer
└── Admin

Both may provide a common operation such as:

get_permissions()

Customer.get_permissions()
    → customer permissions

Admin.get_permissions()
    → administrative permissions

The application can then work with User references without needing
to know the concrete subclass in every case.

Do not introduce artificial polymorphism simply to demonstrate the
concept.

---

# 21. Responsibility Boundaries

The following boundaries should be maintained.

### Model

Knows:

- domain state
- domain behaviour

Does not know:

- HTTP
- SQLite

### Repository

Knows:

- SQLite
- SQL
- persistence

Does not know:

- HTTP
- UI
- authentication workflow

### Service

Knows:

- business workflows
- coordination between repositories and models

Does not know:

- HTTP response formatting

### Route

Knows:

- HTTP
- request/response
- API status codes

Does not know:

- SQL implementation
- complex business logic

---

# 22. Anti-God-Class Rule

No single class should be responsible for the entire application.

Avoid designs such as:

GreenBiteSystem
    ├── database
    ├── authentication
    ├── products
    ├── carts
    ├── orders
    └── admin

Instead, responsibilities are distributed across focused classes.

---

# 23. Expected Dependency Direction

Preferred dependency direction:

Routes
  ↓
Services
  ↓
Repositories
  ↓
Database

Services also use:

Models

Repositories use:

Models + Database

Models do not depend on:

Routes
Services
Repositories
Database

This keeps the domain model independent from infrastructure.

---

# 24. Design Goal

The objective is not to maximise the number of classes.

The objective is to create a small, understandable object-oriented
system where every class has a clear responsibility and collaboration
relationship.

The implementation should remain simple enough for all three team
members to explain during the MSE800 assessment presentation.