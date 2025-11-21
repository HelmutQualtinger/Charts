import pandas as pd
import plotly.graph_objects as go
from smic import smi_total_return_monatlich

# Convert dictionary to pandas DataFrame
dates = pd.to_datetime(list(smi_total_return_monatlich.keys()))
values = list(smi_total_return_monatlich.values())

df = pd.DataFrame({
    'Date': dates,
    'SMI': values
}).sort_values('Date')

# Create Plotly figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['Date'],
    y=df['SMI'],
    mode='lines',
    name='SMI Total Return',
    line=dict(color='rgb(255, 99, 132)', width=2),
    hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>SMI:</b> %{y:,.2f}<extra></extra>'
))

fig.update_layout(
    title='SMI Total Return Index (Monthly)',
    xaxis_title='Date',
    yaxis_title='Index Value',
    template='plotly_dark',
    hovermode='x unified',
    height=600,
    margin=dict(l=60, r=60, t=80, b=60)
)

# Show the plot
fig.show()