"""
Migration 0010 empties the sample default values older rows hold: English descriptions
(L-55) and the theme's fake supplier address and phone (L-58), see D-056.

Same pattern as test_migrations.py: rows are made with the models of migration 0009,
as they stand on the host before the deploy, then the real migration runs on them.
"""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

BEFORE = [("core", "0009_cartorder_address_255")]
AFTER = [("core", "0010_blank_sample_defaults")]


def migrate_to(target):
    executor = MigrationExecutor(connection)
    executor.migrate(target)
    return executor.loader.project_state(target).apps


@pytest.fixture
def old_apps():
    yield migrate_to(BEFORE)
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())


def test_old_english_defaults_are_emptied_and_real_text_is_kept(old_apps):
    Product = old_apps.get_model("core", "Product")
    Vendor = old_apps.get_model("core", "Vendor")
    untouched = Product.objects.create(title="Cà rốt")  # gets the old default sentences
    written = Product.objects.create(title="Bí đỏ", description="Bí đỏ hữu cơ")
    vendor = Vendor.objects.create(name="HTX Rau")

    apps = migrate_to(AFTER)

    product = apps.get_model("core", "Product").objects.get(pk=untouched.pk)
    assert (product.description, product.specification) == ("", "")
    assert apps.get_model("core", "Product").objects.get(pk=written.pk).description == "Bí đỏ hữu cơ"
    vendor = apps.get_model("core", "Vendor").objects.get(pk=vendor.pk)
    assert (vendor.description, vendor.address, vendor.contact) == ("", "", "")
