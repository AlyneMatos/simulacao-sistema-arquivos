import random
import time
import matplotlib.pyplot as plt
import os

def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    func(*args, **kwargs)
    end = time.perf_counter()
    return end - start

def performance_test_inode(fs_inode):
    large_text = "ABCD" * 10000

    fs_inode.touch("bigfile.txt")

    t_write = measure_time(fs_inode.write, "bigfile.txt", large_text)
    t_read = measure_time(fs_inode.read, "bigfile.txt")
    fs_inode.mkdir("dir1")
    t_move = measure_time(fs_inode.move, "bigfile.txt", "dir1")

    return [t_write, t_read, t_move]

def performance_test_linked_list(fs_ll):
    large_text = "ABCD" * 10000

    fs_ll.touch("bigfile.txt")

    t_write = measure_time(fs_ll.write, "bigfile.txt", large_text)
    t_read = measure_time(fs_ll.read, "bigfile.txt")
    fs_ll.mkdir("dir1")
    t_move = measure_time(fs_ll.move, "bigfile.txt", "dir1")

    return [t_write, t_read, t_move]

def read_random_inode(fs_inode, filename, start, end):
    inode = fs_inode.current_dir.children[filename]
    idx_start = start // 4
    idx_end = end // 4
    offset_start = start % 4
    offset_end = end % 4

    data = ""
    for i in range(idx_start, idx_end + 1):
        block_id = inode.blocks[i]
        block_data = fs_inode.block_storage.get(block_id, "")
        data += block_data

    return data[offset_start:offset_start + (end - start)]

def read_random_linked_list(fs_ll, filename, start, end):
    file = fs_ll.current_dir.children[filename]
    current = file.start_block
    idx = 0
    result = []

    while current and idx < end:
        if idx >= start:
            result.append(current.data)
        current = current.next_block
        idx += 1

    return ''.join(result)

def performance_test(fs_inode, fs_ll):
    inode_times = performance_test_inode(fs_inode)
    linked_list_times = performance_test_linked_list(fs_ll)

    print("\n===== Resultados - Sistema I-node =====")
    print(f"Tempo de Escrita: {inode_times[0]:.6f} s")
    print(f"Tempo de Leitura: {inode_times[1]:.6f} s")
    print(f"Tempo de Movimentação: {inode_times[2]:.6f} s")

    print("\n===== Resultados - Sistema Lista Encadeada =====")
    print(f"Tempo de Escrita: {linked_list_times[0]:.6f} s")
    print(f"Tempo de Leitura: {linked_list_times[1]:.6f} s")
    print(f"Tempo de Movimentação: {linked_list_times[2]:.6f} s")

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

    for i, v in enumerate(inode_times):
        plt.text(i - 0.15, v, f"{v:.2e}", ha='center', va='bottom', fontsize=9)
    for i, v in enumerate(linked_list_times):
        plt.text(i + 0.15, v, f"{v:.2e}", ha='center', va='bottom', fontsize=9)

    os.makedirs("data", exist_ok=True)
    plt.savefig("data/resultado_comparacao.png")
    print("\nGráfico salvo em: data/resultado_comparacao.png")

def create_nested_dirs(fs, depth):
    for i in range(1, depth + 1):
        fs.mkdir(f"dir{i}")
        fs.cd(f"dir{i}")

    for _ in range(depth):
        fs.cd("..")

def navigation_only(fs, depth):
    for i in range(1, depth + 1):
        fs.cd(f"dir{i}")

    for _ in range(depth):
        fs.cd("..")

def test_random_access(fs_inode, fs_ll, num_tests=10, read_size=1000):
    inode_times = []
    ll_times = []

    file_size = fs_inode.current_dir.children["bigfile.txt"].size

    for _ in range(num_tests):
        start = random.randint(0, file_size - read_size)
        end = start + read_size

        t_inode = measure_time(read_random_inode, fs_inode, "bigfile.txt", start, end)
        t_ll = measure_time(read_random_linked_list, fs_ll, "bigfile.txt", start, end)

        inode_times.append(t_inode)
        ll_times.append(t_ll)

    avg_inode = sum(inode_times) / num_tests
    avg_ll = sum(ll_times) / num_tests

    print("\n===== Teste Acesso Aleatório =====")
    print(f"Média (I-node): {avg_inode:.6f} s")
    print(f"Média (Lista Encadeada): {avg_ll:.6f} s")

    # Gráfico
    labels = [f"Teste {i+1}" for i in range(num_tests)]
    x = range(num_tests)

    plt.figure(figsize=(12, 6))
    plt.bar([i - 0.15 for i in x], inode_times, width=0.3, label='I-node', color='blue')
    plt.bar([i + 0.15 for i in x], ll_times, width=0.3, label='Lista Encadeada', color='green')
    plt.xticks(x, labels, rotation=45)
    plt.ylabel("Tempo (s)")
    plt.title("Teste de Acesso Aleatório - I-node vs Lista Encadeada")
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/acesso_aleatorio_comparacao.png")
    print("Gráfico salvo em: data/acesso_aleatorio_comparacao.png")

def test_navigation(fs_inode, fs_ll, depth=100):
    inode_time = measure_time(navigation_only, fs_inode, depth)
    ll_time = measure_time(navigation_only, fs_ll, depth)

    print("\n===== Teste de Facilidade de Navegação =====")
    print(f"Tempo (I-node): {inode_time:.6f} s")
    print(f"Tempo (Lista Encadeada): {ll_time:.6f} s")

    plt.figure(figsize=(8, 5))
    plt.bar(['I-node', 'Lista Encadeada'], [inode_time, ll_time], color=['blue', 'green'])
    plt.ylabel("Tempo (s)")
    plt.title(f"Facilidade de Navegação (Profundidade {depth})")
    plt.tight_layout()
    os.makedirs("data", exist_ok=True)
    plt.savefig("data/navegacao_comparacao.png")
    print("Gráfico salvo em: data/navegacao_comparacao.png")