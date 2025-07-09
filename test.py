from inode.file_system_inode import FileSystemInode
from lista_encadeada.file_system_linked_list import FileSystemLinkedList
from testes.comparar_desempenho import performance_test

if __name__ == "__main__":
    fs_inode = FileSystemInode()
    fs_ll = FileSystemLinkedList()

    performance_test(fs_inode, fs_ll)
