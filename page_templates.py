from PySide6.QtWebEngineWidgets import QWebEngineView

class PageTemplates:
    @staticmethod
    def get_homepage():
        """Return the HTML content for the homepage."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>KEPLER COMMUNITY Browser</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, rgba(36, 9, 112, 0.85) 0%, rgba(26, 7, 72, 0.85) 100%),
                              url('Welcome-To-KEPLER-COMMUNITY.png') no-repeat center center fixed;
                    background-size: cover;
                    color: white;
                    margin: 0;
                    padding: 20px;
                    height: 100vh;
                    box-sizing: border-box;
                    overflow: hidden;
                }
                .overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: radial-gradient(circle at center, transparent 0%, rgba(36, 9, 112, 0.3) 100%);
                    z-index: 1;
                    pointer-events: none;
                }
                .container {
                    position: relative;
                    z-index: 2;
                    max-width: 1200px;
                    margin: 0 auto;
                    text-align: center;
                    animation: fadeIn 1s ease-out;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .logo {
                    font-size: 48px;
                    font-weight: bold;
                    color: #a8a8ff;
                    margin: 40px 0;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                    animation: glow 2s ease-in-out infinite alternate;
                }
                @keyframes glow {
                    from { text-shadow: 0 0 10px rgba(168, 168, 255, 0.3); }
                    to { text-shadow: 0 0 20px rgba(168, 168, 255, 0.6); }
                }
                .search-box {
                    background-color: rgba(26, 7, 72, 0.8);
                    border-radius: 25px;
                    padding: 20px;
                    margin: 20px auto;
                    max-width: 600px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    transform: translateY(0);
                    transition: all 0.3s ease;
                }
                .search-box:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
                }
                .quick-links {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 20px;
                    margin: 40px auto;
                    max-width: 800px;
                }
                .link-card {
                    background-color: rgba(26, 7, 72, 0.8);
                    border-radius: 10px;
                    padding: 15px;
                    transition: all 0.3s ease;
                    cursor: pointer;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                }
                .link-card:hover {
                    transform: translateY(-5px) scale(1.02);
                    background-color: rgba(38, 31, 160, 0.8);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                    border-color: rgba(255, 255, 255, 0.2);
                }
                .link-card img {
                    width: 32px;
                    height: 32px;
                    margin-bottom: 10px;
                    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
                    transition: transform 0.3s ease;
                }
                .link-card:hover img {
                    transform: scale(1.1);
                }
                .link-card h3 {
                    margin: 0;
                    color: #a8a8ff;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
                }
                .welcome-text {
                    font-size: 24px;
                    color: #a8a8ff;
                    margin: 20px 0;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                    opacity: 0;
                    animation: slideIn 1s ease-out forwards;
                    animation-delay: 0.5s;
                }
                @keyframes slideIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .footer {
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    text-align: center;
                    padding: 10px;
                    background-color: rgba(26, 7, 72, 0.9);
                    color: #888;
                    backdrop-filter: blur(5px);
                    z-index: 2;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }
            </style>
        </head>
        <body>
            <div class="overlay"></div>
            <div class="container">
                <div class="logo">KEPLER COMMUNITY</div>
                <div class="welcome-text">Welcome to KEPLER COMMUNITY Browser</div>
                <div class="search-box">
                    <p>Type a URL or search term in the address bar above to get started</p>
                </div>
                <div class="quick-links">
                    <div class="link-card" onclick="window.location.href='https://www.google.com'">
                        <img src="https://www.google.com/favicon.ico" alt="Google">
                        <h3>Google</h3>
                    </div>
                    <div class="link-card" onclick="window.location.href='https://www.youtube.com'">
                        <img src="https://www.youtube.com/favicon.ico" alt="YouTube">
                        <h3>YouTube</h3>
                    </div>
                    <div class="link-card" onclick="window.location.href='https://www.github.com'">
                        <img src="https://github.com/favicon.ico" alt="GitHub">
                        <h3>GitHub</h3>
                    </div>
                    <div class="link-card" onclick="window.location.href='https://www.wikipedia.org'">
                        <img src="https://www.wikipedia.org/favicon.ico" alt="Wikipedia">
                        <h3>Wikipedia</h3>
                    </div>
                </div>
            </div>
            <div class="footer">
                KEPLER COMMUNITY Browser [ALPHA]
            </div>
        </body>
        </html>
        """

    @staticmethod
    def show_error_page(web_view: QWebEngineView, domain: str):
        """Display a custom error page when a connection fails."""
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Connection Error</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #240970;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    text-align: center;
                }}
                .container {{
                    padding: 20px;
                    border-radius: 10px;
                    background-color: rgba(26, 7, 72, 0.8);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    width: 90%;
                }}
                h1 {{
                    font-size: 72px;
                    margin: 0;
                    color: #ff6b6b;
                }}
                h2 {{
                    font-size: 24px;
                    margin: 20px 0;
                    color: #a8a8ff;
                }}
                p {{
                    font-size: 18px;
                    margin: 10px 0;
                    line-height: 1.5;
                }}
                .search-button {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 20px;
                    transition: background-color 0.3s;
                }}
                .search-button:hover {{
                    background-color: #45a049;
                }}
                .error-details {{
                    font-size: 16px;
                    color: #888;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <h2>Connection Failed</h2>
                <p>We couldn't establish a connection to:</p>
                <p><strong>{domain}</strong></p>
                <p>The website might be:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Temporarily unavailable</li>
                    <li>Moved to a new address</li>
                    <li>No longer existing</li>
                </ul>
                <p>Would you like to search for this instead?</p>
                <a href="https://www.google.com/search?q={domain}" class="search-button">
                    Search on Google
                </a>
                <div class="error-details">
                    Error Code: CONNECTION_FAILED<br>
                    Browser: KEPLER COMMUNITY
                </div>
            </div>
        </body>
        </html>
        """
        web_view.setHtml(error_html) 