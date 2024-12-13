from itertools import chain, combinations
from typing import Set, List, Tuple

class KeyFinder:
    def __init__(self, attributes: str, dependencies: str):
        # Khởi tạo các thuộc tính
        self.all_attributes = set(attributes.replace(' ', '').split(','))
        self.dependencies = [tuple(dep.split('->')) for dep in dependencies.split(',')]
        self.steps = []

    def find_keys(self) -> dict:
        """
        Tìm khóa và siêu khóa theo quy trình:
        1. Tìm tập nguồn (TN)
        2. Tìm tập trung gian (TG)
        3. Tìm siêu khóa
        4. Tìm khóa từ siêu khóa
        """
        try:
            # 1. Tìm tập nguồn (TN) - các thuộc tính chỉ xuất hiện ở vế trái
            right_sides = set(chain.from_iterable(dep[1].strip() for dep in self.dependencies))
            source_attrs = self.all_attributes - right_sides
            self.steps.append(f"Tìm tập nguồn (TN): {', '.join(sorted(source_attrs))}")

            # 2. Tìm tập trung gian (TG) - các thuộc tính xuất hiện cả vế trái và vế phải
            left_sides = set(chain.from_iterable(dep[0].strip() for dep in self.dependencies))
            intermediate_attrs = left_sides & right_sides
            self.steps.append(f"Tìm tập trung gian (TG): {', '.join(sorted(intermediate_attrs))}")

            # Xử lý trường hợp đặc biệt: TG rỗng
            if not intermediate_attrs:
                self.steps.append("TG rỗng => TN là khóa duy nhất")
                return {
                    'superkeys': [sorted(list(source_attrs))],
                    'keys': [sorted(list(source_attrs))],
                    'steps': self.steps,
                    'success': True
                }

            # 3. Tìm siêu khóa
            superkeys = []
            # Sinh tất cả tập con của TG và kết hợp với TN
            for subset in self._generate_subsets(intermediate_attrs):
                # Mọi siêu khóa phải chứa TN
                candidate = source_attrs.union(subset)
                closure = self._calculate_closure(candidate)
                
                if closure == self.all_attributes:
                    superkeys.append(candidate)
                    self.steps.append(f"Tìm thấy siêu khóa: {', '.join(sorted(candidate))}")

            # 4. Tìm khóa (siêu khóa tối thiểu)
            keys = []
            for candidate in superkeys:
                is_minimal = True
                # Kiểm tra tính tối thiểu
                for other in superkeys:
                    if other != candidate and other.issubset(candidate):
                        is_minimal = False
                        break
                
                if is_minimal:
                    keys.append(candidate)
                    self.steps.append(f"Xác định khóa: {', '.join(sorted(candidate))}")

            return {
                'superkeys': [sorted(list(sk)) for sk in sorted(superkeys, key=len)],
                'keys': [sorted(list(k)) for k in sorted(keys, key=len)],
                'steps': self.steps,
                'success': True
            }

        except Exception as e:
            return {
                'superkeys': [],
                'keys': [],
                'steps': [f"Lỗi: {str(e)}"],
                'success': False
            }

    def _calculate_closure(self, attributes: Set[str]) -> Set[str]:
        """Tính bao đóng của một tập thuộc tính"""
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for left, right in self.dependencies:
                left = left.strip()
                right = right.strip()
                if set(left).issubset(closure) and not set(right).issubset(closure):
                    closure.update(set(right))
                    changed = True
        
        return closure

    def _generate_subsets(self, attrs: Set[str]) -> List[Set[str]]:
        """Sinh tất cả tập con của một tập thuộc tính"""
        return [set(combo) for r in range(len(attrs) + 1) 
                for combo in combinations(attrs, r)]

def find_keys(attributes: str, dependencies: str) -> dict:
    """
    Hàm wrapper để sử dụng KeyFinder
    """
    finder = KeyFinder(attributes, dependencies)
    return finder.find_keys()
