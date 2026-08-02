from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
        ('ticket_sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ticket',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='order',
                to='ticket_sales.ticket',
            ),
        ),
    ]
