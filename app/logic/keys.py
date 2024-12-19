from itertools import chain, combinations
from typing import Set, List, Dict, Tuple

def powerset(iterable: set) -> chain:
    """
    Tìm tất cả tập con của một tập hợp
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def parse_dependencies(F: List[str]) -> List[Tuple[set, set]]:
    """
    Chuyển đổi chuỗi phụ thuộc hàm thành tuple (left, right)
    """
    result = []
    for f in F:
        left, right = f.split('->')
        result.append((
            set(left.strip()),
            set(right.strip())
        ))
    return result

def closure(attributes: Set[str], F: List[str]) -> Set[str]:
    """
    Tính bao đóng của tập thuộc tính
    """
    closure_set = set(attributes)
    deps = parse_dependencies(F)
    
    while True:
        added = False
        for left, right in deps:
            if left.issubset(closure_set) and not right.issubset(closure_set):
                closure_set.update(right)
                added = True
        if not added:
            break
    return closure_set

def find_tn_tg(Q: Set[str], F: List[str]) -> Tuple[Set[str], Set[str]]:
    """
    Tìm tập nguồn (TN) và tập trung gian (TG)
    """
    deps = parse_dependencies(F)
    L = set(chain.from_iterable(left for left, _ in deps))
    R = set(chain.from_iterable(right for _, right in deps))
    
    TN = Q - R  # Tập nguồn
    TG = L & R  # Tập trung gian
    return TN, TG

def find_superkeys(TN: Set[str], TG: Set[str], Q: Set[str], F: List[str]) -> List[Set[str]]:
    """
    Tìm tất cả các siêu khóa
    """
    superkeys = []
    for xi in powerset(TG):
        xi_set = TN.union(set(xi))
        if closure(xi_set, F) == Q:
            # Kiểm tra tính tối thiểu
            if not any(xi_set > existing for existing in superkeys):
                superkeys.append(xi_set)
                # Loại bỏ các siêu khóa không tối thiểu đã tìm thấy trước đó
                superkeys = [sk for sk in superkeys if not sk > xi_set]
    return superkeys

def find_keys(superkeys: List[Set[str]], TG: Set[str]) -> List[Set[str]]:
    """
    Tìm các khóa (siêu khóa tối thiểu)
    """
    keys = []
    for sk in sorted(superkeys, key=len):  # Xét theo độ dài tăng dần
        if not any(sk > k for k in keys):  # Kiểm tra tính tối thiểu
            keys.append(sk)
    return keys

def prepare_table_data(TN: Set[str], TG: Set[str], Q: Set[str], F: List[str]) -> List[Dict]:
    """
    Chuẩn bị dữ liệu cho bảng hiển thị
    """
    superkeys = find_superkeys(TN, TG, Q, F)
    keys = find_keys(superkeys, TG)
    table_data = []
    
    for xi in powerset(TG):
        xi_set = set(xi)
        k = TN.union(xi_set)
        k_plus = closure(k, F)
        is_superkey = k_plus == Q
        is_key = k in keys
        
        table_data.append({
            "xi": ", ".join(sorted(xi_set)) if xi_set else "∅",
            "k": ", ".join(sorted(k)),
            "k_plus": ", ".join(sorted(k_plus)),
            "sk": "Yes" if is_superkey else "No",
            "key": "Yes" if is_key else "No"
        })
    
    return table_data

def process_keys(attributes: str, dependencies: str) -> Dict:
    """
    Hàm chính xử lý việc tìm khóa
    """
    try:
        # Chuẩn hóa dữ liệu đầu vào
        Q = set(attr.strip() for attr in attributes.split(','))
        F = [dep.strip() for dep in dependencies.split(',')]
        
        # Tìm TN và TG
        TN, TG = find_tn_tg(Q, F)
        
        # Kiểm tra từng điều kiện dừng riêng biệt
        if len(TG) == 0:
            return {
                'success': True,
                'TN': ", ".join(sorted(TN)),
                'TG': ", ".join(sorted(TG)),
                'keys': [", ".join(sorted(TN))],
                'skip_table': True,
                'stop_reason': 'empty_tg'  # TG rỗng
            }
            
        if closure(TN, F) == Q:
            return {
                'success': True,
                'TN': ", ".join(sorted(TN)),
                'TG': ", ".join(sorted(TG)),
                'keys': [", ".join(sorted(TN))],
                'skip_table': True,
                'stop_reason': 'tn_closure'  # TN+ = Q
            }
        
        # Nếu không thỏa điều kiện dừng, tiếp tục tạo bảng
        table_data = prepare_table_data(TN, TG, Q, F)
        
        return {
            'success': True,
            'TN': ", ".join(sorted(TN)),
            'TG': ", ".join(sorted(TG)),
            'table_data': table_data,
            'skip_table': False
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Chỉ export hàm process_keys
__all__ = ['process_keys']