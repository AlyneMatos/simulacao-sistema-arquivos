MAX_BLOCKS = 1024
BLOCK_SIZE = 64

class Block:
    def __init__(self, data):
        self.data = data
        self.next_block = None  # índice do próximo bloco ou None

class File:
    def __init__(self, name, parent=None):
        self.name = name
        self.size = 0
        self.start_block = None  # índice do primeiro bloco
        self.parent = parent

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}  # nome -> File ou Directory
        self.parent = parent

class FileSystemLinkedList:
    def __init__(self):
        self.root = Directory("/")
        self.current_dir = self.root
        self.blocks = [None] * MAX_BLOCKS
        self.free_blocks = list(range(MAX_BLOCKS))  # blocos livres

    def _allocate_block(self, data):
        if not self.free_blocks:
            print("Erro: disco cheio, sem blocos livres.")
            return None
        block_id = self.free_blocks.pop(0)
        self.blocks[block_id] = Block(data)
        return block_id

    def _free_blocks_chain(self, start_block_id):
        current_id = start_block_id
        while current_id is not None:
            block = self.blocks[current_id]
            next_id = block.next_block
            self.blocks[current_id] = None
            self.free_blocks.append(current_id)
            current_id = next_id

    # --- Navegação ---
    def _resolve_path(self, path):
        if path.startswith("/"):
            current = self.root
            parts = [p for p in path.strip("/").split("/") if p]
        else:
            current = self.current_dir
            parts = [p for p in path.strip().split("/") if p]

        for part in parts[:-1]:
            if part == ".":
                continue
            elif part == "..":
                if current.parent:
                    current = current.parent
            elif part in current.children and isinstance(current.children[part], Directory):
                current = current.children[part]
            else:
                return None, None
        if not parts:
            return current, ""
        return current, parts[-1]

    def _get_node(self, path):
        if path == "/":
            return self.root
        if path.startswith("/"):
            current = self.root
            parts = [p for p in path.strip("/").split("/") if p]
        else:
            current = self.current_dir
            parts = [p for p in path.strip().split("/") if p]

        for part in parts:
            if part == ".":
                continue
            elif part == "..":
                if current.parent:
                    current = current.parent
            elif part in current.children:
                current = current.children[part]
            else:
                return None
        return current

    # --- Comandos ---
    def mkdir(self, dirname):
        if dirname in self.current_dir.children:
            print(f"Diretório '{dirname}' já existe.")
            return
        self.current_dir.children[dirname] = Directory(dirname, parent=self.current_dir)

    def touch(self, filename):
        if filename in self.current_dir.children:
            print(f"Arquivo '{filename}' já existe.")
            return
        self.current_dir.children[filename] = File(filename, parent=self.current_dir)

    def ls(self):
        for name, node in self.current_dir.children.items():
            suffix = "/" if isinstance(node, Directory) else ""
            print(name + suffix)

    def cd(self, dirname):
        if dirname == ".":
            return
        elif dirname == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
            return
        node = self._get_node(dirname)
        if node and isinstance(node, Directory):
            self.current_dir = node
        else:
            print(f"Diretório '{dirname}' não encontrado.")

    def move(self, source_path, target_path):
        src_parent, src_name = self._resolve_path(source_path)
        if not src_parent or src_name not in src_parent.children:
            print(f"Fonte '{source_path}' não encontrada.")
            return

        target_node = self._get_node(target_path)
        if not target_node or not isinstance(target_node, Directory):
            print(f"Destino '{target_path}' não encontrado.")
            return

        node = src_parent.children.pop(src_name)
        node.parent = target_node
        if node.name in target_node.children:
            print(f"Já existe '{node.name}' em '{target_path}'.")
            src_parent.children[src_name] = node  # desfaz mudança
            return
        target_node.children[node.name] = node
        print(f"'{src_name}' movido para '{target_path}' com sucesso.")

    def write(self, filename, data):
        if filename not in self.current_dir.children or not isinstance(self.current_dir.children[filename], File):
            print(f"Arquivo '{filename}' não encontrado.")
            return
        file = self.current_dir.children[filename]

        if file.start_block is not None:
            self._free_blocks_chain(file.start_block)
        file.start_block = None
        file.size = len(data)

        prev_block_id = None
        first_block_id = None
        for i in range(0, len(data), BLOCK_SIZE):
            chunk = data[i:i+BLOCK_SIZE]
            block_id = self._allocate_block(chunk)
            if block_id is None:
                print("Erro ao alocar bloco. Abortando.")
                if first_block_id is not None:
                    self._free_blocks_chain(first_block_id)
                file.start_block = None
                file.size = 0
                return
            if prev_block_id is not None:
                self.blocks[prev_block_id].next_block = block_id
            else:
                first_block_id = block_id
            prev_block_id = block_id
        file.start_block = first_block_id

    def read(self, filename):
        if filename not in self.current_dir.children or not isinstance(self.current_dir.children[filename], File):
            print(f"Arquivo '{filename}' não encontrado.")
            return
        file = self.current_dir.children[filename]

        content = []
        current_block_id = file.start_block
        while current_block_id is not None:
            block = self.blocks[current_block_id]
            content.append(block.data)
            current_block_id = block.next_block
        print("".join(content))

    def delete(self, name):
        if name not in self.current_dir.children:
            print(f"'{name}' não encontrado.")
            return
        node = self.current_dir.children[name]
        if isinstance(node, File) and node.start_block is not None:
            self._free_blocks_chain(node.start_block)
        del self.current_dir.children[name]
        print(f"'{name}' removido com sucesso.")

    def get_path(self):
        parts = []
        current = self.current_dir
        while current is not None:
            parts.append(current.name)
            current = current.parent
        parts.reverse()
        if parts[0] == "/":
            return "/" + "/".join(parts[1:])
        return "/".join(parts)
