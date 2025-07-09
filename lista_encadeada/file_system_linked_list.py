class Block:
    def __init__(self, data, next_block=None):
        self.data = data
        self.next_block = next_block

class File:
    def __init__(self, name, parent=None):
        self.name = name
        self.size = 0
        self.start_block = None
        self.parent = parent

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.children = {}
        self.parent = parent

class FileSystemLinkedList:
    def __init__(self):
        self.root = Directory("/")
        self.current_dir = self.root

    def mkdir(self, dirname):
        if dirname in self.current_dir.children:
            print("Diretório já existe.")
            return
        self.current_dir.children[dirname] = Directory(dirname, parent=self.current_dir)

    def touch(self, filename):
        if filename in self.current_dir.children:
            print("Arquivo já existe.")
            return
        self.current_dir.children[filename] = File(filename, parent=self.current_dir)

    def ls(self):
        for name in self.current_dir.children:
            print(name)

    def cd(self, dirname):
        if dirname == ".":
            return
        elif dirname == "..":
            if self.current_dir.parent is not None:
                self.current_dir = self.current_dir.parent
        elif dirname in self.current_dir.children and isinstance(self.current_dir.children[dirname], Directory):
            self.current_dir = self.current_dir.children[dirname]
        else:
            print("Diretório não encontrado.")

    def move(self, source_path, target_dir_name):
        source_parent, source_name = self.find_dir_and_name(source_path)
        if source_parent is None or source_name not in source_parent.children:
            print("Arquivo não encontrado.")
            return

        if target_dir_name not in self.current_dir.children or not isinstance(
                self.current_dir.children[target_dir_name], Directory):
            print("Diretório de destino inválido.")
            return

        file_obj = source_parent.children.pop(source_name)
        target_dir = self.current_dir.children[target_dir_name]

        # Atualiza o parent para o novo diretório
        file_obj.parent = target_dir

        target_dir.children[source_name] = file_obj
        print(f"Arquivo '{source_name}' movido para '{target_dir_name}'.")

    def write(self, filename, data, block_size=4):
        if filename not in self.current_dir.children:
            print("Arquivo não encontrado.")
            return
        file = self.current_dir.children[filename]
        file.size = len(data)

        prev_block = None
        file.start_block = None  # resetar a lista de blocos ao escrever novo conteúdo

        # Dividir dados em blocos de tamanho block_size
        for i in range(0, len(data), block_size):
            bloco_conteudo = data[i:i + block_size]
            new_block = Block(bloco_conteudo)

            if prev_block is None:
                file.start_block = new_block
            else:
                prev_block.next_block = new_block

            prev_block = new_block

        # print(f"Arquivo {filename} escrito com {file.size} bytes em blocos de {block_size} caracteres.")

    def read(self, filename):
        if filename not in self.current_dir.children:
            print("Arquivo não encontrado.")
            return
        file = self.current_dir.children[filename]
        chars = []
        block = file.start_block
        while block:
            chars.append(block.data)
            block = block.next_block
        print(''.join(chars))

    def delete(self, name):
        if name not in self.current_dir.children:
            print("Arquivo/Diretório não encontrado.")
            return
        del self.current_dir.children[name]
        print(f"{name} removido com sucesso.")

    def find_dir_and_name(self, path):
        parts = path.strip().split('/')
        current = self.current_dir
        for part in parts[:-1]:
            if part in current.children and isinstance(current.children[part], Directory):
                current = current.children[part]
            else:
                return None, None
        return current, parts[-1]

    def get_path(self, directory=None):
        if directory is None:
            directory = self.current_dir
        path_parts = []
        while directory is not None:
            path_parts.append(directory.name)
            directory = directory.parent
        path_parts.reverse()
        if path_parts[0] == "/":
            return "/" + "/".join(path_parts[1:])
        return "/".join(path_parts)


