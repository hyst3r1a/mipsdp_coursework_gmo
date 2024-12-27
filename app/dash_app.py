from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy.sql import text
from app.database import db

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Waste Management Dashboard"),

    # Metrics Overview
    html.Div([
        html.Div(id='total-waste-year', style={'fontSize': '24px', 'padding': '10px'}),
        html.Div(id='total-waste-cost-month', style={'fontSize': '24px', 'padding': '10px'}),
        html.Div(id='average-daily-waste', style={'fontSize': '24px'}),
        html.Div(id='total-waste-all-time', style={'fontSize': '24px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    # Line Chart for Monthly Trends
    dcc.Graph(id='monthly-trend'),
    # Bar Chart for Top Products
    dcc.Graph(id='top-products'),
    # Pie Chart for Waste by Reason
    dcc.Graph(id='waste-by-reason'),
    # Additional visualizations
    dcc.Graph(id='top-reasons'),
    dcc.Graph(id='top-products-least-waste'),
    dcc.Graph(id='waste-trends-six-months'),
    dcc.Graph(id='top-products-by-cost'),
    dcc.Graph(id='waste-by-category'),
    dcc.Graph(id='daily-waste-trend-month'),
    dcc.Graph(id='monthly-average-waste-cost'),
    dcc.Graph(id='most-frequent-reason'),
    dcc.Graph(id='top-products-by-cost-all-time'),
    dcc.Graph(id='waste-by-reason-table'),
    dcc.Graph(id='yearly-waste-quantity'),
    dcc.Graph(id='top-reasons-last-3-months'),
])


def fetch_data(query):
    result = db.session.execute(text(query))
    return pd.DataFrame(result.fetchall(), columns=result.keys())


@app.callback(
    Output('total-waste-year', 'children'),
    Input('monthly-trend', 'id')  # Example input for triggering update
)
def update_total_waste_year(_):
    query = """
    SELECT SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now');
    """
    result = fetch_data(query)
    total_quantity = result['total_quantity'][0] if not result.empty else 0
    return f"Total Waste This Year: {total_quantity} kg"


@app.callback(
    Output('monthly-trend', 'figure'),
    Input('monthly-trend', 'id')
)
def update_monthly_trend(_):
    query = """
    SELECT td.month || '-' || td.year AS period, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    GROUP BY td.year, td.month
    ORDER BY td.year, td.month;
    """
    data = fetch_data(query)
    fig = px.line(data, x='period', y='total_quantity', title="Monthly Waste Trend")
    return fig


@app.callback(
    Output('top-products', 'figure'),
    Input('top-products', 'id')
)
def update_top_products(_):
    query = """
    SELECT product_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN product_dimension pd ON wf.product_id = pd.product_id
    GROUP BY product_name
    ORDER BY total_quantity DESC
    LIMIT 5;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='product_name', y='total_quantity', title="Top Products by Waste")
    return fig


@app.callback(
    Output('waste-by-reason', 'figure'),
    Input('waste-by-reason', 'id')
)
def update_waste_by_reason(_):
    query = """
    SELECT reason_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN reason_dimension rd ON wf.reason_id = rd.reason_id
    GROUP BY reason_name
    ORDER BY total_quantity DESC;
    """
    data = fetch_data(query)
    fig = px.pie(data, names='reason_name', values='total_quantity', title="Waste by Reason")
    return fig


@app.callback(
    Output('top-reasons', 'figure'),
    Input('top-reasons', 'id')
)
def update_top_reasons(_):
    query = """
    SELECT reason_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN reason_dimension rd ON wf.reason_id = rd.reason_id
    GROUP BY reason_name
    ORDER BY total_quantity DESC
    LIMIT 3;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='reason_name', y='total_quantity', title="Top 3 Reasons for Waste")
    return fig


@app.callback(
    Output('yearly-waste-distribution', 'figure'),
    Input('yearly-waste-distribution', 'id')
)
def update_yearly_waste_distribution(_):
    query = """
    SELECT td.week || '-' || td.year AS period, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now')
    GROUP BY td.year, td.week
    ORDER BY total_quantity DESC
    LIMIT 1;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='period', y='total_quantity', title="Weekly Waste Distribution")
    return fig

@app.callback(
    Output('average-daily-waste', 'children'),
    Input('average-daily-waste', 'id')
)
def update_average_daily_waste(_):
    query = """
    SELECT AVG(quantity) AS avg_daily_waste
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.month = strftime('%m', 'now') AND td.year = strftime('%Y', 'now');
    """
    result = fetch_data(query)
    avg_daily_waste = result['avg_daily_waste'][0] if not result.empty else 0
    return f"Average Daily Waste: {avg_daily_waste:.2f} kg"

@app.callback(
    Output('top-products-least-waste', 'figure'),
    Input('top-products-least-waste', 'id')
)
def update_top_products_least_waste(_):
    query = """
    SELECT product_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN product_dimension pd ON wf.product_id = pd.product_id
    GROUP BY product_name
    ORDER BY total_quantity ASC
    LIMIT 10;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='product_name', y='total_quantity', title="Top 10 Products with Least Waste")
    return fig

@app.callback(
    Output('waste-trends-six-months', 'figure'),
    Input('waste-trends-six-months', 'id')
)
def update_waste_trends_six_months(_):
    query = """
    SELECT td.month || '-' || td.year AS period, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now') OR td.year = strftime('%Y', 'now') - 1
    GROUP BY td.year, td.month
    ORDER BY td.year DESC, td.month DESC
    LIMIT 6;
    """
    data = fetch_data(query)
    fig = px.line(data, x='period', y='total_quantity', title="Waste Trends (Last 6 Months)")
    return fig

@app.callback(
    Output('top-products-by-cost', 'figure'),
    Input('top-products-by-cost', 'id')
)
def update_top_products_by_cost(_):
    query = """
    SELECT product_name, SUM(cost) AS total_cost
    FROM waste_facts wf
    JOIN product_dimension pd ON wf.product_id = pd.product_id
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now')
    GROUP BY product_name
    ORDER BY total_cost DESC
    LIMIT 5;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='product_name', y='total_cost', title="Top 5 Products by Cost (This Year)")
    return fig


@app.callback(
    Output('waste-by-category', 'figure'),
    Input('waste-by-category', 'id')
)
def update_waste_by_category(_):
    query = """
    SELECT category, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN product_dimension pd ON wf.product_id = pd.product_id
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now')
    GROUP BY category
    ORDER BY total_quantity DESC;
    """
    data = fetch_data(query)
    fig = px.pie(data, names='category', values='total_quantity', title="Waste by Product Category (This Year)")
    return fig


@app.callback(
    Output('total-waste-cost-month', 'children'),
    Input('total-waste-cost-month', 'id')
)
def update_total_waste_cost_month(_):
    query = """
    SELECT SUM(cost) AS total_cost
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.month = strftime('%m', 'now') AND td.year = strftime('%Y', 'now');
    """
    result = fetch_data(query)
    total_cost = result['total_cost'][0] if not result.empty else 0
    return f"Total Waste Cost (This Month): ${total_cost:.2f}"

@app.callback(
    Output('daily-waste-trend-month', 'figure'),
    Input('daily-waste-trend-month', 'id')
)
def update_daily_waste_trend_month(_):
    query = """
    SELECT td.day || '-' || td.month || '-' || td.year AS date, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.month = strftime('%m', 'now') AND td.year = strftime('%Y', 'now')
    GROUP BY td.year, td.month, td.day
    ORDER BY td.year, td.month, td.day;
    """
    data = fetch_data(query)
    fig = px.line(data, x='date', y='total_quantity', title="Daily Waste Trend (This Month)")
    return fig

@app.callback(
    Output('monthly-average-waste-cost', 'figure'),
    Input('monthly-average-waste-cost', 'id')
)
def update_monthly_average_waste_cost(_):
    query = """
    SELECT td.month || '-' || td.year AS period, AVG(cost) AS avg_cost
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    GROUP BY td.year, td.month
    ORDER BY td.year, td.month;
    """
    data = fetch_data(query)
    fig = px.line(data, x='period', y='avg_cost', title="Monthly Average Waste Cost")
    return fig


@app.callback(
    Output('most-frequent-reason', 'figure'),
    Input('most-frequent-reason', 'id')
)
def update_most_frequent_reason(_):
    query = """
    SELECT reason_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN reason_dimension rd ON wf.reason_id = rd.reason_id
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.month = strftime('%m', 'now') AND td.year = strftime('%Y', 'now')
    GROUP BY reason_name
    ORDER BY total_quantity DESC
    LIMIT 1;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='reason_name', y='total_quantity', title="Most Frequent Reason for Waste (This Month)")
    return fig


@app.callback(
    Output('top-products-by-cost-all-time', 'figure'),
    Input('top-products-by-cost-all-time', 'id')
)
def update_top_products_by_cost_all_time(_):
    query = """
    SELECT product_name, SUM(cost) AS total_cost
    FROM waste_facts wf
    JOIN product_dimension pd ON wf.product_id = pd.product_id
    GROUP BY product_name
    ORDER BY total_cost DESC
    LIMIT 3;
    """
    data = fetch_data(query)
    fig = px.pie(data, names='product_name', values='total_cost', title="Top 3 Products by Cost (All Time)")
    return fig


@app.callback(
    Output('waste-by-reason-table', 'children'),
    Input('waste-by-reason-table', 'id')
)
def update_waste_by_reason_table(_):
    query = """
    SELECT reason_name, SUM(quantity) AS total_quantity, SUM(cost) AS total_cost
    FROM waste_facts wf
    JOIN reason_dimension rd ON wf.reason_id = rd.reason_id
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now')
    GROUP BY reason_name
    ORDER BY total_quantity DESC;
    """
    data = fetch_data(query)
    return html.Table(
        [html.Tr([html.Th(col) for col in data.columns])] +
        [html.Tr([html.Td(data.iloc[i][col]) for col in data.columns]) for i in range(len(data))]
    )


@app.callback(
    Output('yearly-waste-quantity', 'figure'),
    Input('yearly-waste-quantity', 'id')
)
def update_yearly_waste_quantity(_):
    query = """
    SELECT td.year, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN time_dimension td ON wf.time_id = td.time_id
    GROUP BY td.year
    ORDER BY td.year;
    """
    data = fetch_data(query)
    fig = px.line(data, x='year', y='total_quantity', title="Yearly Waste Quantity Over Time")
    return fig


@app.callback(
    Output('top-reasons-last-3-months', 'figure'),
    Input('top-reasons-last-3-months', 'id')
)
def update_top_reasons_last_3_months(_):
    query = """
    SELECT reason_name, SUM(quantity) AS total_quantity
    FROM waste_facts wf
    JOIN reason_dimension rd ON wf.reason_id = rd.reason_id
    JOIN time_dimension td ON wf.time_id = td.time_id
    WHERE td.year = strftime('%Y', 'now') OR td.year = strftime('%Y', 'now') - 1
    AND td.month >= strftime('%m', 'now') - 2
    GROUP BY reason_name
    ORDER BY total_quantity DESC
    LIMIT 3;
    """
    data = fetch_data(query)
    fig = px.bar(data, x='reason_name', y='total_quantity', title="Top Reasons for Waste (Last 3 Months)")
    return fig


@app.callback(
    Output('total-waste-all-time', 'children'),
    Input('total-waste-all-time', 'id')
)
def update_total_waste_all_time(_):
    query = """
    SELECT SUM(quantity) AS total_quantity, SUM(cost) AS total_cost
    FROM waste_facts;
    """
    result = fetch_data(query)
    total_quantity = result['total_quantity'][0] if not result.empty else 0
    total_cost = result['total_cost'][0] if not result.empty else 0
    return f"Total Waste: {total_quantity} kg, Total Cost: ${total_cost:.2f}"
