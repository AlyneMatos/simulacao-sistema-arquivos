from  inode.file_system_inode import FileSystemInode
from lista_encadeada.file_system_linked_list import FileSystemLinkedList

def menu(fs):
    while True:
        path = fs.get_path() if hasattr(fs, "get_path") else "/"
        cmd = input(f">> {path}: ").strip()
        if not cmd:
            continue
        parts = cmd.split()
        op = parts[0]
        args = parts[1:]

        if op == "mkdir":
            fs.mkdir(args[0])
        elif op == "touch":
            fs.touch(args[0])
        elif op == "ls":
            fs.ls()
        elif op == "cd":
            fs.cd(args[0])
        elif op == "move":
            fs.move(args[0], args[1])
        elif op == "write":
            fs.write(args[0], " ".join(args[1:]))
        elif op == "read":
            fs.read(args[0])
        elif op == "delete":
            fs.delete(args[0])
        elif op == "inodes":
            fs.show_inode_table()
        elif op == "blocks":
            fs.show_free_blocks()
        elif op == "exit":
            break
        else:
            print("Comando inválido.")

print("Escolha o sistema de arquivos:")
print("1 - i-nodes")
print("2 - Lista Encadeada")
choice = input("Opção: ")

fs = FileSystemInode() if choice == "1" else FileSystemLinkedList()
menu(fs)
