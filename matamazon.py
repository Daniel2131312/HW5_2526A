# TODO add all imports needed here
import json
import sys
from distutils.sysconfig import customize_compiler
from itertools import product
import os
from sys import stderr


class InvalidIdException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InvalidPriceException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class Customer:

    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("ID is invalid")

        self.id = int(id)
        self.name = name[:].replace('_', ' ')
        self.city = city[:].replace('_', ' ')
        self.address = address[:].replace('_', ' ')


    def __repr__(self):
        return f"Customer(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"

    pass


class Supplier:
    def __init__(self, id, name, city, address):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("ID is invalid")

        self.id = int(id)
        self.name = name[:].replace('_', ' ')
        self.city = city[:].replace('_', ' ')
        self.address = address[:].replace('_', ' ')

    def __repr__(self):
        return f"Supplier(id={self.id}, name='{self.name}', city='{self.city}', address='{self.address}')"

    pass


class Product:
    def __init__(self, id, name, price, supplier_id, quantity):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("ID is invalid")

        if not isinstance(price, (float, int)) or price < 0:
            raise InvalidPriceException("Price is invalid")

        if not isinstance(supplier_id, int) or supplier_id < 0:
            raise InvalidIdException("Supplier_id is invalid")

        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Quantity is invalid")

        self.id = id
        self.name = name[:].replace('_', ' ')
        self.price = price
        self.supplier_id = supplier_id
        self.quantity = quantity

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, supplier_id={self.supplier_id}, quantity={self.quantity})"

    def __lt__(self, other):
        return self.price < other.price

    pass


class Order:
    def __init__(self, id, customer_id, product_id, quantity, total_price):
        if not isinstance(id, int) or id < 0:
            raise InvalidIdException("ID is invalid")

        if not isinstance(customer_id, int) or customer_id < 0:
            raise InvalidIdException("Customer id is invalid")

        if not isinstance(product_id, int) or product_id < 0:
            raise InvalidIdException("Product id is invalid")

        if not isinstance(quantity, int) or quantity < 0:
            raise InvalidIdException("Quantity is invalid")

        if not isinstance(total_price, (float, int)) or total_price < 0:
            raise InvalidPriceException("Total price is invalid")

        self.id = id
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.total_price = total_price

    def __repr__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id}, product_id={self.product_id}, quantity={self.quantity}, total_price={self.total_price})"

    pass


class MatamazonSystem:
    def __init__(self):
        self.recent_id = 1
        self.customers = {}
        self.suppliers = {}
        self.products = {}
        self.orders = {}

        pass

    def register_entity(self, entity, is_customer):
        if is_customer:
            if entity.id in self.customers:
                raise InvalidIdException("Customer already exists")

            self.customers[entity.id] = entity
        else:
            if entity.id in self.suppliers:
                raise InvalidIdException("Supplier already exists")

            self.suppliers[entity.id] = entity

        pass

    def add_or_update_product(self, product):
        if product.id in self.products.keys():
            if product.supplier_id != self.products[product.id].supplier_id:
                raise InvalidIdException("Unmatching suppliers")

            self.products[product.id].name = product.name
            self.products[product.id].price = product.price
            self.products[product.id].quantity = product.quantity
        else:
            self.products[product.id] = product


        pass

    def place_order(self, customer_id, product_id, quantity=1):
        if not isinstance(customer_id, int) or customer_id < 0 or customer_id not in self.customers:
            raise InvalidIdException("Customer_id is invalid")

        if not isinstance(product_id, int) or product_id < 0:
            raise InvalidIdException("Product_id is invalid")

        if not isinstance(quantity, int) or quantity < 0 :
            raise InvalidIdException("Quantity is invalid")

        if product_id not in self.products:
            return "The product does not exist in the system"

        if quantity > self.products[product_id].quantity:
            return "The quantity requested for this product is greater than the quantity in stock"

        self.products[product_id].quantity -= quantity
        order = Order(self.recent_id, customer_id, product_id, quantity, quantity*(self.products[product_id].price))
        self.orders[order.id] = order
        self.recent_id = self.recent_id + 1
        return "The order has been accepted in the system"

        pass

    def remove_object(self, _id, class_type):
        if not isinstance(_id, int) or _id < 0:
            raise InvalidIdException("ID is invalid")

        lc_class_type = class_type.lower().strip()

        if lc_class_type == "order":
            if _id not in self.orders.keys():
                raise InvalidIdException("ID is invalid")

            quantity = self.orders[_id].quantity
            self.products[self.orders[_id].product_id].quantity += quantity
            del self.orders[_id]
            return quantity
        elif lc_class_type == "customer":
            if not _id in self.customers.keys():
                raise InvalidIdException("ID is invalid")
            for order in self.orders.values():
                if order.customer_id == _id:
                    raise InvalidIdException("ID is invalid")
            del self.customers[_id]
        elif lc_class_type == "supplier":
            if not _id in self.suppliers.keys():
                raise InvalidIdException("ID is invalid")
            for order in self.orders.values():
                if self.products[order.product_id].supplier_id == _id:
                    raise InvalidIdException("ID is invalid")
            del self.suppliers[_id]
        elif lc_class_type == "product":
            if not _id in self.products.keys():
                raise InvalidIdException("ID is invalid")
            for order in self.orders.values():
                if order.product_id == _id:
                    raise InvalidIdException("ID is invalid")
            del self.products[_id]

        pass

    def search_products_filter(self, product, query, max_price):
        return query in product.name and product.quantity > 0 and (max_price is None or max_price >= product.price)

    def search_products(self, query, max_price=None):
        if max_price is not None and not isinstance(max_price, (int, float)):
            raise InvalidPriceException("Max_price is invalid")

        mp = float(max_price) if max_price is not None else None
        prods = [prod for prod in self.products.values() if self.search_products_filter(prod, query, mp)]

        return sorted(prods)


    def export_system_to_file(self, path):
        with open(path, "w") as f:
            for customer in self.customers.values():
                print(customer.__repr__(), file=f)

            for supplier in self.suppliers.values():
                print(supplier.__repr__(), file=f)

            for prod in self.products.values():
                print(prod.__repr__(), file=f)

        pass

    def get_orders_by_city(self):
        orders_by_city = {self.suppliers[self.products[order.product_id].supplier_id].city :
                              [] for order in self.orders.values()}

        for city in orders_by_city.keys():
            orders_by_city[city] = [order.__repr__() for order in self.orders.values()
                                    if self.suppliers[self.products[order.product_id].supplier_id].city == city]

        return orders_by_city


    def export_orders(self, out_file):
        json.dump(self.get_orders_by_city(), out_file)

        pass


def load_system_from_file(path):
    if not os.path.isfile(path):
        raise FileNotFoundError("File not found")

    system = MatamazonSystem()

    with open(path, "r") as f:
        for line in f:
            if line.startswith("Customer") or line.startswith("Supplier"):
                system.register_entity(eval(line), line.startswith("Customer"))
            elif line.startswith("Product"):
                system.add_or_update_product(eval(line))

    return system

    pass

if __name__ == "__main__":

    try:
        if "-l" not in sys.argv:
            print(
                    "Usage: python3 matamazon.py -l < matamazon_log > -s < matamazon_system > -o <output_file> -os <out_matamazon_system>",
                    file=sys.stderr)
            exit(0)

        valid_flags = ["-l", "-s", "-o", "-os"]

        for flag in range(1, len(sys.argv), 2):
            if sys.argv[flag] not in valid_flags:
                print(
                    "Usage: python3 matamazon.py -l < matamazon_log > -s < matamazon_system > -o <output_file> -os <out_matamazon_system>",
                    file=sys.stderr)
                exit(0)

        if "-s" in sys.argv:
            system = load_system_from_file(sys.argv[sys.argv.index("-s") + 1])
        else:
            system = MatamazonSystem()

        if not os.path.isfile(sys.argv[sys.argv.index("-l") + 1]):
            raise FileNotFoundError("File not found")

        with open(sys.argv[sys.argv.index("-l") + 1], "r") as f:
            for line in f:
                data = line.split()
                if data[0] == "register":
                    if data[1] == "customer":
                        system.register_entity(Customer(int(data[2]), data[3], data[4], data[5]), True)
                    elif data[1] == "supplier":
                        system.register_entity(Supplier(int(data[2]), data[3], data[4], data[5]), False)
                elif data[0] == "add" or data[0] == "update":
                    system.add_or_update_product(Product(int(data[1]), data[2], float(data[3]), int(data[4]), int(data[5])))
                elif data[0] == "order":
                    if len(data) == 3:
                        system.place_order(int(data[1]), int(data[2]))
                    elif len(data) == 4:
                        system.place_order(int(data[1]), int(data[2]), int(data[3]))
                elif data[0] == "remove":
                    quantity = system.remove_object(int(data[2]), data[1])
                elif data[0] == "search":
                    if len(data) == 2:
                        products = system.search_products(data[1])
                    elif len(data) == 3:
                        products = system.search_products(data[1], float(data[2]))
                    print(products)

        if "-os" in sys.argv:
            system.export_system_to_file(sys.argv[sys.argv.index("-os") + 1])

        if "-o" in sys.argv:
            with open(sys.argv[sys.argv.index("-o") + 1], "w") as f:
                system.export_orders(f)
        else:
            print(json.dumps(system.get_orders_by_city()))

    except Exception as e:
        print("The matamazon script has encountered an error")
        exit(0)
