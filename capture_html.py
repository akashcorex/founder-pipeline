#!/usr/bin/env python3
"""
Capture an HTML file to a PNG screenshot using Puppeteer.

Usage:
  python3 capture_html.py --input page.html --output out.png
  python3 capture_html.py --input page.html --output out.png --width 1080 --height 1080

Requires Node.js and Puppeteer (available from carousel-routine/node_modules).
"""

import argparse
import subprocess
import sys
import tempfile
import os


def main():
    parser = argparse.ArgumentParser(description="Capture HTML to PNG via Puppeteer")
    parser.add_argument("--input", required=True, help="Path to HTML file")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--width", type=int, default=1080, help="Viewport width (default: 1080)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    args = parser.parse_args()

    input_abs = os.path.abspath(args.input)
    output_abs = os.path.abspath(args.output)

    if not os.path.exists(input_abs):
        print(f"Error: input file not found: {input_abs}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_abs) or ".", exist_ok=True)

    project_root = os.path.dirname(os.path.abspath(__file__))
    carousel_dir = os.path.join(project_root, "carousel-routine")
    node_modules = os.path.join(carousel_dir, "node_modules")

    if not os.path.isdir(node_modules):
        print("Error: carousel-routine/node_modules not found. Run: cd carousel-routine && npm install")
        sys.exit(1)

    puppeteer_bin = os.path.join(node_modules, ".bin", "puppeteer")
    node_path = os.path.join(node_modules, ".bin")
    env = os.environ.copy()
    env["PATH"] = node_path + os.pathsep + env.get("PATH", "")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        js_path = f.name
        f.write(f"""
const puppeteer = require('{os.path.join(node_modules, "puppeteer")}');
const http = require('http');
const fs = require('fs');

(async () => {{
  const browser = await puppeteer.launch({{
    headless: 'shell',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  }});
  const page = await browser.newPage();
  await page.setViewport({{ width: {args.width}, height: {args.height} }});

  const server = http.createServer((req, res) => {{
    res.writeHead(200, {{'Content-Type': 'text/html'}});
    res.end(fs.readFileSync({json.dumps(input_abs)}));
  }});
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;

  await page.goto('http://localhost:' + port, {{ waitUntil: 'networkidle0', timeout: 30000 }});
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => new Promise(r => setTimeout(r, 500)));

  await page.screenshot({{
    path: {json.dumps(output_abs)},
    clip: {{ x: 0, y: 0, width: {args.width}, height: {args.height} }},
    omitBackground: false
  }});

  console.log('Screenshot saved: ' + {json.dumps(output_abs)});

  server.close();
  await browser.close();
}})();
""")

    try:
        result = subprocess.run(
            ["node", js_path],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=project_root,
        )
        if result.returncode != 0:
            print("Puppeteer error:", result.stderr)
            sys.exit(1)
        print(result.stdout.strip())
    finally:
        os.unlink(js_path)


if __name__ == "__main__":
    main()
