
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import pdfkit

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def generate_report(data, output_format='pdf'):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report_template.html")

    rendered = template.render(
        date=datetime.now().strftime("%Y-%m-%d"),
        restarts=data.get("restarts", 0),
        avg_cpu=data.get("avg_cpu", 0.0),
        avg_ram=data.get("avg_ram", 0.0),
        alerts=data.get("alerts", [])
    )

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d')}.{output_format}")

    if output_format == "html":
        with open(output_path, "w") as f:
            f.write(rendered)
    elif output_format == "pdf":
        pdfkit.from_string(rendered, output_path)

    return output_path
