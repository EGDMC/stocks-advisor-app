import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Create the layout
app.layout = dbc.Container([
    html.H1("Stock Advisor App"),
    html.P("This is a placeholder page. The full application functionality will be added soon."),
    dbc.Alert(
        "The application is being configured. Please check back later.",
        color="info"
    )
], className="p-5")

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)