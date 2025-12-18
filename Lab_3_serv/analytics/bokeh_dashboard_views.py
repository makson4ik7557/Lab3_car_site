"""
Bokeh Dashboard views для аналітичних графіків

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
    Код впринципі той самий що і в Plotly dashboard + конвертація Decimal для Bokeh
    """
    from repo_practice.views import AnalyticsViewSet
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

                # Bokeh не може серіалізувати Decimal, конвертуємо в float
                for record in data:
                    for key, value in list(record.items()):
                        if isinstance(value, Decimal):
                            record[key] = float(value)
                        elif value is None:
                            record[key] = 0.0

                logger.info(f"Bokeh API call to {endpoint}: {len(data)} records")
                return data
        return []
    except Exception as e:
        logger.error(f"Bokeh API call failed for {endpoint}: {str(e)}")
        return []


def create_sales_by_employee_chart(request, min_sales):
    """
    Графік 1: Vertical Bar Chart - Продажі по співробітниках

    Returns:
        tuple: (script, div) або (None, None)
    """
    try:
        from .services import AnalyticsService
        analytics = AnalyticsService()

        # DataFrame напряму з Service (вже з full_name)
        df_sales = analytics.get_sales_by_employee_df(min_sales)

        if df_sales.empty:
            logger.warning(f"Bokeh графік 1: Немає даних для min_sales={min_sales}")
            return None, None

        logger.info(f"Bokeh графік 1: Отримано {len(df_sales)} записів")

        # ✅ ВИПРАВЛЕННЯ: Додаємо ID до full_name для унікальності (Bokeh вимагає унікальні x_range)
        df_sales['display_name'] = df_sales['full_name'] + ' (#' + df_sales['employee__id'].astype(str) + ')'

        logger.info(f"Bokeh графік 1: Перші 3 display_name: {df_sales['display_name'].head(3).tolist()}")

        source = ColumnDataSource(df_sales)

        p = figure(
            x_range=df_sales['display_name'].tolist(),  # ✅ ВИПРАВЛЕНО: display_name
            height=400,
            title=f'Продажі по співробітниках (мін. {min_sales} продаж)',
            toolbar_location=None,
            tools=""
        )

        p.vbar(
            x='display_name',  # ✅ ВИПРАВЛЕНО: display_name
            top='total_revenue',
            width=0.8,
            source=source,
            color='#3b82f6',
            legend_label="Дохід"
        )

        hover = HoverTool(tooltips=[
            ("Співробітник", "@full_name"),  # ✅ Показуємо full_name без ID в tooltip
            ("ID", "@employee__id"),
            ("Дохід", "@total_revenue{$0,0}"),
            ("Продажів", "@total_sales")
        ])
        p.add_tools(hover)
        p.xaxis.major_label_orientation = pi/4
        p.yaxis.axis_label = "Дохід ($)"

        script, div = components(p)
        logger.info(f"Bokeh графік 1: components() успішно виконано, script length={len(script)}, div length={len(div)}")
        return script, div

    except Exception as e:
        logger.error(f"Bokeh графік 1: ПОМИЛКА - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None


def create_profit_by_brand_chart(request, min_cars):
    """
    Графік 2: Pie Chart (Wedge) - Розподіл прибутку по марках

    Returns:
        tuple: (script, div) або (None, None)
    """
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_brands = analytics.get_profit_by_brand_df(min_cars)

    if df_brands.empty:
        return None, None

    df_brands['angle'] = df_brands['total_revenue'] / df_brands['total_revenue'].sum() * 2 * pi

    num_brands = len(df_brands)
    if num_brands <= 2:
        df_brands['color'] = ['#3b82f6', '#ef4444'][:num_brands]
    elif num_brands <= 20:
        df_brands['color'] = Category20c[max(3, num_brands)][:num_brands]
    else:
        df_brands['color'] = Viridis256[:num_brands]

    df_brands['percentage'] = (df_brands['total_revenue'] / df_brands['total_revenue'].sum() * 100).round(1)
    source = ColumnDataSource(df_brands)

    p = figure(
        height=400,
        title=f'Розподіл прибутку по марках (мін. {min_cars} авто)',
        toolbar_location=None,
        tools="hover",
        tooltips="@car__make: @total_revenue{$0,0} (@percentage%)",
        x_range=(-0.5, 1.0)
    )

    p.wedge(
        x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True),
        end_angle=cumsum('angle'),
        line_color="white",
        fill_color='color',
        legend_field='car__make',
        source=source
    )

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return components(p)


def create_transaction_dynamics_chart(request, min_amount):
    """
    Графік 3: Line Chart - Динаміка транзакцій дилерів

    Returns:
        tuple: (script, div) або (None, None)
    """
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_transactions = analytics.get_transaction_dynamics_df(min_amount)

    if df_transactions.empty:
        return None, None

    all_dealers = df_transactions['dealer__username'].unique().tolist()
    df_pivot = df_transactions.pivot_table(
        index='dealer__username',
        columns='transaction_type',
        values='total_amount',
        fill_value=0
    ).reset_index()

    p = figure(
        x_range=all_dealers,
        height=400,
        title=f'Динаміка транзакцій дилерів (мін. ${min_amount:,.0f})',
        x_axis_label='Дилер',
        y_axis_label='Сума ($)',
        toolbar_location=None
    )

    colors = {'BUY': '#ef4444', 'SELL': '#10b981', 'MODIFY': '#f59e0b'}

    for trans_type in df_transactions['transaction_type'].unique():
        df_type = df_transactions[df_transactions['transaction_type'] == trans_type]
        df_type = df_type.sort_values('dealer__username')

        dealers_list = df_type['dealer__username'].tolist()
        amounts_list = df_type['total_amount'].tolist()
        source = ColumnDataSource(df_type)

        line = p.line(
            x=dealers_list,
            y=amounts_list,
            legend_label=trans_type,
            line_width=3,
            color=colors.get(trans_type, '#3b82f6')
        )

        circles = p.circle(
            x='dealer__username',
            y='total_amount',
            source=source,
            size=10,
            color=colors.get(trans_type, '#3b82f6'),
            alpha=0.8
        )

        hover = HoverTool(
            renderers=[circles],
            tooltips=[
                ("Дилер", "@dealer__username"),
                ("Тип", "@transaction_type"),
                ("Сума", "@total_amount{$0,0}"),
                ("Кількість", "@transaction_count")
            ]
        )
        p.add_tools(hover)

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.xaxis.major_label_orientation = pi/4

    return components(p)


def create_top_customers_chart(request, limit):
    """
    Графік 4: Scatter Plot - Витрати топ клієнтів

    Returns:
        tuple: (script, div) або (None, None)
    """
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_customers = analytics.get_top_customers_df(limit)

    if df_customers.empty:
        return None, None
    source = ColumnDataSource(df_customers)

    p = figure(
        height=400,
        title=f'Топ-{limit} клієнтів по витратам',
        x_axis_label='Куплено авто',
        y_axis_label='Витрачено ($)'
    )

    p.circle(
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
    p.add_tools(hover)

    return components(p)


def create_car_price_statistics_chart(request, min_cars_year):
    """
    Графік 5: Multi-bar Chart - Статистика цін по рокам

    Returns:
        tuple: (script, div) або (None, None)
    """
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_car_stats = analytics.get_car_price_statistics_df(min_cars_year)

    if df_car_stats.empty:
        return None, None
    source = ColumnDataSource(df_car_stats)

    p = figure(
        x_range=df_car_stats['year_str'].tolist(),
        height=400,
        title=f'Статистика цін по рокам (мін. {min_cars_year} авто)',
        toolbar_location=None
    )

    p.vbar(x='year_str', top='average_price', width=0.3, source=source,
            color='#3b82f6', legend_label="Середня")
    p.line('year_str', 'max_price', source=source, line_width=2,
            color='#ef4444', legend_label="Максимум")
    p.line('year_str', 'min_price', source=source, line_width=2,
            color='#10b981', legend_label="Мінімум")

    p.circle('year_str', 'max_price', source=source, size=8, color='#ef4444')
    p.circle('year_str', 'min_price', source=source, size=8, color='#10b981')

    p.yaxis.axis_label = "Ціна ($)"
    p.xaxis.axis_label = "Рік"

    hover = HoverTool(tooltips=[
        ("Рік", "@year"),
        ("Середня", "@average_price{$0,0}"),
        ("Авто", "@cars_count")
    ])
    p.add_tools(hover)

    return components(p)


def create_dealer_balance_chart(request, min_transactions):
    """
    Графік 6: Grouped Bar Chart - Баланси та операції дилерів

    Returns:
        tuple: (script, div) або (None, None)
    """
    from bokeh.transform import dodge
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service (Decimal вже конвертовано)
    df_dealer_balance = analytics.get_dealer_balance_summary_df(min_transactions)

    if df_dealer_balance.empty:
        return None, None

    dealers = df_dealer_balance['dealer__username'].tolist()
    source = ColumnDataSource(df_dealer_balance)

    p = figure(
        x_range=dealers,
        height=400,
        title=f'Операції дилерів (мін. {min_transactions} транзакцій)',
        toolbar_location=None
    )

    buy_renderer = p.vbar(x=dodge('dealer__username', -0.25, range=p.x_range),
            top='buy_transactions', width=0.2,
            source=source, color='#ef4444', legend_label="Купівлі")

    sell_renderer = p.vbar(x=dodge('dealer__username', 0.0, range=p.x_range),
            top='sell_transactions', width=0.2,
            source=source, color='#10b981', legend_label="Продажі")

    modify_renderer = p.vbar(x=dodge('dealer__username', 0.25, range=p.x_range),
            top='modify_transactions', width=0.2,
            source=source, color='#f59e0b', legend_label="Модифікації")

    p.yaxis.axis_label = "Кількість операцій"
    p.xaxis.axis_label = "Дилер"

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
    p.add_tools(hover_buy, hover_sell, hover_modify)

    return components(p)


@login_required
def bokeh_dashboard(request):
    """
    Bokeh Dashboard

    Графіки:
    1. Bar chart - продажі по співробітниках
    2. Pie chart - розподіл прибутку по марках
    3. Line chart - динаміка транзакцій дилерів
    4. Scatter plot - витрати топ клієнтів
    5. Multi-bar chart - статистика цін по рокам
    6. Grouped bar chart - баланси дилерів
    """
    # Отримуємо параметри фільтрації з GET запиту
    filters = {
        'min_sales': int(request.GET.get('min_sales', 1)),
        'min_cars': int(request.GET.get('min_cars', 1)),
        'min_amount': float(request.GET.get('min_amount', 0)),
        'top_customers': int(request.GET.get('top_customers', 10)),
        'min_cars_year': int(request.GET.get('min_cars_year', 1)),
        'min_transactions': int(request.GET.get('min_transactions', 1)),
    }

    chart1_script, chart1_div = create_sales_by_employee_chart(request, filters['min_sales'])
    chart2_script, chart2_div = create_profit_by_brand_chart(request, filters['min_cars'])
    chart3_script, chart3_div = create_transaction_dynamics_chart(request, filters['min_amount'])
    chart4_script, chart4_div = create_top_customers_chart(request, filters['top_customers'])
    chart5_script, chart5_div = create_car_price_statistics_chart(request, filters['min_cars_year'])
    chart6_script, chart6_div = create_dealer_balance_chart(request, filters['min_transactions'])

    # Формуємо контекст для template
    context = {
        'filters': filters,
        'chart1_script': chart1_script,
        'chart1_div': chart1_div,
        'chart2_script': chart2_script,
        'chart2_div': chart2_div,
        'chart3_script': chart3_script,
        'chart3_div': chart3_div,
        'chart4_script': chart4_script,
        'chart4_div': chart4_div,
        'chart5_script': chart5_script,
        'chart5_div': chart5_div,
        'chart6_script': chart6_script,
        'chart6_div': chart6_div,
    }

    return render(request, 'repo_practice/bokeh_dashboard.html', context)

