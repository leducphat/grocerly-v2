from django.db import migrations


def fill_product(apps, schema_editor):
    """Link the existing order lines to their product (L-25, D-045).

    A line only holds the product's title, so it is linked only when exactly one
    product has that title: a wrong link is worse than an empty one, because the stock
    and the right to review follow it. In a migration `Product.objects` is the plain
    manager, so a product deleted softly since the sale is found too.
    """
    Product = apps.get_model("core", "Product")
    CartOrderItem = apps.get_model("core", "CartOrderItem")

    for line in CartOrderItem.objects.filter(product__isnull=True):
        matches = list(Product.objects.filter(title=line.item)[:2])
        if len(matches) == 1:
            line.product = matches[0]
            line.save(update_fields=["product"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_cartorderitem_product"),
    ]

    # Going back leaves the links in place: 0007 drops the column right after.
    operations = [
        migrations.RunPython(fill_product, migrations.RunPython.noop),
    ]
