from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0004_aberturacaixa'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagamento',
            name='caixa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pagamentos', to='caixa.aberturacaixa'),
        ),
        migrations.AddField(
            model_name='movimentacaocaixa',
            name='caixa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimentacoes', to='caixa.aberturacaixa'),
        ),
    ]