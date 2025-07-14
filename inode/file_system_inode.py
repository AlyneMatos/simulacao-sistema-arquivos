from collections import deque
from inode.config import BLOCK_SIZE, MAX_BLOCKS, INODE_TABLE_SIZE
from inode.block import Block
from inode.inode import Inode

class FileSystemInode:
    def __init__(self):
        self.inode_table = {}
        self.next_inode_id = 0
        self.block_storage = {}
        self.free_blocks = deque(range(MAX_BLOCKS))

        root_inode = self.create_inode("/", is_dir=True)
        self.root = root_inode
        self.current_dir = self.root

    def create_inode(self, name, is_dir=False, parent=None):
        if len(self.inode_table) >= INODE_TABLE_SIZE:
            print("Erro: limite de i-nodes atingido.")
            return None
        inode = Inode(self.next_inode_id, name, is_dir, parent)
        self.inode_table[self.next_inode_id] = inode
        self.next_inode_id += 1
        if parent and parent.is_dir:
            parent.children[name] = inode
        return inode

    def mkdir(self, dirname):
        if dirname in self.current_dir.children:
            print("Diretório já existe.")
            return
        self.create_inode(dirname, is_dir=True, parent=self.current_dir)

    def touch(self, filename):
        if filename in self.current_dir.children:
            print("Arquivo já existe.")
            return
        self.create_inode(filename, is_dir=False, parent=self.current_dir)

    def delete(self, name):
        if name not in self.current_dir.children:
            print("Arquivo/Diretório não encontrado.")
            return
        inode = self.current_dir.children[name]

        if not inode.is_dir:
            for block_id in inode.blocks:
                self._free_block(block_id)

        del self.inode_table[inode.inode_id]
        del self.current_dir.children[name]
        print(f"{name} removido com sucesso.")

    def ls(self):
        for name in self.current_dir.children:
            print(name)

    def cd(self, dirname):
        if dirname == ".":
            return
        elif dirname == "..":
            if self.current_dir.parent:
                self.current_dir = self.current_dir.parent
        elif dirname in self.current_dir.children:
            inode = self.current_dir.children[dirname]
            if inode.is_dir:
                self.current_dir = inode
            else:
                print("Não é um diretório.")
        else:
            print("Diretório não encontrado.")

    def get_path(self, inode=None):
        if inode is None:
            inode = self.current_dir
        parts = []
        while inode:
            parts.append(inode.name)
            inode = inode.parent
        return "/" + "/".join(reversed(parts[:-1]))

    def _allocate_block(self, data):
        if not self.free_blocks:
            print("Erro: espaço em disco esgotado.")
            return None
        block_id = self.free_blocks.popleft()
        block_id = f"block_{block_id}"
        self.block_storage[block_id] = Block(block_id, data)
        return block_id

    def _free_block(self, block_id):
        block_index = int(block_id.split("_")[1])
        self.free_blocks.append(block_index)
        del self.block_storage[block_id]

    def write(self, filename, data):
        inode = self._get_inode_by_name(filename)
        if inode is None:
            print("Arquivo não encontrado.")
            return

        novos_blocos = []
        for i in range(0, len(data), BLOCK_SIZE):
            chunk = data[i:i + BLOCK_SIZE]
            block_id = self._allocate_block(chunk)
            if block_id is None:
                print("Erro: falha ao alocar bloco.")
                for bid in novos_blocos:
                    self._free_block(bid)
                return
            novos_blocos.append(block_id)

        for old_block in inode.blocks:
            self._free_block(old_block)

        inode.blocks = novos_blocos
        inode.size = len(data)

    def read(self, filename):
        inode = self._get_inode_by_name(filename)
        if inode is None:
            print("Arquivo não encontrado.")
            return None

        parts = []
        for block_id in inode.blocks:
            block = self.block_storage.get(block_id)
            if block:
                parts.append(block.data)
        content = ''.join(parts)
        print(content)

    def move(self, source_name, target_dir_name):
        if source_name not in self.current_dir.children:
            print(f"'{source_name}' não encontrado no diretório atual.")
            return
        if target_dir_name not in self.current_dir.children:
            print(f"Diretório destino '{target_dir_name}' não encontrado no diretório atual.")
            return

        source_inode = self.current_dir.children[source_name]
        target_inode = self.current_dir.children[target_dir_name]

        if not target_inode.is_dir:
            print(f"'{target_dir_name}' não é um diretório.")
            return

        if source_name in target_inode.children:
            print(f"Já existe um arquivo ou diretório chamado '{source_name}' no destino.")
            return

        del self.current_dir.children[source_name]

        source_inode.parent = target_inode

        target_inode.children[source_name] = source_inode

        print(f"'{source_name}' movido para '{target_dir_name}' com sucesso.")

    def show_inode_table(self):
        print("\nTabela de i-nodes:")
        for inode_id, inode in self.inode_table.items():
            print(f"ID: {inode_id}, Nome: {inode.name}, Dir: {inode.is_dir}, "
                  f"Tamanho: {inode.size}, Blocos: {inode.blocks}")

    def show_free_blocks(self):
        print(f"\nBlocos livres: {len(self.free_blocks)} / {MAX_BLOCKS}")
        print(f"IDs disponíveis: {sorted(self.free_blocks)}")

    def _get_inode_by_name(self, name):
        return self.current_dir.children.get(name)
