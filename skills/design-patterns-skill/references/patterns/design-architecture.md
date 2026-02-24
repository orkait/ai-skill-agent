# Design & Architecture Principles

## Single Responsibility Principle (SRP)

**Definition:** Each class or module should have only one reason to change. It should encapsulate one cohesive responsibility.

**Supported by:** *Clean Code*, *The Pragmatic Programmer*, SOLID Principles

### Examples

```python
# Bad - Multiple responsibilities
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        # Database logic
        pass
    
    def send_welcome_email(self):
        # Email logic
        pass
    
    def generate_report(self):
        # Reporting logic
        pass

# Good - Separated concerns
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        # Database logic
        pass

class EmailService:
    def send_welcome(self, user):
        # Email logic
        pass

class UserReportGenerator:
    def generate(self, user):
        # Reporting logic
        pass
```

### Do
- Encapsulate related data and behavior
- Separate concerns (data access, business logic, presentation)
- Create cohesive modules
- Make reasons for change explicit

### Don't
- Mix data access, logic, and UI in one class
- Create "god objects" that do everything
- Couple unrelated functionality

### AI Pitfalls
- Cramming multiple operations into one class
- Creating utility classes with unrelated methods
- Mixing infrastructure and domain logic

---

## Composition Over Inheritance

**Definition:** Prefer combining objects to form behavior over creating deep class hierarchies. Favor "has-a" relationships over "is-a".

**Supported by:** *The Pragmatic Programmer*, *Design Patterns*

### Examples

```python
# Bad - Rigid inheritance hierarchy
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins cannot fly")

# Good - Composition with behavior injection
class FlyBehavior:
    def fly(self):
        pass

class CanFly(FlyBehavior):
    def fly(self):
        return "Flying"

class CannotFly(FlyBehavior):
    def fly(self):
        return "Cannot fly"

class Bird:
    def __init__(self, fly_behavior):
        self.fly_behavior = fly_behavior
    
    def perform_fly(self):
        return self.fly_behavior.fly()

# Usage
sparrow = Bird(CanFly())
penguin = Bird(CannotFly())
```

### Do
- Use interfaces or protocols to define contracts
- Inject dependencies and behaviors
- Compose small, focused objects
- Favor delegation over inheritance

### Don't
- Create deep inheritance hierarchies (>3 levels)
- Inherit just to override behavior
- Use inheritance for code reuse alone
- Force unnatural "is-a" relationships

### AI Pitfalls
- Defaulting to inheritance for code reuse
- Creating rigid class hierarchies
- Not recognizing when composition is clearer

---

## Program to an Interface, Not an Implementation

**Definition:** Depend on abstractions (interfaces, protocols) rather than concrete implementations. This enables flexibility and testability.

**Supported by:** *Design Patterns*, *Code Complete*, Dependency Inversion Principle

### Examples

```python
# Bad - Depends on concrete implementation
class OrderProcessor:
    def __init__(self):
        self.payment = StripePayment()  # Hard-coded dependency
    
    def process(self, order):
        self.payment.charge(order.total)

# Good - Depends on abstraction
class PaymentProcessor:
    def charge(self, amount):
        raise NotImplementedError

class StripePayment(PaymentProcessor):
    def charge(self, amount):
        # Stripe-specific logic
        pass

class PayPalPayment(PaymentProcessor):
    def charge(self, amount):
        # PayPal-specific logic
        pass

class OrderProcessor:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment = payment_processor
    
    def process(self, order):
        self.payment.charge(order.total)

# Usage - Easy to swap implementations
processor = OrderProcessor(StripePayment())
# or
processor = OrderProcessor(PayPalPayment())
```

### Do
- Define interfaces for key abstractions
- Inject dependencies via constructors
- Use dependency injection frameworks when appropriate
- Code against contracts, not implementations

### Don't
- Hard-code concrete class names
- Use `isinstance()` checks to switch behavior
- Create tight coupling to specific implementations

### AI Pitfalls
- Using fixed class names instead of interfaces
- Not recognizing opportunities for abstraction
- Creating concrete dependencies in constructors

---

## Essential Design Patterns

### Factory Pattern

**Purpose:** Delegate object creation to factory methods or classes. Decouples client code from concrete instantiation.

**Use when:** Object creation is complex or varies based on conditions.

```python
# Example
class LoggerFactory:
    @staticmethod
    def get_logger(log_type):
        if log_type == "file":
            return FileLogger()
        elif log_type == "console":
            return ConsoleLogger()
        elif log_type == "cloud":
            return CloudLogger()
        else:
            raise ValueError(f"Unknown logger type: {log_type}")

# Usage
logger = LoggerFactory.get_logger("file")
logger.log("Application started")
```

### Strategy Pattern

**Purpose:** Define a family of interchangeable algorithms and make them swappable at runtime.

**Use when:** You need different behaviors for the same operation.

```python
# Example
class SortStrategy:
    def sort(self, data):
        raise NotImplementedError

class QuickSort(SortStrategy):
    def sort(self, data):
        # Quick sort implementation
        pass

class MergeSort(SortStrategy):
    def sort(self, data):
        # Merge sort implementation
        pass

class DataProcessor:
    def __init__(self, sort_strategy: SortStrategy):
        self.sorter = sort_strategy
    
    def process(self, data):
        sorted_data = self.sorter.sort(data)
        return sorted_data

# Usage
processor = DataProcessor(MergeSort())
result = processor.process([3, 1, 4, 1, 5])
```

### Observer Pattern

**Purpose:** Define a one-to-many dependency where changes in one object notify all dependents automatically.

**Use when:** Multiple objects need to react to state changes.

```python
# Example
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer:
    def update(self, event):
        raise NotImplementedError

class EmailNotifier(Observer):
    def update(self, event):
        print(f"Sending email for: {event}")

class SlackNotifier(Observer):
    def update(self, event):
        print(f"Posting to Slack: {event}")

# Usage
order_system = Subject()
order_system.attach(EmailNotifier())
order_system.attach(SlackNotifier())
order_system.notify("Order #123 shipped")
```

### Decorator Pattern

**Purpose:** Dynamically add responsibilities to objects without modifying their class.

**Use when:** You need flexible, composable enhancements.

```python
# Example
class Notifier:
    def send(self, message):
        raise NotImplementedError

class BasicNotifier(Notifier):
    def send(self, message):
        print(f"Basic notification: {message}")

class NotifierDecorator(Notifier):
    def __init__(self, notifier: Notifier):
        self._notifier = notifier
    
    def send(self, message):
        self._notifier.send(message)

class SlackDecorator(NotifierDecorator):
    def send(self, message):
        super().send(message)
        print(f"Also sent to Slack: {message}")

class EmailDecorator(NotifierDecorator):
    def send(self, message):
        super().send(message)
        print(f"Also sent via email: {message}")

# Usage - Compose behaviors
notifier = EmailDecorator(SlackDecorator(BasicNotifier()))
notifier.send("System alert")
```

### Adapter Pattern

**Purpose:** Convert one interface into another that clients expect. Enables incompatible interfaces to work together.

**Use when:** Integrating legacy systems or third-party libraries.

```python
# Example
class LegacyPrinter:
    def print_text(self, text):
        print(f"[LEGACY] {text}")

class ModernPrinter:
    def print(self, content):
        raise NotImplementedError

class PrinterAdapter(ModernPrinter):
    def __init__(self, legacy_printer: LegacyPrinter):
        self.legacy = legacy_printer
    
    def print(self, content):
        self.legacy.print_text(content)

# Usage
old_printer = LegacyPrinter()
adapter = PrinterAdapter(old_printer)
adapter.print("Hello World")  # Uses modern interface, delegates to legacy
```

### Command Pattern

**Purpose:** Encapsulate a request as an object, enabling queuing, logging, or undoable operations.

**Use when:** You need to queue operations, support undo/redo, or log actions.

```python
# Example
class Command:
    def execute(self):
        raise NotImplementedError
    
    def undo(self):
        raise NotImplementedError

class Light:
    def on(self):
        print("Light is ON")
    
    def off(self):
        print("Light is OFF")

class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self):
        self.light.on()
    
    def undo(self):
        self.light.off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light
    
    def execute(self):
        self.light.off()
    
    def undo(self):
        self.light.on()

# Usage
living_room_light = Light()
light_on = LightOnCommand(living_room_light)
light_on.execute()  # Light is ON
light_on.undo()     # Light is OFF
```

### Singleton Pattern

**Purpose:** Ensure only one instance of a class exists globally.

**Use when:** You need a single point of access (e.g., config, logger, connection pool).

**Caution:** Often overused. Consider dependency injection instead.

```python
# Example
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class ConfigManager(Singleton):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = {}
            self.initialized = True

# Usage
config1 = ConfigManager()
config2 = ConfigManager()
assert config1 is config2  # Same instance
```

---

## Pattern Usage Guidelines

### Do
- Apply patterns when they improve clarity and flexibility
- Choose patterns based on structural fit
- Use patterns to communicate design intent
- Combine patterns when appropriate

### Don't
- Force patterns into simple code
- Use patterns for the sake of patterns
- Apply patterns without understanding the problem
- Over-abstract with unnecessary pattern layers

### AI Pitfalls
- Predicting patterns where none are needed
- Misnaming pattern roles (e.g., calling a simple factory a "Factory Pattern")
- Misapplying pattern intent (e.g., Singleton for everything)
- Creating pattern boilerplate without actual benefit

---

## Summary

Good architecture is:
- **Modular** - clear boundaries and responsibilities
- **Flexible** - uses composition and interfaces
- **Abstract** - depends on contracts, not implementations
- **Pattern-aware** - applies proven solutions appropriately

When designing systems, ask:
- Does each module have one clear responsibility?
- Can I swap implementations easily?
- Am I using inheritance or composition?
- Does this pattern solve a real structural problem?
