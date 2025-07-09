import time
import matplotlib.pyplot as plt
from inode.file_system_inode import FileSystemInode
from lista_encadeada.file_system_linked_list import FileSystemLinkedList
import os

def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    func(*args, **kwargs)
    end = time.perf_counter()
    return end - start

def performance_test_inode(fs_inode):
    large_text = "ABCD" * 10000  # 10.000 caracteres

    fs_inode.touch("bigfile.txt")

    t_write = measure_time(fs_inode.write, "bigfile.txt", large_text)
    t_read = measure_time(fs_inode.read, "bigfile.txt")
    fs_inode.mkdir("dir1")
    t_move = measure_time(fs_inode.move, "bigfile.txt", "dir1")

    return [t_write, t_read, t_move]

def performance_test_linked_list(fs_ll):
    large_text = "ABCD" * 10000  # 10.000 caracteres

    fs_ll.touch("bigfile.txt")

    t_write = measure_time(fs_ll.write, "bigfile.txt", large_text)
    t_read = measure_time(fs_ll.read, "bigfile.txt")
    fs_ll.mkdir("dir1")
    t_move = measure_time(fs_ll.move, "bigfile.txt", "dir1")

    return [t_write, t_read, t_move]

# Executar testes
fs_inode = FileSystemInode()
fs_ll = FileSystemLinkedList()

def performance_test(fs_inode, fs_ll):
    inode_times = performance_test_inode(fs_inode)
    linked_list_times = performance_test_linked_list(fs_ll)

    # Mostrar resultados no terminal
    print("\n===== Resultados - Sistema I-node =====")
    print(f"Tempo de Escrita: {inode_times[0]:.6f} s")
    print(f"Tempo de Leitura: {inode_times[1]:.6f} s")
    print(f"Tempo de Movimentação: {inode_times[2]:.6f} s")

    print("\n===== Resultados - Sistema Lista Encadeada =====")
    print(f"Tempo de Escrita: {linked_list_times[0]:.6f} s")
    print(f"Tempo de Leitura: {linked_list_times[1]:.6f} s")
    print(f"Tempo de Movimentação: {linked_list_times[2]:.6f} s")

    # Plotar gráfico comparativo
    labels = ["Escrita", "Leitura", "Movimentação"]
    x = range(len(labels))

    plt.figure(figsize=(10, 6))
    plt.bar([i - 0.15 for i in x], inode_times, width=0.3, label='I-node', color='blue')
    plt.bar([i + 0.15 for i in x], linked_list_times, width=0.3, label='Lista Encadeada', color='green')
    plt.xticks(x, labels)
    plt.ylabel("Tempo (s)")
    plt.title("Comparação de Desempenho - I-node vs Lista Encadeada")
    plt.legend()
    plt.tight_layout()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    os.makedirs("data", exist_ok=True)
    plt.savefig("data/resultado_comparacao.png")
    print("\nGráfico salvo em: data/resultado_comparacao.png")

