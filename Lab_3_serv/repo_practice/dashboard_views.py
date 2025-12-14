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
    from .views import AnalyticsViewSet
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

        # Маппінг endpoint → ViewSet method
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
        # Fallback на випадок помилки
        return call_analytics_internal(endpoint, params)


def call_analytics_internal(endpoint, params=None):
    """
    Внутрішній виклик Repository як fallback коли HTTP API не працює
    Це забезпечує що dashboard завжди працює
    """
    from .services.repo_service import RepositoryService
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


@login_required
def plotly_dashboard(request):
    """
    Головний дашборд з 6 Plotly графіками

    1. Bar chart - продажі по співробітниках
    2. Pie chart - розподіл прибутку по марках авто
    3. Line chart - динаміка транзакцій дилерів
    4. Scatter plot - витрати топ клієнтів
    5. Histogram - розподіл цін авто по рокам
    6. Box plot - баланси дилерів по типах операцій
    """
    # Отримуємо параметри фільтрації з GET запиту
    min_sales = int(request.GET.get('min_sales', 1))
    min_cars = int(request.GET.get('min_cars', 1))
    min_amount = float(request.GET.get('min_amount', 0))
    top_customers_limit = int(request.GET.get('top_customers', 10))
    min_cars_year = int(request.GET.get('min_cars_year', 1))
    min_transactions = int(request.GET.get('min_transactions', 1))

    # === ГРАФІК 1: Bar Chart - Продажі по співробітниках ===
    sales_data = call_analytics_api(request, 'sales-by-employee', {'min_sales': min_sales})
    logger.info(f"Графік 1 - отримано {len(sales_data)} записів через API")

    df_sales = pd.DataFrame(sales_data)

    if not df_sales.empty:

        # Створюємо повне ім'я співробітника
        df_sales['full_name'] = df_sales['employee__first_name'] + ' ' + df_sales['employee__last_name']

        logger.info(f"Графік 1 - дані після обробки:\n{df_sales[['full_name', 'total_revenue']].to_string()}")

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_sales['full_name'].tolist(),  # Конвертуємо в list!
            y=df_sales['total_revenue'].tolist(),  # Конвертуємо в list!
            name='Загальний дохід',
            marker_color='rgb(55, 83, 109)',
            text=[f'${x:,.0f}' for x in df_sales['total_revenue']],  # Конвертуємо в list!
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Дохід: $%{y:,.2f}<br>Продажів: %{customdata}<extra></extra>',
            customdata=df_sales['total_sales'].tolist()  # Конвертуємо в list!
        ))

        fig1.update_layout(
            title=f'Продажі по співробітниках (мін. {min_sales} продаж)',
            xaxis_title='Співробітник',
            yaxis_title='Загальний дохід ($)',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        chart1_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 1 - немає даних")
        chart1_json = None

    # === ГРАФІК 2: Pie Chart - Розподіл прибутку по марках авто ===
    brand_data = call_analytics_api(request, 'profit-by-brand', {'min_cars': min_cars})
    logger.info(f"Графік 2 - отримано {len(brand_data)} записів через API")

    df_brands = pd.DataFrame(brand_data)

    if not df_brands.empty:

        logger.info(f"Графік 2 - дані:\n{df_brands[['car__make', 'total_revenue']].to_string()}")

        fig2 = go.Figure(data=[go.Pie(
            labels=df_brands['car__make'].tolist(),
            values=df_brands['total_revenue'].tolist(),
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Дохід: $%{value:,.2f}<br>Частка: %{percent}<br>Продано авто: %{customdata}<extra></extra>',
            customdata=df_brands['cars_sold'].tolist()
        )])

        fig2.update_layout(
            title=f'Розподіл прибутку по марках автомобілів (мін. {min_cars} авто)',
            template='plotly_white',
            height=400
        )
        chart2_json = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 2 - немає даних")
        chart2_json = None

    # === ГРАФІК 3: Line Chart - Динаміка транзакцій дилерів ===
    transaction_data = call_analytics_api(request, 'transaction-dynamics', {'min_amount': min_amount})
    logger.info(f"Графік 3 - отримано {len(transaction_data)} записів через API")

    df_transactions = pd.DataFrame(transaction_data)

    if not df_transactions.empty:

        logger.info(f"Графік 3 - дані:\n{df_transactions[['dealer__username', 'transaction_type', 'total_amount']].to_string()}")

        # Групуємо по типу транзакції для кращої візуалізації
        fig3 = go.Figure()

        for trans_type in df_transactions['transaction_type'].unique():
            df_type = df_transactions[df_transactions['transaction_type'] == trans_type]

            fig3.add_trace(go.Scatter(
                x=df_type['dealer__username'].tolist(),
                y=df_type['total_amount'].tolist(),
                mode='lines+markers',
                name=trans_type,
                line=dict(width=2),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Тип: ' + trans_type + '<br>Сума: $%{y:,.2f}<br>Кількість: %{customdata}<extra></extra>',
                customdata=df_type['transaction_count'].tolist()
            ))

        fig3.update_layout(
            title=f'Динаміка транзакцій дилерів (мін. сума ${min_amount:,.0f})',
            xaxis_title='Дилер',
            yaxis_title='Загальна сума ($)',
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        chart3_json = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 3 - немає даних")
        chart3_json = None

    # === ГРАФІК 4: Scatter Plot - Витрати топ клієнтів ===
    customers_data = call_analytics_api(request, 'top-customers', {'limit': top_customers_limit})
    logger.info(f"Графік 4 - отримано {len(customers_data)} записів через API")

    df_customers = pd.DataFrame(customers_data)

    if not df_customers.empty:

        df_customers['full_name'] = df_customers['customer__first_name'] + ' ' + df_customers['customer__last_name']

        logger.info(f"Графік 4 - дані:\n{df_customers[['full_name', 'total_spent']].to_string()}")

        fig4 = go.Figure(data=go.Scatter(
            x=df_customers['cars_purchased'].tolist(),
            y=df_customers['total_spent'].tolist(),
            mode='markers+text',
            marker=dict(
                size=(df_customers['total_spent'] / df_customers['total_spent'].max() * 50).tolist(),  # Конвертуємо в list!
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

        fig4.update_layout(
            title=f'Топ-{top_customers_limit} клієнтів по витратам',
            xaxis_title='Кількість куплених автомобілів',
            yaxis_title='Загальні витрати ($)',
            template='plotly_white',
            height=400
        )
        chart4_json = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 4 - немає даних")
        chart4_json = None

    # === ГРАФІК 5: Histogram - Розподіл цін авто по рокам ===
    car_stats_data = call_analytics_api(request, 'car-price-statistics', {'min_cars': min_cars_year})
    logger.info(f"Графік 5 - отримано {len(car_stats_data)} записів через API")

    df_car_stats = pd.DataFrame(car_stats_data)

    if not df_car_stats.empty:

        logger.info(f"Графік 5 - дані:\n{df_car_stats[['year', 'average_price', 'cars_count']].to_string()}")

        fig5 = go.Figure()

        # Додаємо три лінії: середня, макс, мін ціна
        fig5.add_trace(go.Bar(
            x=df_car_stats['year'].tolist(),
            y=df_car_stats['average_price'].tolist(),
            name='Середня ціна',
            marker_color='rgb(158, 202, 225)',
            hovertemplate='<b>Рік: %{x}</b><br>Середня ціна: $%{y:,.2f}<br>Авто: %{customdata}<extra></extra>',
            customdata=df_car_stats['cars_count'].tolist()
        ))

        fig5.add_trace(go.Scatter(
            x=df_car_stats['year'].tolist(),
            y=df_car_stats['max_price'].tolist(),
            mode='lines+markers',
            name='Максимальна ціна',
            line=dict(color='rgb(255, 99, 71)', width=2),
            marker=dict(size=6)
        ))

        fig5.add_trace(go.Scatter(
            x=df_car_stats['year'].tolist(),
            y=df_car_stats['min_price'].tolist(),
            mode='lines+markers',
            name='Мінімальна ціна',
            line=dict(color='rgb(144, 238, 144)', width=2),
            marker=dict(size=6)
        ))

        fig5.update_layout(
            title=f'Статистика цін автомобілів по рокам (мін. {min_cars_year} авто)',
            xaxis_title='Рік виробництва',
            yaxis_title='Ціна ($)',
            template='plotly_white',
            height=400,
            barmode='overlay'
        )
        chart5_json = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 5 - немає даних")
        chart5_json = None

    # === ГРАФІК 6: Box Plot - Баланси дилерів ===
    dealer_balance_data = call_analytics_api(request, 'dealer-balance-summary', {'min_transactions': min_transactions})
    logger.info(f"Графік 6 - отримано {len(dealer_balance_data)} записів через API")
    logger.info(f"Графік 6 - сирі дані: {dealer_balance_data}")


    df_dealer_balance = pd.DataFrame(dealer_balance_data)

    if not df_dealer_balance.empty:

        logger.info(f"Графік 6 - DataFrame після конвертації:\n{df_dealer_balance.to_string()}")

        fig6 = go.Figure()

        # Створюємо grouped bar chart для різних типів операцій
        fig6.add_trace(go.Bar(
            x=df_dealer_balance['dealer__username'].tolist(),
            y=df_dealer_balance['buy_transactions'].tolist(),
            name='Купівлі',
            marker_color='rgb(255, 127, 80)',
            hovertemplate='<b>%{x}</b><br>Купівель: %{y}<br>Сума: $%{customdata:,.2f}<extra></extra>',
            customdata=df_dealer_balance['total_buy_amount'].tolist()
        ))

        fig6.add_trace(go.Bar(
            x=df_dealer_balance['dealer__username'].tolist(),
            y=df_dealer_balance['sell_transactions'].tolist(),
            name='Продажі',
            marker_color='rgb(144, 238, 144)',
            hovertemplate='<b>%{x}</b><br>Продажів: %{y}<br>Сума: $%{customdata:,.2f}<extra></extra>',
            customdata=df_dealer_balance['total_sell_amount'].tolist()
        ))

        fig6.add_trace(go.Bar(
            x=df_dealer_balance['dealer__username'].tolist(),
            y=df_dealer_balance['modify_transactions'].tolist(),
            name='Модифікації',
            marker_color='rgb(135, 206, 250)',
            hovertemplate='<b>%{x}</b><br>Модифікацій: %{y}<extra></extra>'
        ))

        # Додаємо лінію балансу
        fig6.add_trace(go.Scatter(
            x=df_dealer_balance['dealer__username'].tolist(),
            y=df_dealer_balance['current_balance'].tolist(),
            mode='lines+markers',
            name='Поточний баланс',
            line=dict(color='rgb(255, 215, 0)', width=3),
            marker=dict(size=10, symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Баланс: $%{y:,.2f}<extra></extra>'
        ))

        fig6.update_layout(
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
        chart6_json = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        logger.warning("Графік 6 - немає даних")
        chart6_json = None

    context = {
        'chart1_json': chart1_json,
        'chart2_json': chart2_json,
        'chart3_json': chart3_json,
        'chart4_json': chart4_json,
        'chart5_json': chart5_json,
        'chart6_json': chart6_json,
        'filters': {
            'min_sales': min_sales,
            'min_cars': min_cars,
            'min_amount': min_amount,
            'top_customers': top_customers_limit,
            'min_cars_year': min_cars_year,
            'min_transactions': min_transactions
        }
    }

    return render(request, 'repo_practice/plotly_dashboard.html', context)


