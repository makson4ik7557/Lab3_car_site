from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import json
import logging

logger = logging.getLogger(__name__)


def call_analytics_api(request, endpoint, params=None):
    """
    Helper функція для виклику REST API analytics endpoints
    """
    from repo_practice.views import AnalyticsViewSet
    from rest_framework.test import APIRequestFactory
    from django.http import QueryDict

    if not request.user.is_authenticated:
        return []

    try:
        # Створюємо mock API request з параметрами
        factory = APIRequestFactory()
        query_string = '&'.join([f'{k}={v}' for k, v in (params or {}).items()])
        api_request = factory.get(f'/api/analytics/{endpoint}/?{query_string}')
        api_request.user = request.user
        api_request.query_params = QueryDict(query_string)

        # Викликаємо відповідний метод ViewSet
        viewset = AnalyticsViewSet()
        viewset.request = api_request
        viewset.format_kwarg = None

        # Маппінг
        method_map = {
            'sales-by-employee': viewset.sales_by_employee,
            'profit-by-brand': viewset.profit_by_brand,
            'transaction-dynamics': viewset.transaction_dynamics,
            'top-customers': viewset.top_customers,
            'car-price-statistics': viewset.car_price_statistics,
            'dealer-balance-summary': viewset.dealer_balance_summary,
        }

        method = method_map.get(endpoint)
        if not method:
            logger.error(f"Unknown endpoint: {endpoint}")
            return []

        # Викликаємо API ViewSet method
        response = method(api_request)

        # Отримуємо дані з Response
        if hasattr(response, 'data'):
            data = response.data
            logger.info(f"API ViewSet call to {endpoint}: {data.get('records_count', 0)} records")
            return data.get('data', [])
        else:
            logger.error(f"Invalid response from {endpoint}")
            return []

    except Exception as e:
        logger.error(f"API ViewSet call failed for {endpoint}: {str(e)}, using fallback")
        return call_analytics_internal(endpoint, params)


def call_analytics_internal(endpoint, params=None):
    """
    Внутрішній виклик Repository як fallback коли HTTP API не працює
    Це забезпечує що dashboard завжди працює
    """
    from repo_practice.services.repo_service import RepositoryService
    from decimal import Decimal

    repo = RepositoryService()
    params = params or {}

    try:
        if endpoint == 'sales-by-employee':
            data = repo.analytics.get_sales_by_employee(params.get('min_sales', 1))
        elif endpoint == 'profit-by-brand':
            data = repo.analytics.get_profit_by_car_brand(params.get('min_cars', 1))
        elif endpoint == 'transaction-dynamics':
            data = repo.analytics.get_transaction_dynamics_by_dealer(params.get('min_amount', 0))
        elif endpoint == 'top-customers':
            data = repo.analytics.get_top_customers_by_spending(params.get('limit', 10))
        elif endpoint == 'car-price-statistics':
            data = repo.analytics.get_car_price_statistics_by_year(params.get('min_cars', 1))
        elif endpoint == 'dealer-balance-summary':
            data = repo.analytics.get_dealer_balance_summary(params.get('min_transactions', 1))
        else:
            return []

        # Конвертуємо Decimal в float
        for record in data:
            for key, value in record.items():
                if isinstance(value, Decimal):
                    record[key] = float(value)

        return data
    except Exception as e:
        logger.error(f"Internal call failed for {endpoint}: {str(e)}")
        return []


def create_sales_chart_plotly(request, min_sales):
    """Графік 1: Bar Chart - Продажі по співробітниках"""
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_sales = analytics.get_sales_by_employee_df(min_sales)

    if df_sales.empty:
        logger.warning(f"Plotly графік 1: Немає даних для min_sales={min_sales}")
        return None

    logger.info(f"Plotly графік 1: Отримано {len(df_sales)} записів")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sales['full_name'].tolist(),
        y=df_sales['total_revenue'].tolist(),
        name='Загальний дохід',
        marker_color='rgb(55, 83, 109)',
        text=[f'${x:,.0f}' for x in df_sales['total_revenue']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Дохід: $%{y:,.2f}<br>Продажів: %{customdata}<extra></extra>',
        customdata=df_sales['total_sales'].tolist()
    ))

    fig.update_layout(
        title=f'Продажі по співробітниках (мін. {min_sales} продаж)',
        xaxis_title='Співробітник',
        yaxis_title='Загальний дохід ($)',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_brand_chart_plotly(request, min_cars):
    """Графік 2: Pie Chart - Розподіл прибутку по марках"""
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_brands = analytics.get_profit_by_brand_df(min_cars)

    if df_brands.empty:
        logger.warning(f"Plotly графік 2: Немає даних для min_cars={min_cars}")
        return None

    logger.info(f"Plotly графік 2: Отримано {len(df_brands)} записів")

    fig = go.Figure(data=[go.Pie(
        labels=df_brands['car__make'].tolist(),
        values=df_brands['total_revenue'].tolist(),
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set3),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Дохід: $%{value:,.2f}<br>Частка: %{percent}<br>Продано авто: %{customdata}<extra></extra>',
        customdata=df_brands['cars_sold'].tolist()
    )])

    fig.update_layout(
        title=f'Розподіл прибутку по марках автомобілів (мін. {min_cars} авто)',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_transaction_chart_plotly(request, min_amount):
    """Графік 3: Line Chart - Динаміка транзакцій дилерів"""
    transaction_data = call_analytics_api(request, 'transaction-dynamics', {'min_amount': min_amount})
    df_transactions = pd.DataFrame(transaction_data)

    if df_transactions.empty:
        return None

    fig = go.Figure()

    for trans_type in df_transactions['transaction_type'].unique():
        df_type = df_transactions[df_transactions['transaction_type'] == trans_type]

        fig.add_trace(go.Scatter(
            x=df_type['dealer__username'].tolist(),
            y=df_type['total_amount'].tolist(),
            mode='lines+markers',
            name=trans_type,
            line=dict(width=2),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Тип: ' + trans_type + '<br>Сума: $%{y:,.2f}<br>Кількість: %{customdata}<extra></extra>',
            customdata=df_type['transaction_count'].tolist()
        ))

    fig.update_layout(
        title=f'Динаміка транзакцій дилерів (мін. сума ${min_amount:,.0f})',
        xaxis_title='Дилер',
        yaxis_title='Загальна сума ($)',
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_customers_chart_plotly(request, limit):
    """Графік 4: Scatter Plot - Витрати топ клієнтів"""
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service (вже з full_name)
    df_customers = analytics.get_top_customers_df(limit)

    if df_customers.empty:
        return None


    fig = go.Figure(data=go.Scatter(
        x=df_customers['cars_purchased'].tolist(),
        y=df_customers['total_spent'].tolist(),
        mode='markers+text',
        marker=dict(
            size=(df_customers['total_spent'] / df_customers['total_spent'].max() * 50).tolist(),
            color=df_customers['total_spent'].tolist(),
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Витрачено ($)")
        ),
        text=df_customers['full_name'].tolist(),
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Куплено авто: %{x}<br>Витрачено: $%{y:,.2f}<br>Середня ціна: $%{customdata:,.2f}<extra></extra>',
        customdata=df_customers['average_purchase'].tolist()
    ))

    fig.update_layout(
        title=f'Топ-{limit} клієнтів по витратам',
        xaxis_title='Кількість куплених автомобілів',
        yaxis_title='Загальні витрати ($)',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_car_stats_chart_plotly(request, min_cars_year):
    """Графік 5: Histogram - Розподіл цін авто по рокам"""
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_car_stats = analytics.get_car_price_statistics_df(min_cars_year)

    if df_car_stats.empty:
        return None

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_car_stats['year'].tolist(),
        y=df_car_stats['average_price'].tolist(),
        name='Середня ціна',
        marker_color='rgb(158, 202, 225)',
        hovertemplate='<b>Рік: %{x}</b><br>Середня ціна: $%{y:,.2f}<br>Авто: %{customdata}<extra></extra>',
        customdata=df_car_stats['cars_count'].tolist()
    ))

    fig.add_trace(go.Scatter(
        x=df_car_stats['year'].tolist(),
        y=df_car_stats['max_price'].tolist(),
        mode='lines+markers',
        name='Максимальна ціна',
        line=dict(color='rgb(255, 99, 71)', width=2),
        marker=dict(size=6)
    ))

    fig.add_trace(go.Scatter(
        x=df_car_stats['year'].tolist(),
        y=df_car_stats['min_price'].tolist(),
        mode='lines+markers',
        name='Мінімальна ціна',
        line=dict(color='rgb(144, 238, 144)', width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=f'Статистика цін автомобілів по рокам (мін. {min_cars_year} авто)',
        xaxis_title='Рік виробництва',
        yaxis_title='Ціна ($)',
        template='plotly_white',
        height=400,
        barmode='overlay'
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def create_dealer_balance_chart_plotly(request, min_transactions):
    """Графік 6: Grouped Bar + Line - Баланси дилерів"""
    from .services import AnalyticsService
    analytics = AnalyticsService()

    # DataFrame напряму з Service
    df_dealer_balance = analytics.get_dealer_balance_summary_df(min_transactions)

    if df_dealer_balance.empty:
        return None

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_dealer_balance['dealer__username'].tolist(),
        y=df_dealer_balance['buy_transactions'].tolist(),
        name='Купівлі',
        marker_color='rgb(255, 127, 80)',
        hovertemplate='<b>%{x}</b><br>Купівель: %{y}<br>Сума: $%{customdata:,.2f}<extra></extra>',
        customdata=df_dealer_balance['total_buy_amount'].tolist()
    ))

    fig.add_trace(go.Bar(
        x=df_dealer_balance['dealer__username'].tolist(),
        y=df_dealer_balance['sell_transactions'].tolist(),
        name='Продажі',
        marker_color='rgb(144, 238, 144)',
        hovertemplate='<b>%{x}</b><br>Продажів: %{y}<br>Сума: $%{customdata:,.2f}<extra></extra>',
        customdata=df_dealer_balance['total_sell_amount'].tolist()
    ))

    fig.add_trace(go.Bar(
        x=df_dealer_balance['dealer__username'].tolist(),
        y=df_dealer_balance['modify_transactions'].tolist(),
        name='Модифікації',
        marker_color='rgb(135, 206, 250)',
        hovertemplate='<b>%{x}</b><br>Модифікацій: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df_dealer_balance['dealer__username'].tolist(),
        y=df_dealer_balance['current_balance'].tolist(),
        mode='lines+markers',
        name='Поточний баланс',
        line=dict(color='rgb(255, 215, 0)', width=3),
        marker=dict(size=10, symbol='diamond'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Баланс: $%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f'Операції та баланси дилерів (мін. {min_transactions} транзакцій)',
        xaxis_title='Дилер',
        yaxis_title='Кількість операцій',
        yaxis2=dict(
            title='Баланс ($)',
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        height=400,
        barmode='group',
        hovermode='x unified'
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@login_required
def plotly_dashboard(request):
    """
    Plotly Dashboard

    Графіки:
    1. Bar chart - продажі по співробітниках
    2. Pie chart - розподіл прибутку по марках авто
    3. Line chart - динаміка транзакцій дилерів
    4. Scatter plot - витрати топ клієнтів
    5. Histogram - розподіл цін авто по рокам
    6. Grouped Bar + Line - баланси дилерів по типах операцій
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

    chart1_json = create_sales_chart_plotly(request, filters['min_sales'])
    chart2_json = create_brand_chart_plotly(request, filters['min_cars'])
    chart3_json = create_transaction_chart_plotly(request, filters['min_amount'])
    chart4_json = create_customers_chart_plotly(request, filters['top_customers'])
    chart5_json = create_car_stats_chart_plotly(request, filters['min_cars_year'])
    chart6_json = create_dealer_balance_chart_plotly(request, filters['min_transactions'])

    # Формуємо контекст для template
    context = {
        'chart1_json': chart1_json,
        'chart2_json': chart2_json,
        'chart3_json': chart3_json,
        'chart4_json': chart4_json,
        'chart5_json': chart5_json,
        'chart6_json': chart6_json,
        'filters': filters
    }

    return render(request, 'repo_practice/plotly_dashboard.html', context)