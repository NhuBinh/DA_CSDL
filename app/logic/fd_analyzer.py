class FunctionalDependency:
    def __init__(self, left, right):
        # Convert both left and right to sorted lists of attributes
        self.left = sorted(left)
        self.right = sorted(right)

    def __eq__(self, other):
        if not isinstance(other, FunctionalDependency):
            return False
        return self.left == other.left and set(self.right) == set(other.right)

    def __hash__(self):
        return hash((tuple(self.left), tuple(self.right)))

    def __repr__(self):
        return f"{','.join(self.left)} -> {','.join(self.right)}"

    @staticmethod
    def parse_dependencies(deps_str):
        """Parse dependencies from string format."""
        try:
            dependencies = set()
            for line in deps_str.strip().split('\n'):
                if '->' not in line:
                    continue
                left, right = line.split('->')
                left_attrs = [attr.strip() for attr in left.split(',') if attr.strip()]
                right_attrs = [attr.strip() for attr in right.split(',') if attr.strip()]
                dependencies.add(FunctionalDependency(left_attrs, right_attrs))
            return dependencies
        except Exception as e:
            raise ValueError(f"Lỗi khi xử lý phụ thuộc hàm: {str(e)}")

    @staticmethod
    def parse_decomposition(decomp_str):
        """Parse decomposition from string format."""
        try:
            return [
                [attr.strip() for attr in relation.split(',') if attr.strip()]
                for relation in decomp_str.strip().split('\n')
                if relation.strip()
            ]
        except Exception as e:
            raise ValueError(f"Lỗi khi xử lý lược đồ: {str(e)}")

    @staticmethod
    def check_preservation(dependencies_str, decomposition_str):
        try:
            # Parse input strings
            dependencies = FunctionalDependency.parse_dependencies(dependencies_str)
            decomposition = FunctionalDependency.parse_decomposition(decomposition_str)
            
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
                        if set(fd.left).issubset(closure):
                            new_attrs = set(fd.right) - closure
                            if new_attrs:
                                closure.update(new_attrs)
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
                    if set(fd.left).issubset(rel_set) and all(r in rel_set for r in fd.right):
                        G.add(fd)
                        steps.append(f"Giữ lại: {fd}")

            # Step 3: Calculate F - G
            F_minus_G = dependencies - G
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
                
                if all(r in closure for r in fd.right):
                    steps.append(f"==> {fd} thuộc G+")
                else:
                    steps.append(f"==> {fd} không thuộc G+")
                    return False, f"Phép tách không bảo toàn phụ thuộc: {fd}", steps

            steps.append("\nKết luận: Tất cả phụ thuộc trong F-G đều suy diễn được từ G nên phép tách bảo toàn phụ thuộc hàm")
            return True, "Phép tách bảo toàn phụ thuộc hàm", steps

        except ValueError as e:
            return False, str(e), []
        except Exception as e:
            return False, f"Lỗi không xác định: {str(e)}", []