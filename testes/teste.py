import matplotlib.pyplot as plt
import time
from inode.file_system_inode import FileSystemInode
from lista_encadeada.file_system_linked_list import FileSystemLinkedList

def benchmark(fs_class, filename_prefix, data_sizes):
    write_times = []
    read_times = []

    for size in data_sizes:
        fs = fs_class()
        filename = f"{filename_prefix}_{size}.txt"
        data = "x" * size

        fs.touch(filename)

        #  tempo de escrita
        start_write = time.perf_counter()
        fs.write(filename, data)
        end_write = time.perf_counter()
        write_times.append(end_write - start_write)

        # tempo de leitura
        start_read = time.perf_counter()
        fs.read(filename)
        end_read = time.perf_counter()
        read_times.append(end_read - start_read)

    return write_times, read_times

def executar_testes():
    data_sizes = list(range(10, 10001, 100))

    inode_write, inode_read = benchmark(FileSystemInode, "file_inode", data_sizes)

    ll_write, ll_read = benchmark(FileSystemLinkedList, "file_ll", data_sizes)

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(data_sizes, inode_write, label="Inode - Escrita", color='blue')
    plt.plot(data_sizes, ll_write, label="Lista Encadeada - Escrita", color='orange')
    plt.xlabel("Tamanho do arquivo (caracteres)")
    plt.ylabel("Tempo de escrita (s)")
    plt.title("Desempenho de Escrita")
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(data_sizes, inode_read, label="Inode - Leitura", color='green')
    plt.plot(data_sizes, ll_read, label="Lista Encadeada - Leitura", color='red')
    plt.xlabel("Tamanho do arquivo (caracteres)")
    plt.ylabel("Tempo de leitura (s)")
    plt.title("Desempenho de Leitura")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    plt.savefig("benchmark_resultados.png")
    # plt.show()

if __name__ == "__main__":
    executar_testes()
