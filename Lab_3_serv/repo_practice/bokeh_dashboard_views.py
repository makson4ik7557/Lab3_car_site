"""
Bokeh Dashboard views для аналітичних графіків
АРХІТЕКТУРА: Database → Repository → REST API ViewSet → Dashboard (pandas + Bokeh)

Використовує ті самі 6 агрегованих запитів що й Plotly dashboard
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
import logging
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.transform import cumsum
from bokeh.palettes import Category20c, Viridis256
from math import pi

logger = logging.getLogger(__name__)


def call_analytics_api(request, endpoint, params=None):
    """
    Helper функція для виклику REST API analytics endpoints
    Той самий код що і в Plotly dashboard + конвертація Decimal для Bokeh
    """
    from .views import AnalyticsViewSet
    from rest_framework.test import APIRequestFactory
    from django.http import QueryDict
    from decimal import Decimal

    if not request.user.is_authenticated:
        return []

    try:
        factory = APIRequestFactory()
        query_string = '&'.join([f'{k}={v}' for k, v in (params or {}).items()])
        api_request = factory.get(f'/api/analytics/{endpoint}/?{query_string}')
        api_request.user = request.user
        api_request.query_params = QueryDict(query_string)

        viewset = AnalyticsViewSet()
        viewset.request = api_request
        viewset.format_kwarg = None

        method_map = {
            'sales-by-employee': viewset.sales_by_employee,
            'profit-by-brand': viewset.profit_by_brand,
            'transaction-dynamics': viewset.transaction_dynamics,
            'top-customers': viewset.top_customers,
            'car-price-statistics': viewset.car_price_statistics,
            'dealer-balance-summary': viewset.dealer_balance_summary,
        }

        method = method_map.get(endpoint)
        if method:
            response = method(api_request)
            if hasattr(response, 'data'):
                data = response.data.get('data', [])

                # ВАЖЛИВО: Bokeh не може серіалізувати Decimal, конвертуємо в float
                for record in data:
                    for key, value in list(record.items()):
                        if isinstance(value, Decimal):
                            record[key] = float(value)
                        elif value is None:
                            record[key] = 0.0

                logger.info(f"✅ Bokeh API call to {endpoint}: {len(data)} records")
                return data
        return []
    except Exception as e:
        logger.error(f"Bokeh API call failed for {endpoint}: {str(e)}")
        return []


@login_required
def bokeh_dashboard(request):
    """
    Bokeh дашборд з 6 графіками (v2)

    1. Bar chart (vbar) - продажі по співробітниках
    2. Pie chart (wedge) - розподіл прибутку по марках
    3. Line chart - динаміка транзакцій дилерів
    4. Scatter plot (circle) - витрати топ клієнтів
    5. Multi-bar chart - статистика цін по рокам
    6. Grouped bar chart - баланси дилерів
    """
    # Отримуємо параметри фільтрації
    min_sales = int(request.GET.get('min_sales', 1))
    min_cars = int(request.GET.get('min_cars', 1))
    min_amount = float(request.GET.get('min_amount', 0))
    top_customers_limit = int(request.GET.get('top_customers', 10))
    min_cars_year = int(request.GET.get('min_cars_year', 1))
    min_transactions = int(request.GET.get('min_transactions', 1))

    charts_components = []

    # === ГРАФІК 1: Vertical Bar Chart - Продажі по співробітниках ===
    sales_data = call_analytics_api(request, 'sales-by-employee', {'min_sales': min_sales})
    df_sales = pd.DataFrame(sales_data)

    if not df_sales.empty:
        df_sales['full_name'] = df_sales['employee__first_name'] + ' ' + df_sales['employee__last_name']

        source = ColumnDataSource(df_sales)

        p1 = figure(
            x_range=df_sales['full_name'].tolist(),
            height=400,
            title=f'Продажі по співробітниках (мін. {min_sales} продаж)',
            toolbar_location=None,
            tools=""
        )

        p1.vbar(
            x='full_name',
            top='total_revenue',
            width=0.8,
            source=source,
            color='#3b82f6',
            legend_label="Дохід"
        )

        hover = HoverTool(tooltips=[
            ("Співробітник", "@full_name"),
            ("Дохід", "@total_revenue{$0,0}"),
            ("Продажів", "@total_sales")
        ])
        p1.add_tools(hover)

        p1.xaxis.major_label_orientation = pi/4
        p1.yaxis.axis_label = "Дохід ($)"

        script1, div1 = components(p1)
        charts_components.append(('chart1', script1, div1))
    else:
        charts_components.append(('chart1', None, None))

    # === ГРАФІК 2: Pie Chart (Wedge) - Розподіл по марках ===
    brand_data = call_analytics_api(request, 'profit-by-brand', {'min_cars': min_cars})
    df_brands = pd.DataFrame(brand_data)

    if not df_brands.empty:
        df_brands['angle'] = df_brands['total_revenue'] / df_brands['total_revenue'].sum() * 2 * pi
        df_brands['color'] = Category20c[len(df_brands)] if len(df_brands) <= 20 else Viridis256[:len(df_brands)]
        df_brands['percentage'] = (df_brands['total_revenue'] / df_brands['total_revenue'].sum() * 100).round(1)

        source = ColumnDataSource(df_brands)

        p2 = figure(
            height=400,
            title=f'Розподіл прибутку по марках (мін. {min_cars} авто)',
            toolbar_location=None,
            tools="hover",
            tooltips="@car__make: @total_revenue{$0,0} (@percentage%)",
            x_range=(-0.5, 1.0)
        )

        p2.wedge(
            x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True),
            end_angle=cumsum('angle'),
            line_color="white",
            fill_color='color',
            legend_field='car__make',
            source=source
        )

        p2.axis.axis_label = None
        p2.axis.visible = False
        p2.grid.grid_line_color = None

        script2, div2 = components(p2)
        charts_components.append(('chart2', script2, div2))
    else:
        charts_components.append(('chart2', None, None))

    # === ГРАФІК 3: Line Chart - Динаміка транзакцій ===
    transaction_data = call_analytics_api(request, 'transaction-dynamics', {'min_amount': min_amount})
    df_transactions = pd.DataFrame(transaction_data)

    if not df_transactions.empty:
        # Отримуємо всіх унікальних дилерів для x_range
        all_dealers = df_transactions['dealer__username'].unique().tolist()

        # Створюємо pivot таблицю для правильного відображення ліній
        df_pivot = df_transactions.pivot_table(
            index='dealer__username',
            columns='transaction_type',
            values='total_amount',
            fill_value=0
        ).reset_index()

        p3 = figure(
            x_range=all_dealers,
            height=400,
            title=f'Динаміка транзакцій дилерів (мін. ${min_amount:,.0f})',
            x_axis_label='Дилер',
            y_axis_label='Сума ($)',
            toolbar_location=None
        )

        colors = {'BUY': '#ef4444', 'SELL': '#10b981', 'MODIFY': '#f59e0b'}

        # Малюємо лінії для кожного типу транзакції
        for trans_type in df_transactions['transaction_type'].unique():
            df_type = df_transactions[df_transactions['transaction_type'] == trans_type]

            # Сортуємо по дилерах для коректного відображення
            df_type = df_type.sort_values('dealer__username')

            # Створюємо список x-координат (індекси дилерів)
            dealers_list = df_type['dealer__username'].tolist()
            amounts_list = df_type['total_amount'].tolist()

            # Створюємо ColumnDataSource
            source = ColumnDataSource(df_type)

            # Малюємо лінію (використовуємо dealer__username як категоріальну вісь)
            line = p3.line(
                x=dealers_list,
                y=amounts_list,
                legend_label=trans_type,
                line_width=3,
                color=colors.get(trans_type, '#3b82f6')
            )

            # Малюємо точки з HoverTool
            circles = p3.circle(
                x='dealer__username',
                y='total_amount',
                source=source,
                size=10,
                color=colors.get(trans_type, '#3b82f6'),
                alpha=0.8
            )

            # Додаємо HoverTool для кожної серії окремо
            hover = HoverTool(
                renderers=[circles],
                tooltips=[
                    ("Дилер", "@dealer__username"),
                    ("Тип", "@transaction_type"),
                    ("Сума", "@total_amount{$0,0}"),
                    ("Кількість", "@transaction_count")
                ]
            )
            p3.add_tools(hover)

        p3.legend.location = "top_left"
        p3.legend.click_policy = "hide"
        p3.xaxis.major_label_orientation = pi/4

        script3, div3 = components(p3)
        charts_components.append(('chart3', script3, div3))
    else:
        charts_components.append(('chart3', None, None))

    # === ГРАФІК 4: Scatter Plot - Витрати клієнтів ===
    customers_data = call_analytics_api(request, 'top-customers', {'limit': top_customers_limit})
    df_customers = pd.DataFrame(customers_data)

    if not df_customers.empty:
        df_customers['full_name'] = df_customers['customer__first_name'] + ' ' + df_customers['customer__last_name']

        source = ColumnDataSource(df_customers)

        p4 = figure(
            height=400,
            title=f'Топ-{top_customers_limit} клієнтів по витратам',
            x_axis_label='Куплено авто',
            y_axis_label='Витрачено ($)'
        )

        p4.circle(
            'cars_purchased',
            'total_spent',
            size=15,
            color='#8b5cf6',
            alpha=0.6,
            source=source
        )

        hover = HoverTool(tooltips=[
            ("Клієнт", "@full_name"),
            ("Куплено авто", "@cars_purchased"),
            ("Витрачено", "@total_spent{$0,0}"),
            ("Середня ціна", "@average_purchase{$0,0}")
        ])
        p4.add_tools(hover)

        script4, div4 = components(p4)
        charts_components.append(('chart4', script4, div4))
    else:
        charts_components.append(('chart4', None, None))

    # === ГРАФІК 5: Multi-bar Chart - Ціни по рокам ===
    car_stats_data = call_analytics_api(request, 'car-price-statistics', {'min_cars': min_cars_year})
    df_car_stats = pd.DataFrame(car_stats_data)

    if not df_car_stats.empty:
        df_car_stats['year_str'] = df_car_stats['year'].astype(str)

        source = ColumnDataSource(df_car_stats)

        p5 = figure(
            x_range=df_car_stats['year_str'].tolist(),
            height=400,
            title=f'Статистика цін по рокам (мін. {min_cars_year} авто)',
            toolbar_location=None
        )

        p5.vbar(x='year_str', top='average_price', width=0.3, source=source,
                color='#3b82f6', legend_label="Середня")
        p5.line('year_str', 'max_price', source=source, line_width=2,
                color='#ef4444', legend_label="Максимум")
        p5.line('year_str', 'min_price', source=source, line_width=2,
                color='#10b981', legend_label="Мінімум")

        p5.circle('year_str', 'max_price', source=source, size=8, color='#ef4444')
        p5.circle('year_str', 'min_price', source=source, size=8, color='#10b981')

        p5.yaxis.axis_label = "Ціна ($)"
        p5.xaxis.axis_label = "Рік"

        hover = HoverTool(tooltips=[
            ("Рік", "@year"),
            ("Середня", "@average_price{$0,0}"),
            ("Авто", "@cars_count")
        ])
        p5.add_tools(hover)

        script5, div5 = components(p5)
        charts_components.append(('chart5', script5, div5))
    else:
        charts_components.append(('chart5', None, None))

    # === ГРАФІК 6: Grouped Bar Chart - Баланси дилерів ===
    dealer_balance_data = call_analytics_api(request, 'dealer-balance-summary', {'min_transactions': min_transactions})
    df_dealer_balance = pd.DataFrame(dealer_balance_data)

    if not df_dealer_balance.empty:
        from bokeh.transform import dodge

        dealers = df_dealer_balance['dealer__username'].tolist()
        source = ColumnDataSource(df_dealer_balance)

        p6 = figure(
            x_range=dealers,
            height=400,
            title=f'Операції дилерів (мін. {min_transactions} транзакцій)',
            toolbar_location=None
        )

        # Використовуємо dodge transform для групування барів
        buy_renderer = p6.vbar(x=dodge('dealer__username', -0.25, range=p6.x_range),
                top='buy_transactions', width=0.2,
                source=source, color='#ef4444', legend_label="Купівлі")

        sell_renderer = p6.vbar(x=dodge('dealer__username', 0.0, range=p6.x_range),
                top='sell_transactions', width=0.2,
                source=source, color='#10b981', legend_label="Продажі")

        modify_renderer = p6.vbar(x=dodge('dealer__username', 0.25, range=p6.x_range),
                top='modify_transactions', width=0.2,
                source=source, color='#f59e0b', legend_label="Модифікації")

        p6.yaxis.axis_label = "Кількість операцій"
        p6.xaxis.axis_label = "Дилер"

        # Окремі tooltips для кожного типу операції - використовуємо renderers
        hover_buy = HoverTool(renderers=[buy_renderer], tooltips=[
            ("Дилер", "@dealer__username"),
            ("Купівлі", "@buy_transactions"),
            ("Сума купівель", "@total_buy_amount{$0,0}")
        ])
        hover_sell = HoverTool(renderers=[sell_renderer], tooltips=[
            ("Дилер", "@dealer__username"),
            ("Продажі", "@sell_transactions"),
            ("Сума продажів", "@total_sell_amount{$0,0}")
        ])
        hover_modify = HoverTool(renderers=[modify_renderer], tooltips=[
            ("Дилер", "@dealer__username"),
            ("Модифікації", "@modify_transactions"),
            ("Баланс", "@current_balance{$0,0}")
        ])
        p6.add_tools(hover_buy, hover_sell, hover_modify)

        script6, div6 = components(p6)
        charts_components.append(('chart6', script6, div6))
    else:
        charts_components.append(('chart6', None, None))

    # Формуємо контекст
    context = {
        'filters': {
            'min_sales': min_sales,
            'min_cars': min_cars,
            'min_amount': min_amount,
            'top_customers': top_customers_limit,
            'min_cars_year': min_cars_year,
            'min_transactions': min_transactions
        }
    }

    # Додаємо компоненти графіків
    for chart_name, script, div in charts_components:
        context[f'{chart_name}_script'] = script
        context[f'{chart_name}_div'] = div

    return render(request, 'repo_practice/bokeh_dashboard.html', context)

