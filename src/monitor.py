import docker
from tabulate import tabulate

def get_container_stats(container):
    stats = container.stats(stream=False)

    mem_usage = stats.get('memory_stats', {}).get('usage', 0) / (1024 ** 2)

    cpu_stats = stats.get('cpu_stats', {}).get('cpu_usage', {})
    precpu_stats = stats.get('precpu_stats', {}).get('cpu_usage', {})
    system_cpu = stats.get('cpu_stats', {}).get('system_cpu_usage', 0)
    pre_system_cpu = stats.get('precpu_stats', {}).get('system_cpu_usage', 0)

    cpu_delta = cpu_stats.get('total_usage', 0) - precpu_stats.get('total_usage', 0)
    system_delta = system_cpu - pre_system_cpu
    cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0

    net_rx = 0
    net_tx = 0
    if 'networks' in stats:
        for iface in stats['networks'].values():
            net_rx += iface.get('rx_bytes', 0)
            net_tx += iface.get('tx_bytes', 0)

    return {
        'cpu_percent': round(cpu_percent, 2),
        'mem_MB': round(mem_usage, 2),
        'rx_KB': round(net_rx / 1024, 2),
        'tx_KB': round(net_tx / 1024, 2),
    }


def list_containers():
    """
    Liste les conteneurs Docker et affiche leurs statistiques.
    """
    client = docker.from_env()
    containers = client.containers.list(all=True)
    result = []

    for container in containers:
        stats = {
            'Nom': container.name,
            'Image': container.image.tags[0] if container.image.tags else 'inconnu',
            'Statut': container.status
        }

        if container.status == 'running':
            usage = get_container_stats(container)
            stats.update({
                'CPU (%)': usage['cpu_percent'],
                'Mémoire (Mo)': usage['mem_MB'],
                'Rx (Ko)': usage['rx_KB'],
                'Tx (Ko)': usage['tx_KB']
            })
        else:
            stats.update({
                'CPU (%)': '-',
                'Mémoire (Mo)': '-',
                'Rx (Ko)': '-',
                'Tx (Ko)': '-'
            })

        result.append(stats)

    print(tabulate(result, headers='keys', tablefmt='grid'))
    
list_containers()

def collect_data():
    client = docker.from_env()
    containers = client.containers.list(all=True)

    total_cpu = 0
    total_mem = 0
    restart_count = 0
    alerts = []

    active_containers = 0

    for container in containers:
        try:
            stats = get_container_stats(container)
            total_cpu += stats['cpu_percent']
            total_mem += stats['mem_MB']
            active_containers += 1

            inspect = container.attrs
            restart_count += inspect['RestartCount'] if 'RestartCount' in inspect else 0

            # Exemple d'alerte simple
            if stats['cpu_percent'] > 80:
                alerts.append(f"CPU élevé sur {container.name}: {stats['cpu_percent']}%")
            if stats['mem_MB'] > 500:
                alerts.append(f"RAM élevée sur {container.name}: {stats['mem_MB']} Mo")

        except Exception as e:
            alerts.append(f"Erreur collecte stats sur {container.name}: {str(e)}")

    avg_cpu = round(total_cpu / active_containers, 2) if active_containers > 0 else 0
    avg_mem = round(total_mem / active_containers, 2) if active_containers > 0 else 0

    return {
        'restarts': restart_count,
        'avg_cpu': avg_cpu,
        'avg_ram': avg_mem,
        'alerts': alerts
    }