import random
import string
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
import platform
import json
import os

class FingerprintManager:
    def __init__(self):
        self.user_agents = [
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0 Safari/537.36",
            "KEPLER COMMUNITY/1.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
        ]
        
        self.screen_resolutions = [
            (1920, 1080),
            (1366, 768),
            (1536, 864),
            (1440, 900),
            (1280, 720),
            (1600, 900),
            (1280, 1024),
            (1400, 1050),
            (1680, 1050),
            (1920, 1200),
            (1024, 768),
            (1280, 800),
            (1440, 900),
            (1680, 1050)
        ]
        
        self.languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "en-CA,en;q=0.9",
            "en-AU,en;q=0.9",
            "en-NZ,en;q=0.9",
            "en-ZA,en;q=0.9",
            "en-IN,en;q=0.9",
            "en-IE,en;q=0.9",
            "en-SG,en;q=0.9",
            "en-HK,en;q=0.9",
            "en-MY,en;q=0.9",
            "en-PH,en;q=0.9",
            "en-TH,en;q=0.9",
            "en-VN,en;q=0.9",
            "en-ID,en;q=0.9",
            "en-PK,en;q=0.9",
            "en-EG,en;q=0.9",
            "en-SA,en;q=0.9",
            "en-AE,en;q=0.9"
        ]
        
        self.platforms = [
            "Win32", "Win64", "MacIntel", "Linux x86_64"
        ]
        
        # Load or create canvas noise
        self.canvas_noise = self.load_or_create_canvas_noise()

    def load_or_create_canvas_noise(self):
        noise_file = "canvas_noise.json"
        if os.path.exists(noise_file):
            with open(noise_file, 'r') as f:
                return json.load(f)
        else:
            # Generate random noise pattern
            noise = {
                'offset': random.uniform(0, 1),
                'multiplier': random.uniform(0.9, 1.1)
            }
            with open(noise_file, 'w') as f:
                json.dump(noise, f)
            return noise

    def get_random_fingerprint(self):
        return {
            'user_agent': random.choice(self.user_agents),
            'platform': random.choice(self.platforms),
            'language': random.choice(self.languages),
            'resolution': random.choice(self.screen_resolutions),
            'canvas_noise': self.canvas_noise
        }

    def apply_fingerprint(self, profile: QWebEngineProfile, settings: QWebEngineSettings):
        fingerprint = self.get_random_fingerprint()
        
        # Set user agent
        profile.setHttpUserAgent(fingerprint['user_agent'])
        profile.setHttpAcceptLanguage(fingerprint['language'])
        
        # Inject JavaScript to override fingerprinting APIs
        js_code = f"""
        // Override platform
        Object.defineProperty(navigator, 'platform', {{
            get: function() {{ return '{fingerprint['platform']}'; }}
        }});
        
        // Override screen resolution
        Object.defineProperty(screen, 'width', {{
            get: function() {{ return {fingerprint['resolution'][0]}; }}
        }});
        Object.defineProperty(screen, 'height', {{
            get: function() {{ return {fingerprint['resolution'][1]}; }}
        }});
        
        // Add noise to canvas fingerprinting
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function() {{
            const context = originalGetContext.apply(this, arguments);
            if (context && arguments[0] === '2d') {{
                const originalFillRect = context.fillRect;
                context.fillRect = function() {{
                    const offset = {fingerprint['canvas_noise']['offset']};
                    const multiplier = {fingerprint['canvas_noise']['multiplier']};
                    arguments[0] += offset;
                    arguments[1] += offset;
                    arguments[2] *= multiplier;
                    arguments[3] *= multiplier;
                    return originalFillRect.apply(this, arguments);
                }};
            }}
            return context;
        }};
        
        // Override WebGL fingerprinting
        const getParameterProxyHandler = {{
            apply: function(target, thisArg, argumentsList) {{
                const param = argumentsList[0];
                if (param === thisArg.VENDOR || param === thisArg.RENDERER) {{
                    return 'KEPLER COMMUNITY Browser';
                }}
                return target.apply(thisArg, argumentsList);
            }}
        }};
        
        if (WebGLRenderingContext.prototype) {{
            WebGLRenderingContext.prototype.getParameter = new Proxy(
                WebGLRenderingContext.prototype.getParameter,
                getParameterProxyHandler
            );
        }}
        """
        
        # Add the script to be injected on page load
        return js_code

    def randomize_headers(self, request):
        """Add random headers to requests to further prevent fingerprinting"""
        headers = request.header()
        headers.add("Accept", "*/*")
        headers.add("DNT", "1")  # Do Not Track
        headers.add("Upgrade-Insecure-Requests", "1")
        headers.add("Sec-Fetch-Dest", random.choice(["document", "empty", "image"]))
        headers.add("Sec-Fetch-Mode", random.choice(["navigate", "cors", "no-cors"]))
        headers.add("Sec-Fetch-Site", random.choice(["none", "same-origin", "cross-site"]))
        return headers 