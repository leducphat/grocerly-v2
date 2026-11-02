"""
The data migration that links old order lines to their product (L-25, D-045).

The rows are made with the models of migration 0007, as they stand on the host before
the deploy, and then the real migration runs on them.
"""

from decimal import Decimal

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

BEFORE = [("core", "0007_cartorderitem_product")]
AFTER = [("core", "0008_fill_order_item_product")]


def migrate_to(target):
    executor = MigrationExecutor(connection)
    executor.migrate(target)
    return executor.loader.project_state(target).apps


@pytest.fixture
def old_apps():
    yield migrate_to(BEFORE)
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())


def order_line(apps, title):
    order = apps.get_model("core", "CartOrder").objects.create(price=Decimal("25000.00"))
    return apps.get_model("core", "CartOrderItem").objects.create(order=order, item=title, quantity=1)


def product_id_of(line):
    migrate_to(AFTER)
    line.refresh_from_db()
    return line.product_id


def test_line_is_linked_to_the_only_product_with_its_title(old_apps):
    product = old_apps.get_model("core", "Product").objects.create(title="Cà rốt")
    line = order_line(old_apps, "Cà rốt")

    assert product_id_of(line) == product.id


def test_line_is_linked_to_a_product_deleted_softly_since_the_sale(old_apps):
    product = old_apps.get_model("core", "Product").objects.create(title="Cà rốt", is_deleted=True)
    line = order_line(old_apps, "Cà rốt")

    assert product_id_of(line) == product.id


def test_line_stays_empty_when_two_products_share_its_title(old_apps):
    Product = old_apps.get_model("core", "Product")
    Product.objects.create(title="Cà rốt")
    Product.objects.create(title="Cà rốt")
    line = order_line(old_apps, "Cà rốt")

    assert product_id_of(line) is None


def test_line_stays_empty_when_no_product_has_its_title(old_apps):
    old_apps.get_model("core", "Product").objects.create(title="Cà chua")
    line = order_line(old_apps, "Cà rốt")

    assert product_id_of(line) is None


def test_line_already_linked_is_left_alone(old_apps):
    Product = old_apps.get_model("core", "Product")
    linked = Product.objects.create(title="Tên khác")
    Product.objects.create(title="Cà rốt")
    line = order_line(old_apps, "Cà rốt")
    line.product = linked
    line.save()

    assert product_id_of(line) == linked.id


def test_going_back_to_0006_removes_the_column_and_keeps_the_lines(old_apps):
    line = order_line(old_apps, "Cà rốt")
    migrate_to(AFTER)

    apps = migrate_to([("core", "0006_alter_cartorder_product_status")])

    CartOrderItem = apps.get_model("core", "CartOrderItem")
    assert "product" not in [field.name for field in CartOrderItem._meta.get_fields()]
    assert CartOrderItem.objects.get(pk=line.pk).item == "Cà rốt"
