class Inode:
    def __init__(self, inode_id, name, is_dir=False, parent=None):
        self.inode_id = inode_id
        self.name = name
        self.size = 0
        self.blocks = []
        self.is_dir = is_dir
        self.children = {} if is_dir else None
        self.parent = parent
