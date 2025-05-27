
import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Load Data
sales = pd.read_csv('sales_data.csv')
products = pd.read_csv('product_data.csv')
inventory = pd.read_csv('inventory_data.csv')

# Convert date column to datetime
sales['Date'] = pd.to_datetime(sales['Date'])

# Merge datasets
sales = sales.merge(products, on='Product_ID')
inventory = inventory.merge(products, on='Product_ID')

# Create Dashboard App with external stylesheets for better styling
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Define color palette
colors = {
    'primary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#17a2b8',
    'dark': '#2c3e50',
    'light': '#ecf0f1'
}

# Layout with dynamic components
app.layout = html.Div([
    # Interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds
        n_intervals=0
    ),
    
    # Header with real-time clock
    html.Div([
        html.Div([
            html.H1("🚀 Real-Time Sales & Operations Dashboard", 
                    style={
                        'textAlign': 'left',
                        'color': colors['dark'],
                        'margin': '0',
                        'fontFamily': 'Arial, sans-serif',
                        'fontSize': '2.2rem',
                        'fontWeight': 'bold'
                    }),
            html.P(id='live-clock', 
                   style={
                       'textAlign': 'left',
                       'color': colors['info'],
                       'margin': '5px 0 0 0',
                       'fontSize': '1rem'
                   })
        ], style={'flex': '1'}),
        
        html.Div([
            html.Button('🔄 Refresh Data', 
                       id='refresh-button',
                       n_clicks=0,
                       style={
                           'backgroundColor': colors['primary'],
                           'color': 'white',
                           'border': 'none',
                           'padding': '10px 20px',
                           'borderRadius': '5px',
                           'cursor': 'pointer',
                           'fontSize': '1rem',
                           'fontWeight': 'bold'
                       })
        ])
    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'backgroundColor': colors['light'], 
        'padding': '20px', 
        'borderRadius': '10px', 
        'marginBottom': '20px'
    }),
    
    # Interactive Controls Section
    html.Div([
        html.Div([
            html.Label("📅 Select Date Range:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=sales['Date'].min(),
                end_date=sales['Date'].max(),
                display_format='YYYY-MM-DD',
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'margin': '0 10px'}),
        
        html.Div([
            html.Label("🌍 Filter by Region:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': 'All Regions', 'value': 'all'}] + 
                        [{'label': region, 'value': region} for region in sales['Region'].unique()],
                value='all',
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'margin': '0 10px'}),
        
        html.Div([
            html.Label("📦 Filter by Category:", 
                      style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': 'All Categories', 'value': 'all'}] + 
                        [{'label': cat, 'value': cat} for cat in products['Category'].unique()],
                value='all',
                style={'width': '100%'}
            )
        ], style={'flex': '1', 'margin': '0 10px'})
    ], style={
        'display': 'flex',
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'marginBottom': '20px'
    }),
    
    # Dynamic KPI Cards
    html.Div(id='kpi-cards', style={'marginBottom': '30px'}),
    
    # Charts Section with tabs
    html.Div([
        dcc.Tabs(id="chart-tabs", value='sales-tab', children=[
            dcc.Tab(label='📊 Sales Analysis', value='sales-tab'),
            dcc.Tab(label='📈 Trends', value='trends-tab'),
            dcc.Tab(label='🎯 Product Performance', value='product-tab'),
        ], style={'marginBottom': '20px'}),
        
        html.Div(id='tab-content')
    ], style={
        'backgroundColor': 'white',
        'padding': '25px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'marginBottom': '20px'
    }),
    
    # Dynamic Inventory Section
    html.Div(id='inventory-section')
    
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f4f6f7',
    'padding': '20px',
    'minHeight': '100vh'
})

# Callback for live clock
@app.callback(
    Output('live-clock', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_clock(n):
    return f"🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Callback for dynamic KPI cards
@app.callback(
    Output('kpi-cards', 'children'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_kpi_cards(start_date, end_date, region, category, refresh_clicks, n_intervals):
    # Filter data based on selections
    filtered_sales = sales.copy()
    
    if start_date and end_date:
        filtered_sales = filtered_sales[
            (filtered_sales['Date'] >= start_date) & 
            (filtered_sales['Date'] <= end_date)
        ]
    
    if region != 'all':
        filtered_sales = filtered_sales[filtered_sales['Region'] == region]
    
    if category != 'all':
        filtered_sales = filtered_sales[filtered_sales['Category'] == category]
    
    # Calculate metrics
    total_sales = filtered_sales['Sales_Amount'].sum()
    total_units = filtered_sales['Units_Sold'].sum()
    avg_order_value = total_sales / len(filtered_sales) if len(filtered_sales) > 0 else 0
    
    # Calculate growth (simulated)
    growth_rate = np.random.uniform(-10, 15)  # Simulate dynamic growth
    
    return html.Div([
        html.Div([
            html.H3(f"${total_sales:,.0f}", style={'color': colors['success'], 'fontSize': '2rem', 'margin': '0'}),
            html.P("Total Sales", style={'color': '#7f8c8d', 'fontSize': '1.1rem', 'margin': '0'}),
            html.P(f"📈 {growth_rate:+.1f}% vs last period", 
                  style={'color': colors['success'] if growth_rate > 0 else colors['danger'], 
                         'fontSize': '0.9rem', 'margin': '5px 0 0 0'})
        ], className='kpi-card', style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'flex': '1',
            'transition': 'transform 0.3s ease',
            'cursor': 'pointer'
        }),
        
        html.Div([
            html.H3(f"{total_units:,}", style={'color': colors['primary'], 'fontSize': '2rem', 'margin': '0'}),
            html.P("Units Sold", style={'color': '#7f8c8d', 'fontSize': '1.1rem', 'margin': '0'}),
            html.P(f"📦 Avg: {total_units/len(filtered_sales):.1f} per order" if len(filtered_sales) > 0 else "📦 No data", 
                  style={'color': colors['info'], 'fontSize': '0.9rem', 'margin': '5px 0 0 0'})
        ], className='kpi-card', style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'flex': '1',
            'transition': 'transform 0.3s ease',
            'cursor': 'pointer'
        }),
        
        html.Div([
            html.H3(f"${avg_order_value:.0f}", style={'color': colors['warning'], 'fontSize': '2rem', 'margin': '0'}),
            html.P("Avg Order Value", style={'color': '#7f8c8d', 'fontSize': '1.1rem', 'margin': '0'}),
            html.P(f"💰 {len(filtered_sales)} total orders", 
                  style={'color': colors['info'], 'fontSize': '0.9rem', 'margin': '5px 0 0 0'})
        ], className='kpi-card', style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'textAlign': 'center',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'flex': '1',
            'transition': 'transform 0.3s ease',
            'cursor': 'pointer'
        })
    ], style={'display': 'flex'})

# Callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('chart-tabs', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('region-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_tab_content(active_tab, start_date, end_date, region, category):
    # Filter data
    filtered_sales = sales.copy()
    
    if start_date and end_date:
        filtered_sales = filtered_sales[
            (filtered_sales['Date'] >= start_date) & 
            (filtered_sales['Date'] <= end_date)
        ]
    
    if region != 'all':
        filtered_sales = filtered_sales[filtered_sales['Region'] == region]
    
    if category != 'all':
        filtered_sales = filtered_sales[filtered_sales['Category'] == category]
    
    if active_tab == 'sales-tab':
        # Interactive sales chart
        sales_by_region = filtered_sales.groupby("Region")["Sales_Amount"].sum().reset_index()
        fig = px.bar(
            sales_by_region, 
            x="Region", 
            y="Sales_Amount", 
            title="Interactive Sales Performance by Region",
            color="Sales_Amount",
            color_continuous_scale="viridis",
            template="plotly_white"
        )
        fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>')
        
        return dcc.Graph(figure=fig, style={'height': '400px'})
    
    elif active_tab == 'trends-tab':
        # Time series chart
        daily_sales = filtered_sales.groupby('Date')['Sales_Amount'].sum().reset_index()
        fig = px.line(
            daily_sales, 
            x='Date', 
            y='Sales_Amount',
            title="Sales Trend Over Time",
            template="plotly_white"
        )
        fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        fig.update_traces(line_color=colors['primary'], line_width=3)
        
        return dcc.Graph(figure=fig, style={'height': '400px'})
    
    elif active_tab == 'product-tab':
        # Product performance chart
        product_sales = filtered_sales.groupby(['Product_Name', 'Category']).agg({
            'Sales_Amount': 'sum',
            'Units_Sold': 'sum'
        }).reset_index()
        
        fig = px.scatter(
            product_sales, 
            x='Units_Sold', 
            y='Sales_Amount',
            color='Category',
            size='Sales_Amount',
            hover_name='Product_Name',
            title="Product Performance: Sales vs Units Sold",
            template="plotly_white"
        )
        fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        return dcc.Graph(figure=fig, style={'height': '400px'})

# Callback for inventory section
@app.callback(
    Output('inventory-section', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_inventory_section(n_intervals, refresh_clicks):
    # Simulate dynamic inventory changes
    dynamic_inventory = inventory.copy()
    
    # Add some randomness to simulate real-time changes
    np.random.seed(n_intervals + refresh_clicks)
    dynamic_inventory['Stock_Level'] = dynamic_inventory['Stock_Level'] + np.random.randint(-2, 3, len(dynamic_inventory))
    dynamic_inventory['Stock_Level'] = dynamic_inventory['Stock_Level'].clip(lower=0)
    
    low_stock = dynamic_inventory[dynamic_inventory["Stock_Level"] < dynamic_inventory["Reorder_Level"]]
    stock_percentage = ((len(dynamic_inventory) - len(low_stock)) / len(dynamic_inventory)) * 100
    
    # Create gauge chart
    gauge_fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = stock_percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Live Stock Health %"},
        delta = {'reference': 90},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': colors['primary']},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': colors['warning']},
                {'range': [80, 100], 'color': colors['success']}
            ],
            'threshold': {
                'line': {'color': colors['danger'], 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    gauge_fig.update_layout(
        height=300,
        font={'color': colors['dark'], 'family': "Arial"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return html.Div([
        html.Div([
            html.Div([
                html.H3("⚡ Real-Time Stock Monitor", 
                       style={'color': colors['dark'], 'marginBottom': '20px', 'fontSize': '1.5rem'}),
                dcc.Graph(figure=gauge_fig)
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
                'margin': '10px'
            })
        ], style={'flex': '1'}),
        
        html.Div([
            html.H3("⚠️ Live Low Stock Alerts", 
                   style={'color': colors['danger'], 'marginBottom': '20px', 'fontSize': '1.5rem'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th(col, style={
                                'backgroundColor': colors['dark'],
                                'color': 'white',
                                'padding': '12px',
                                'textAlign': 'left',
                                'fontWeight': 'bold'
                            }) for col in ['Product', 'Current Stock', 'Reorder Level', 'Status']
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['Product_Name'], style={'padding': '12px', 'borderBottom': '1px solid #ecf0f1'}),
                            html.Td(row['Stock_Level'], style={'padding': '12px', 'borderBottom': '1px solid #ecf0f1', 'fontWeight': 'bold'}),
                            html.Td(row['Reorder_Level'], style={'padding': '12px', 'borderBottom': '1px solid #ecf0f1'}),
                            html.Td(
                                "🔴 CRITICAL" if row['Stock_Level'] <= row['Reorder_Level']/2 else "🟡 LOW",
                                style={
                                    'padding': '12px', 
                                    'borderBottom': '1px solid #ecf0f1',
                                    'color': colors['danger'] if row['Stock_Level'] <= row['Reorder_Level']/2 else colors['warning'],
                                    'fontWeight': 'bold'
                                }
                            )
                        ]) for _, row in low_stock.iterrows()
                    ])
                ], style={
                    'width': '100%',
                    'borderCollapse': 'collapse',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'borderRadius': '8px',
                    'overflow': 'hidden'
                }) if len(low_stock) > 0 else html.P("✅ All products are well stocked!", 
                                                   style={'color': colors['success'], 'fontSize': '1.2rem', 'textAlign': 'center'})
            ])
        ], style={
            'backgroundColor': 'white',
            'padding': '25px',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'margin': '10px',
            'flex': '2'
        })
    ], style={'display': 'flex', 'marginBottom': '30px'})

# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
