
from collections import defaultdict
from typing import Optional, Set, List, Dict, Tuple

def is_in_1NF(attributes: Set[str], primary_keys: List[Set[str]]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn 1 (1NF):
    - Các thuộc tính đều là nguyên tố
    - Các giá trị là đơn trị
    - Phải có khóa chính
    """
    # Mặc định là True vì ta giả sử dữ liệu đầu vào đã thỏa mãn các giá trị đơn trị
    is_valid = len(primary_keys) > 0
    explanation = "Lược đồ ở dạng chuẩn 1 (1NF) vì:\n"
    explanation += "- Các thuộc tính đều là nguyên tố\n"
    explanation += "- Các giá trị là đơn trị\n"
    
    if not primary_keys:
        is_valid = False
        explanation += "- KHÔNG thỏa mãn: Chưa xác định được khóa chính\n"
    else:
        explanation += f"- Có khóa chính: {','.join([','.join(sorted(k)) for k in primary_keys])}\n"
    
    return is_valid, explanation
def find_partial_dependencies(primary_keys: List[Set[str]], 
                            fds: List[Dict]) -> List[Tuple[Set[str], Set[str]]]:
    """
    Tìm các phụ thuộc bộ phận:
    - Phụ thuộc bộ phận xảy ra khi thuộc tính không khoá phụ thuộc vào một phần của khoá chính
    """
    partial_deps = []
    
    # Xác định các thuộc tính không khóa
    all_attributes = set()
    for fd in fds:
        all_attributes.update(fd['left'], fd['right'])
    
    # Tìm các thuộc tính không khóa
    non_prime_attributes = all_attributes - set.union(*primary_keys)
    
    for fd in fds:
        left = fd['left']
        right = fd['right']
        
        # Chỉ xét các FD có vế phải chứa thuộc tính không khóa
        if not right.issubset(non_prime_attributes):
            continue
            
        # Kiểm tra phụ thuộc bộ phận
        for key in primary_keys:
            # Nếu vế trái là tập con thực sự của khóa 
            # và vế phải chứa thuộc tính không khóa
            if left.issubset(key) and left != key:
                partial_deps.append((left, right))
                break
    
    return partial_deps

def is_in_2NF(primary_keys: List[Set[str]], 
              fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn 2 (2NF):
    - Thuộc tính không khoá phụ thuộc đầy đủ vào khoá
    """
    is_1nf, explanation_1nf = is_in_1NF(set(), primary_keys)
    if not is_1nf:
        return False, "Không đạt 2NF vì không thỏa mãn 1NF"
    
    partial_deps = find_partial_dependencies(primary_keys, fds)
    is_valid = len(partial_deps) == 0
    
    explanation = "Kiểm tra dạng chuẩn 2 (2NF):\n"
    explanation += "1. Đã thỏa mãn 1NF\n"
    
    if partial_deps:
        explanation += "2. Tồn tại các phụ thuộc bộ phận (thuộc tính không khóa phụ thuộc vào một phần của khóa):\n"
        for left, right in partial_deps:
            explanation += f"   - {', '.join(sorted(left))} → {', '.join(sorted(right))}\n"
            explanation += f"     (Vì {', '.join(sorted(right))} là thuộc tính không khóa và phụ thuộc vào {', '.join(sorted(left))} - một phần của khóa)\n"
    else:
        explanation += "2. Không tồn tại phụ thuộc bộ phận\n"
    
    return is_valid, explanation

def is_superkey(attrs: Set[str], primary_keys: List[Set[str]]) -> bool:
    """
    Kiểm tra xem một tập thuộc tính có phải là siêu khóa hay không
    """
    return any(key.issubset(attrs) for key in primary_keys)

def is_prime_attribute(attr: str, primary_keys: List[Set[str]]) -> bool:
    """
    Kiểm tra xem một thuộc tính có phải là thuộc tính nguyên tố hay không
    (thuộc tính nằm trong ít nhất một khóa)
    """
    return any(attr in key for key in primary_keys)

def check_3nf_violation(fd: Dict, primary_keys: List[Set[str]]) -> Tuple[bool, str]:
    """
    Kiểm tra vi phạm 3NF cho một phụ thuộc hàm.
    Trả về (is_violated, explanation)
    """
    left = fd['left']
    right = fd['right']
    
    # Điều kiện 1: X là siêu khóa
    if is_superkey(left, primary_keys):
        return False, "Vế trái là siêu khóa"
        
    # Điều kiện 2: Y là thuộc tính nguyên tố
    all_prime = all(is_prime_attribute(attr, primary_keys) for attr in right)
    if all_prime:
        return False, "Vế phải chứa thuộc tính khoá"
        
    # Vi phạm cả hai điều kiện
    return True, "Vi phạm 3NF: Vế trái không phải siêu khóa và vế phải không chứa thuộc tính của khoá"

def is_in_3NF(primary_keys: List[Set[str]], 
              fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn 3 (3NF):
    1. Phải là 2NF
    2. Với mọi phụ thuộc hàm X→Y, ít nhất một trong các điều kiện sau đúng:
       - X là siêu khóa
       - Y là thuộc tính của khoá
    """
    # Kiểm tra điều kiện 2NF trước
    is_2nf, explanation_2nf = is_in_2NF(primary_keys, fds)
    if not is_2nf:
        return False, "Không đạt 3NF vì không thỏa mãn 2NF"
    
    # Kiểm tra các vi phạm 3NF
    violations = []
    for fd in fds:
        is_violated, reason = check_3nf_violation(fd, primary_keys)
        if is_violated:
            violations.append((fd, reason))
    
    is_valid = len(violations) == 0
    
    # Tạo giải thích chi tiết
    explanation = "Kiểm tra dạng chuẩn 3 (3NF):\n"
    explanation += "1. Đã thỏa mãn 2NF\n"
    explanation += "2. Kiểm tra các phụ thuộc hàm X→Y:\n"
    
    if violations:
        explanation += "   Tồn tại các phụ thuộc hàm vi phạm 3NF:\n"
        for fd, reason in violations:
            explanation += f"   - {', '.join(sorted(fd['left']))} → {', '.join(sorted(fd['right']))}\n"
            explanation += f"     ({reason})\n"
    else:
        explanation += "   Mọi phụ thuộc hàm đều thỏa mãn ít nhất một trong hai điều kiện:\n"
        explanation += "   - X là siêu khóa, hoặc\n"
        explanation += "   - Y là thuộc của khoá\n"
    
    return is_valid, explanation
def is_in_BCNF(primary_keys: List[Set[str]], 
               fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn BCNF:
    - Phải là 3NF
    - Vế trái của mọi phụ thuộc hàm phải là siêu khóa
    """
    print("Primary keys:", primary_keys)  # Debug print
    
    is_3nf, explanation_3nf = is_in_3NF(primary_keys, fds)
    if not is_3nf:
        return False, "Không đạt BCNF vì không thỏa mãn 3NF"
    
    # Kiểm tra mọi phụ thuộc hàm
    non_bcnf_deps = []
    for fd in fds:
        left = fd['left']
        # Debug prints
        print(f"Checking FD: {left} → {fd['right']}")
        print(f"Left set: {left}")
        
        # Một tập thuộc tính là siêu khóa nếu nó chứa ít nhất một khóa
        is_superkey = any(key.issubset(left) for key in primary_keys)
        print(f"Is superkey: {is_superkey}")  # Debug print
        
        if not is_superkey:
            non_bcnf_deps.append(fd)
    
    is_valid = len(non_bcnf_deps) == 0
    explanation = "Kiểm tra dạng chuẩn BCNF:\n"
    explanation += "1. Đã thỏa mãn 3NF\n"
    
    if non_bcnf_deps:
        explanation += "2. Tồn tại các phụ thuộc hàm vi phạm BCNF:\n"
        for fd in non_bcnf_deps:
            explanation += f"   - {', '.join(sorted(fd['left']))} → {', '.join(sorted(fd['right']))}\n"
            explanation += "     (Vế trái không phải là siêu khóa)\n"
    else:
        explanation += "2. Mọi vế trái của phụ thuộc hàm đều là siêu khóa\n"
    
    return is_valid, explanation

def check_normal_forms(attributes: str, dependencies: str, primary_keys: List[Set[str]]) -> Dict:
    """
    Kiểm tra tất cả các dạng chuẩn
    """
    try:
        # Chuyển đổi dữ liệu đầu vào
        attrs = set(attr.strip() for attr in attributes.split(','))
        fds = []
        for dep in dependencies.split(','):
            left, right = dep.strip().split('->')
            fds.append({
                'left': set(left.strip()),
                'right': set(right.strip())
            })
        
        # Kiểm tra xem primary_keys có phải là list của sets không
        if not all(isinstance(key, set) for key in primary_keys):
            raise ValueError("Primary keys must be a list of sets")
            
        # Debug print
        print("Checking with:")
        print(f"Attributes: {attrs}")
        print(f"Dependencies: {fds}")
        print(f"Primary keys: {primary_keys}")
        
        # Kiểm tra từng dạng chuẩn
        is_1nf, explanation_1nf = is_in_1NF(attrs, primary_keys)
        is_2nf, explanation_2nf = is_in_2NF(primary_keys, fds)
        is_3nf, explanation_3nf = is_in_3NF(primary_keys, fds)
        is_bcnf, explanation_bcnf = is_in_BCNF(primary_keys, fds)
        
        return {
            'success': True,
            'normal_forms': {
                '1NF': {'valid': is_1nf, 'explanation': explanation_1nf},
                '2NF': {'valid': is_2nf, 'explanation': explanation_2nf},
                '3NF': {'valid': is_3nf, 'explanation': explanation_3nf},
                'BCNF': {'valid': is_bcnf, 'explanation': explanation_bcnf}
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
def decompose_2NF(primary_keys: List[Set[str]], 
                  fds: List[Dict],
                  attributes: Set[str]) -> List[Dict]:
    """
    Phân rã lược đồ sang dạng chuẩn 2:
    1. Tìm phụ thuộc bộ phận (vế trái không phải là siêu khóa)
    2. Tạo quan hệ riêng cho phụ thuộc bộ phận
    3. Tạo quan hệ chính với khóa và phụ thuộc không bộ phận
    """
    relations = []
    
    # Xác định thuộc tính không khóa
    all_keys = set().union(*primary_keys)
    
    # Tìm các phụ thuộc bộ phận và không bộ phận
    partial_deps = []
    non_partial_deps = []
    
    for fd in fds:
        left = fd['left']
        right = fd['right']
        
        # Kiểm tra siêu khóa
        is_partial = not any(key.issubset(left) and len(key) == len(left) for key in primary_keys)
        
        if is_partial:
            partial_deps.append(fd)
        else:
            non_partial_deps.append(fd)

    # Tạo quan hệ cho mỗi phụ thuộc bộ phận
    for i, fd in enumerate(partial_deps):
        new_relation = {
            'name': f'R_{i+1}',
            'attributes': fd['left'].union(fd['right']),
            'primary_key': fd['left'],
            'fds': [fd],
            'explanation': f'Tạo từ phụ thuộc bộ phận: {", ".join(sorted(fd["left"]))} → {", ".join(sorted(fd["right"]))}'
        }
        relations.append(new_relation)
    
    # Tạo quan hệ chính
    main_attrs = set()
    main_fds = []
    
    for fd in non_partial_deps:
        main_attrs.update(fd['left'])
        main_attrs.update(fd['right'])
        main_fds.append(fd)
    
    # Xác định khóa chính cho quan hệ chính
    main_key = set()
    for primary_key in primary_keys:
        if primary_key.issubset(main_attrs):
            main_key = primary_key
            break

    # Loại bỏ các phụ thuộc hàm không phù hợp với khóa mới
    final_main_fds = []
    for fd in main_fds:
        if fd['left'].issubset(main_key) or fd['left'] == main_key:
            final_main_fds.append(fd)
    
    main_relation = {
        'name': 'R_main',
        'attributes': main_attrs,
        'primary_key': main_key,
        'fds': final_main_fds,
        'explanation': 'Chứa khóa và các phụ thuộc không bộ phận'
    }
    relations.append(main_relation)

    return relations
def decompose_3NF(primary_keys: List[Set[str]], 
                 fds: List[Dict],
                 attributes: Set[str]) -> List[Dict]:
   relations = []
   used_attributes = set()
   
   # Gom nhóm FDs theo vế trái
   fd_groups = defaultdict(list)
   for fd in fds:
       left = frozenset(fd['left'])
       fd_groups[left].append(fd)
   
   # Xử lý từng nhóm FDs
   for left, group_fds in fd_groups.items():
       right = set().union(*[set(fd['right']) for fd in group_fds])
       
       # Kiểm tra relation đã tồn tại
       is_duplicate = any(
           rel['attributes'] == set(left).union(right) and
           rel['primary_key'] == set(left)
           for rel in relations
       )
       
       if not is_duplicate:
           new_fds = [fd for fd in group_fds 
                     if fd['left'].issubset(left) and fd['right'].issubset(right)]
           
           new_relation = {
               'name': f'R_{len(relations) + 1}',
               'attributes': set(left).union(right),
               'primary_key': set(left),
               'fds': new_fds
           }
           relations.append(new_relation)
           used_attributes.update(right)
   
   # Xử lý thuộc tính còn lại nếu cần
   remaining = attributes - used_attributes
   if remaining and not any(rel['attributes'].issuperset(primary_keys[0]) for rel in relations):
       key_relation = {
           'name': f'R_{len(relations) + 1}',
           'attributes': set(primary_keys[0]).union(remaining),
           'primary_key': set(primary_keys[0]),
           'fds': [fd for fd in fds if fd['left'].issubset(primary_keys[0])]
       }
       relations.append(key_relation)
   
   return relations

def decompose_BCNF(primary_keys: List[Set[str]], 
                   fds: List[Dict],
                   attributes: Set[str]) -> List[Dict]:
    """
    Phân rã lược đồ sang dạng BCNF:
    1. Duyệt qua từng phụ thuộc hàm theo thứ tự
    2. Tạo quan hệ riêng cho mỗi phụ thuộc hàm
    3. Đảm bảo bảo toàn thông tin và không mất phụ thuộc
    """
    # Kiểm tra nếu đã là BCNF
    is_bcnf, _ = is_in_BCNF(primary_keys, fds)
    if is_bcnf:
        return [{
            'name': 'R',
            'attributes': attributes,
            'primary_key': primary_keys[0],
            'fds': fds,
            'explanation': 'Lược đồ đã ở dạng BCNF'
        }]

    relations = []
    
    # Phân rã theo từng phụ thuộc hàm theo thứ tự ban đầu
    for i, fd in enumerate(fds):
        left = fd['left']
        right = fd['right']
        
        # Với mỗi phụ thuộc X->Y, tạo một quan hệ chứa X và Y
        rel_attrs = left.union(right)
        new_relation = {
            'name': f'R_{i}',
            'attributes': rel_attrs,
            'primary_key': left,  # Vế trái là khóa chính
            'fds': [fd],
            'explanation': f'Tạo từ phụ thuộc hàm: {", ".join(sorted(left))} → {", ".join(sorted(right))}'
        }
        relations.append(new_relation)

    # Loại bỏ các quan hệ trùng lặp (nếu có)
    unique_relations = []
    seen_attrs = set()
    
    for rel in relations:
        rel_attrs_key = frozenset(rel['attributes'])
        if rel_attrs_key not in seen_attrs:
            unique_relations.append(rel)
            seen_attrs.add(rel_attrs_key)

    return unique_relations

def compute_candidate_keys(attrs: Set[str], dependencies: List[Dict]) -> Set[Set[str]]:
    """
    Tính toán các khóa ứng viên cho một quan hệ
    """
    def is_superkey(attrs_subset: Set[str]) -> bool:
        closure = compute_closure(attrs_subset, dependencies)
        return attrs.issubset(closure)

    def compute_closure(attrs_subset: Set[str], deps: List[Dict]) -> Set[str]:
        closure = attrs_subset.copy()
        changed = True
        while changed:
            changed = False
            for fd in deps:
                if fd['left'].issubset(closure) and not fd['right'].issubset(closure):
                    closure.update(fd['right'])
                    changed = True
        return closure

    # Tìm tập thuộc tính không xuất hiện ở vế phải của phụ thuộc hàm
    rhs_attrs = set().union(*[fd['right'] for fd in dependencies])
    lhs_only_attrs = set().union(*[fd['left'] for fd in dependencies]) - rhs_attrs

    # Khởi tạo với tập thuộc tính không xuất hiện ở vế phải
    candidate_keys = {frozenset(lhs_only_attrs)} if lhs_only_attrs else {frozenset()}

    # Thêm các thuộc tính còn lại cho đến khi tìm được khóa
    remaining_attrs = attrs - lhs_only_attrs
    for attr in remaining_attrs:
        new_keys = set()
        for key in candidate_keys:
            new_key = set(key).union({attr})
            if is_superkey(new_key):
                new_keys.add(frozenset(new_key))
        if new_keys:
            candidate_keys = new_keys

    return {set(k) for k in candidate_keys}

def get_minimal_cover(fds: List[Dict]) -> List[Dict]:
    """
    Tìm tập phụ thuộc hàm tối thiểu (minimal cover)
    1. Chuẩn hóa vế phải
    2. Loại bỏ thuộc tính dư thừa ở vế trái
    3. Loại bỏ phụ thuộc hàm dư thừa
    """
    # Chuẩn hóa vế phải
    normalized_fds = []
    for fd in fds:
        for attr in fd['right']:
            normalized_fds.append({
                'left': fd['left'].copy(),
                'right': {attr}
            })
    
    # Loại bỏ thuộc tính dư thừa ở vế trái
    minimal_left_fds = []
    for fd in normalized_fds:
        minimal_left = fd['left'].copy()
        for attr in fd['left']:
            # Thử loại bỏ từng thuộc tính
            test_left = minimal_left - {attr}
            if test_left and is_dependent(test_left, fd['right'], normalized_fds):
                minimal_left = test_left
        minimal_left_fds.append({
            'left': minimal_left,
            'right': fd['right']
        })
    
    # Loại bỏ phụ thuộc hàm dư thừa
    result = []
    for i, fd in enumerate(minimal_left_fds):
        other_fds = minimal_left_fds[:i] + minimal_left_fds[i+1:]
        if not is_dependent(fd['left'], fd['right'], other_fds):
            result.append(fd)
    
    return result

def is_dependent(left: Set[str], right: Set[str], fds: List[Dict]) -> bool:
    """
    Kiểm tra xem right có phụ thuộc hàm vào left không
    sử dụng thuật toán tìm bao đóng
    """
    closure = left.copy()
    changed = True
    
    while changed:
        changed = False
        for fd in fds:
            if fd['left'].issubset(closure) and not fd['right'].issubset(closure):
                closure.update(fd['right'])
                changed = True
    
    return right.issubset(closure)

def normalize_to_nf(attributes: str, dependencies: str, target_nf: str) -> Dict:
    """
    Chuẩn hóa lược đồ lên dạng chuẩn mục tiêu
    """
    try:
        # Chuyển đổi dữ liệu đầu vào
        attrs = set(attr.strip() for attr in attributes.split(','))
        fds = []
        for dep in dependencies.split(','):
            left, right = dep.strip().split('->')
            fds.append({
                'left': set(left.strip()),
                'right': set(right.strip())
            })
            
        # Tìm khóa
        from .keys import process_keys
        keys_result = process_keys(attributes, dependencies)
        if not keys_result['success']:
            return keys_result
            
        # Xác định khóa chính
        if keys_result.get('skip_table', False):
            primary_keys = [set(keys_result['keys'][0].split(', '))]
        else:
            primary_keys = [
                set(row['k'].split(', '))
                for row in keys_result['table_data']
                if row['key'] == 'Yes'
            ]
            
        # Kiểm tra dạng chuẩn hiện tại
        is_2nf, _ = is_in_2NF(primary_keys, fds)
        is_3nf, _ = is_in_3NF(primary_keys, fds)
        is_bcnf, _ = is_in_BCNF(primary_keys, fds)
        
        current_nf = '1NF'
        if is_bcnf:
            current_nf = 'BCNF'
        elif is_3nf:
            current_nf = '3NF'
        elif is_2nf:
            current_nf = '2NF'
            
        # Thực hiện chuẩn hóa
        if target_nf == '2NF':
            if not is_2nf:
                relations = decompose_2NF(primary_keys, fds, attrs)
            else:
                relations = [{
                    'name': 'R',
                    'attributes': attrs,
                    'primary_key': primary_keys[0],
                    'fds': fds,
                    'explanation': 'Lược đồ đã ở dạng chuẩn 2NF'
                }]
        elif target_nf == '3NF':
            if not is_3nf:
                relations = decompose_3NF(primary_keys, fds, attrs)
            else:
                relations = [{
                    'name': 'R',
                    'attributes': attrs,
                    'primary_key': primary_keys[0],
                    'fds': fds,
                    'explanation': 'Lược đồ đã ở dạng chuẩn 3NF'
                }]
        elif target_nf == 'BCNF':
            if not is_bcnf:
                relations = decompose_BCNF(primary_keys, fds, attrs)
            else:
                relations = [{
                    'name': 'R',
                    'attributes': attrs,
                    'primary_key': primary_keys[0],
                    'fds': fds,
                    'explanation': 'Lược đồ đã ở dạng chuẩn BCNF'
                }]
        else:
            return {
                'success': False,
                'error': 'Dạng chuẩn không hợp lệ'
            }
            
        return {
            'success': True,
            'current_nf': current_nf,
            'relations': relations
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }