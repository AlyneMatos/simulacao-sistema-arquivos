class Inode:
    def __init__(self, name, is_dir=False, parent=None):
        self.name = name
        self.size = 0
        self.blocks = []  # lista de IDs dos blocos
        self.is_dir = is_dir
        self.children = {} if is_dir else None
        self.parent = parent


class FileSystemInode:
    def __init__(self):
        self.root = Inode("/", is_dir=True)
        self.current_dir = self.root
        self.block_storage = {}  # bloco_id -> conteúdo do bloco
        self.next_block_id = 0

    def mkdir(self, dirname):
        if dirname in self.current_dir.children:
            print("Diretório já existe.")
            return
        self.current_dir.children[dirname] = Inode(dirname, is_dir=True, parent=self.current_dir)

    def touch(self, filename):
        if filename in self.current_dir.children:
            print("Arquivo já existe.")
            return
        self.current_dir.children[filename] = Inode(filename, is_dir=False, parent=self.current_dir)

    def ls(self):
        for name in self.current_dir.children:
            print(name)

    def cd(self, dirname):
        if dirname == ".":
            return
        elif dirname == "..":
            if self.current_dir.parent is not None:
                self.current_dir = self.current_dir.parent
        elif dirname in self.current_dir.children and self.current_dir.children[dirname].is_dir:
            self.current_dir = self.current_dir.children[dirname]
        else:
            print("Diretório não encontrado.")

    def move(self, source_path, target_dir_name):
        source_parent, source_name = self.find_inode_and_parent(source_path)
        if source_parent is None or source_name not in source_parent.children:
            print("Arquivo não encontrado.")
            return

        if target_dir_name not in self.current_dir.children or not self.current_dir.children[target_dir_name].is_dir:
            print("Diretório de destino inválido.")
            return

        inode_to_move = source_parent.children.pop(source_name)
        target_dir = self.current_dir.children[target_dir_name]

        # Atualiza o parent do inode movido
        inode_to_move.parent = target_dir

        target_dir.children[source_name] = inode_to_move
        # print(f"Arquivo '{source_name}' movido para '{target_dir_name}'.")

    def write(self, filename, data, block_size=4):
        if filename not in self.current_dir.children:
            print("Arquivo não encontrado.")
            return
        inode = self.current_dir.children[filename]

        # Limpa blocos antigos
        for block_id in inode.blocks:
            if block_id in self.block_storage:
                del self.block_storage[block_id]
        inode.blocks.clear()

        # Divide dados em blocos e armazena
        for i in range(0, len(data), block_size):
            bloco_conteudo = data[i:i+block_size]
            block_id = f"block_{self.next_block_id}"
            self.next_block_id += 1
            self.block_storage[block_id] = bloco_conteudo
            inode.blocks.append(block_id)

        inode.size = len(data)
        # print(f"Arquivo {filename} escrito com {len(data)} bytes em {len(inode.blocks)} blocos.")

    def read(self, filename):
        if filename not in self.current_dir.children:
            print("Arquivo não encontrado.")
            return
        inode = self.current_dir.children[filename]

        conteudo = ""
        for block_id in inode.blocks:
            bloco = self.block_storage.get(block_id, "")
            conteudo += bloco

        print(inode.blocks)
        print(conteudo)

    def delete(self, name):
        if name not in self.current_dir.children:
            print("Arquivo/Diretório não encontrado.")
            return
        inode = self.current_dir.children[name]
        # Liberar blocos
        if not inode.is_dir:
            for block_id in inode.blocks:
                if block_id in self.block_storage:
                    del self.block_storage[block_id]
        del self.current_dir.children[name]
        print(f"{name} removido com sucesso.")

    def get_path(self, inode=None):
        if inode is None:
            inode = self.current_dir
        path_parts = []
        while inode is not None:
            path_parts.append(inode.name)
            inode = inode.parent
        path_parts.reverse()
        if path_parts[0] == "/":
            return "/" + "/".join(path_parts[1:])
        return "/".join(path_parts)

    def find_inode_and_parent(self, path):
        parts = [p for p in path.strip().split('/') if p]
        current = self.current_dir
        for part in parts[:-1]:
            if part in current.children and current.children[part].is_dir:
                current = current.children[part]
            else:
                return None, None
        return current, parts[-1] if parts else (None, None)
