from flask import Flask, render_template_string
import os

app = Flask(__name__)

# Simple test template
test_template = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <h1>Test Template</h1>
    <p>Step: {{ step }}</p>
    <p>Debug: Template is working!</p>
</body>
</html>
"""

@app.route('/test')
def test():
    return render_template_string(test_template, step='test')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True) 