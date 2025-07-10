from inode.file_system_inode import FileSystemInode
from lista_encadeada.file_system_linked_list import FileSystemLinkedList
from testes.comparar_desempenho import performance_test, test_random_access, test_navigation, create_nested_dirs

if __name__ == "__main__":
    fs_inode = FileSystemInode()
    fs_ll = FileSystemLinkedList()

    performance_test(fs_inode, fs_ll)

    fs_inode.cd("dir1")
    fs_ll.cd("dir1")
    test_random_access(fs_inode, fs_ll)

    create_nested_dirs(fs_inode, 100)
    create_nested_dirs(fs_ll, 100)

    test_navigation(fs_inode, fs_ll, depth=100)
