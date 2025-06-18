
from report_generator import generate_report
from monitor import collect_data  # Supposons que monitor.py possède cette fonction

if __name__ == "__main__":
    data = collect_data()
    path = generate_report(data, output_format='pdf')
    print(f"Rapport généré : {path}")
