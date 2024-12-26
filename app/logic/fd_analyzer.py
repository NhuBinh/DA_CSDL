class FunctionalDependency:
    def __init__(self, left, right):
        self.left = sorted(left)
        self.right = right

    def __eq__(self, other):
        if not isinstance(other, FunctionalDependency):
            return False
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((tuple(self.left), self.right))

    def __repr__(self):
        return f"{','.join(self.left)} -> {self.right}"

    @staticmethod
    def check_preservation(dependencies, decomposition):
        steps = []
        
        if not dependencies or not decomposition:
            return False, "Dữ liệu đầu vào không hợp lệ", steps

        def get_closure(attrs, fds):
            closure = set(attrs)
            steps_closure = []
            steps_closure.append(f"Bao đóng ban đầu: {','.join(sorted(closure))}")
            
            changed = True
            while changed:
                changed = False
                for fd in fds:
                    if set(fd.left).issubset(closure) and fd.right not in closure:
                        closure.add(fd.right)
                        changed = True
                        steps_closure.append(f"Áp dụng {fd}: {','.join(sorted(closure))}")
            return closure, steps_closure

        # Step 1: Show initial FDs (F)
        steps.append("Bước 1: Tập F ban đầu:")
        for fd in dependencies:
            steps.append(f"  {fd}")

        # Step 2: Get preserved FDs (G)
        G = set()
        steps.append("\nBước 2: Tính các phụ thuộc hàm trên từng lược đồ con (G):")
        for idx, relation in enumerate(decomposition, 1):
            rel_set = set(relation)
            steps.append(f"\nLược đồ con {idx}: {','.join(sorted(rel_set))}")
            
            for fd in dependencies:
                if set(fd.left).issubset(rel_set) and fd.right in rel_set:
                    G.add(fd)
                    steps.append(f"Giữ lại: {fd}")

        # Step 3: Calculate F - G
        F_minus_G = set(dependencies) - G
        steps.append("\nBước 3: Tìm F - G:")
        if not F_minus_G:
            steps.append("F - G = ∅")
            steps.append("\nKết luận: F = G nên phép tách bảo toàn phụ thuộc hàm")
            return True, "Phép tách bảo toàn phụ thuộc hàm", steps
        else:
            steps.append(f"F - G = {{{', '.join(str(fd) for fd in F_minus_G)}}}")

        # Step 4: Check if F-G FDs are derivable from G
        steps.append("\nBước 4: Kiểm tra các phụ thuộc trong F-G có suy diễn được từ G không:")
        for fd in F_minus_G:
            closure, closure_steps = get_closure(fd.left, list(G))
            steps.append(f"\nKiểm tra {fd}:")
            steps.extend(["  " + s for s in closure_steps])
            
            if fd.right in closure:
                steps.append(f"==> {fd} thuộc G+")
            else:
                steps.append(f"==> {fd} không thuộc G+")
                return False, f"Phép tách không bảo toàn phụ thuộc: {fd}", steps

        steps.append("\nKết luận: Tất cả phụ thuộc trong F-G đều suy diễn được từ G nên phép tách bảo toàn phụ thuộc hàm")
        return True, "Phép tách bảo toàn phụ thuộc hàm", steps