from typing import Set, List, Dict, Tuple

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
        explanation += f"- Có khóa chính: {', '.join([', '.join(sorted(k)) for k in primary_keys])}\n"
    
    return is_valid, explanation

def find_partial_dependencies(primary_keys: List[Set[str]], 
                            fds: List[Dict]) -> List[Tuple[Set[str], Set[str]]]:
    """
    Tìm các phụ thuộc bộ phận (một phần của khóa -> thuộc tính không khóa)
    """
    partial_deps = []
    non_prime_attributes = set()
    
    # Xác định các thuộc tính không khóa
    all_attributes = set()
    for fd in fds:
        all_attributes.update(fd['left'], fd['right'])
    
    for key in primary_keys:
        for fd in fds:
            left = set(fd['left'])
            right = set(fd['right'])
            
            # Kiểm tra nếu vế trái là một phần của khóa
            if left.issubset(key) and left != key:
                non_key_attrs = right - key
                if non_key_attrs:
                    partial_deps.append((left, non_key_attrs))
    
    return partial_deps

def find_transitive_dependencies(primary_keys: List[Set[str]], 
                               fds: List[Dict]) -> List[Tuple[Set[str], Set[str], Set[str]]]:
    """
    Tìm các phụ thuộc bắc cầu (X -> Y -> Z, với X là khóa)
    """
    transitive_deps = []
    
    # Xác định các thuộc tính không khóa
    all_attributes = set()
    for fd in fds:
        all_attributes.update(fd['left'], fd['right'])
    
    non_prime_attributes = all_attributes - set.union(*primary_keys)
    
    for fd1 in fds:
        left1 = set(fd1['left'])
        right1 = set(fd1['right'])
        
        for fd2 in fds:
            left2 = set(fd2['left'])
            right2 = set(fd2['right'])
            
            # Kiểm tra phụ thuộc bắc cầu
            if (right1 == left2 and 
                left1 in primary_keys and 
                right2.issubset(non_prime_attributes)):
                transitive_deps.append((left1, right1, right2))
    
    return transitive_deps

def is_in_2NF(primary_keys: List[Set[str]], 
              fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn 2 (2NF):
    - Phải là 1NF
    - Không có phụ thuộc bộ phận
    """
    is_1nf, explanation_1nf = is_in_1NF(set(), primary_keys)
    if not is_1nf:
        return False, "Không đạt 2NF vì không thỏa mãn 1NF"
    
    partial_deps = find_partial_dependencies(primary_keys, fds)
    is_valid = len(partial_deps) == 0
    
    explanation = "Kiểm tra dạng chuẩn 2 (2NF):\n"
    explanation += "1. Đã thỏa mãn 1NF\n"
    
    if partial_deps:
        explanation += "2. Tồn tại các phụ thuộc bộ phận:\n"
        for left, right in partial_deps:
            explanation += f"   - {', '.join(sorted(left))} → {', '.join(sorted(right))}\n"
    else:
        explanation += "2. Không tồn tại phụ thuộc bộ phận\n"
    
    return is_valid, explanation

def is_in_3NF(primary_keys: List[Set[str]], 
              fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn 3 (3NF):
    - Phải là 2NF
    - Không có phụ thuộc bắc cầu
    """
    is_2nf, explanation_2nf = is_in_2NF(primary_keys, fds)
    if not is_2nf:
        return False, "Không đạt 3NF vì không thỏa mãn 2NF"
    
    transitive_deps = find_transitive_dependencies(primary_keys, fds)
    is_valid = len(transitive_deps) == 0
    
    explanation = "Kiểm tra dạng chuẩn 3 (3NF):\n"
    explanation += "1. Đã thỏa mãn 2NF\n"
    
    if transitive_deps:
        explanation += "2. Tồn tại các phụ thuộc bắc cầu:\n"
        for key, middle, end in transitive_deps:
            explanation += f"   - {', '.join(sorted(key))} → {', '.join(sorted(middle))} → {', '.join(sorted(end))}\n"
    else:
        explanation += "2. Không tồn tại phụ thuộc bắc cầu\n"
    
    return is_valid, explanation

def is_in_BCNF(primary_keys: List[Set[str]], 
               fds: List[Dict]) -> Tuple[bool, str]:
    """
    Kiểm tra điều kiện dạng chuẩn BCNF:
    - Phải là 3NF
    - Vế trái của mọi phụ thuộc hàm phải là siêu khóa
    """
    is_3nf, explanation_3nf = is_in_3NF(primary_keys, fds)
    if not is_3nf:
        return False, "Không đạt BCNF vì không thỏa mãn 3NF"
    
    # Kiểm tra mọi phụ thuộc hàm
    non_bcnf_deps = []
    for fd in fds:
        left = set(fd['left'])
        is_superkey = False
        for key in primary_keys:
            if key.issubset(left):
                is_superkey = True
                break
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

def check_normal_forms(attributes: str, dependencies: str, primary_keys: List[str]) -> Dict:
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
        
        # Chuyển đổi khóa chính
        keys = [set(key.strip()) for key in primary_keys]
        
        # Kiểm tra từng dạng chuẩn
        is_1nf, explanation_1nf = is_in_1NF(attrs, keys)
        is_2nf, explanation_2nf = is_in_2NF(keys, fds)
        is_3nf, explanation_3nf = is_in_3NF(keys, fds)
        is_bcnf, explanation_bcnf = is_in_BCNF(keys, fds)
        
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
    Phân rã lược đồ sang dạng chuẩn 2
    """
    relations = []
    processed_attrs = set()
    
    # Tìm các phụ thuộc bộ phận
    partial_deps = find_partial_dependencies(primary_keys, fds)
    
    if not partial_deps:
        # Nếu không có phụ thuộc bộ phận, giữ nguyên lược đồ
        relations.append({
            'name': 'R',
            'attributes': attributes,
            'primary_key': primary_keys[0],
            'fds': fds
        })
        return relations
        
    # Xử lý từng phụ thuộc bộ phận
    for left, right in partial_deps:
        # Tạo quan hệ mới cho phụ thuộc bộ phận
        new_relation = {
            'name': f'R_{len(relations) + 1}',
            'attributes': left.union(right),
            'primary_key': left,
            'fds': [{'left': left, 'right': right}]
        }
        relations.append(new_relation)
        processed_attrs.update(right)
    
    # Tạo quan hệ cho các thuộc tính còn lại
    remaining_attrs = attributes - processed_attrs
    if remaining_attrs:
        main_relation = {
            'name': 'R_main',
            'attributes': remaining_attrs,
            'primary_key': primary_keys[0],
            'fds': [fd for fd in fds if not any(
                fd['left'] == p_left and fd['right'] == p_right 
                for p_left, p_right in partial_deps
            )]
        }
        relations.append(main_relation)
    
    return relations

def decompose_3NF(primary_keys: List[Set[str]], 
                  fds: List[Dict],
                  attributes: Set[str]) -> List[Dict]:
    """
    Phân rã lược đồ sang dạng chuẩn 3
    """
    relations = []
    processed_attrs = set()
    
    # Tìm các phụ thuộc bắc cầu
    transitive_deps = find_transitive_dependencies(primary_keys, fds)
    
    if not transitive_deps:
        # Nếu không có phụ thuộc bắc cầu, giữ nguyên lược đồ
        relations.append({
            'name': 'R',
            'attributes': attributes,
            'primary_key': primary_keys[0],
            'fds': fds
        })
        return relations
    
    # Xử lý từng phụ thuộc bắc cầu
    for key, middle, end in transitive_deps:
        # Tạo quan hệ cho phụ thuộc Y -> Z
        new_relation = {
            'name': f'R_{len(relations) + 1}',
            'attributes': middle.union(end),
            'primary_key': middle,
            'fds': [{'left': middle, 'right': end}]
        }
        relations.append(new_relation)
        processed_attrs.update(end)
    
    # Tạo quan hệ cho các thuộc tính còn lại
    remaining_attrs = attributes - processed_attrs
    if remaining_attrs:
        main_relation = {
            'name': 'R_main',
            'attributes': remaining_attrs,
            'primary_key': primary_keys[0],
            'fds': [fd for fd in fds if not any(
                fd['left'] == t_middle and fd['right'] == t_end
                for _, t_middle, t_end in transitive_deps
            )]
        }
        relations.append(main_relation)
    
    return relations

def decompose_BCNF(primary_keys: List[Set[str]], 
                   fds: List[Dict],
                   attributes: Set[str]) -> List[Dict]:
    """
    Phân rã lược đồ sang dạng BCNF
    """
    relations = []
    
    # Tìm các phụ thuộc vi phạm BCNF
    non_bcnf_deps = []
    for fd in fds:
        left = fd['left']
        is_superkey = False
        for key in primary_keys:
            if key.issubset(left):
                is_superkey = True
                break
        if not is_superkey:
            non_bcnf_deps.append(fd)
    
    if not non_bcnf_deps:
        # Nếu không có vi phạm BCNF, giữ nguyên lược đồ
        relations.append({
            'name': 'R',
            'attributes': attributes,
            'primary_key': primary_keys[0],
            'fds': fds
        })
        return relations
    
    # Phân rã theo từng phụ thuộc vi phạm BCNF
    for fd in non_bcnf_deps:
        left = fd['left']
        right = fd['right']
        
        # Tạo quan hệ mới
        new_relation = {
            'name': f'R_{len(relations) + 1}',
            'attributes': left.union(right),
            'primary_key': left,
            'fds': [{'left': left, 'right': right}]
        }
        relations.append(new_relation)
    
    # Tạo quan hệ cho các thuộc tính còn lại
    remaining_attrs = attributes - set().union(*[r['attributes'] for r in relations])
    if remaining_attrs:
        main_relation = {
            'name': 'R_main',
            'attributes': remaining_attrs,
            'primary_key': primary_keys[0],
            'fds': [fd for fd in fds if fd not in non_bcnf_deps]
        }
        relations.append(main_relation)
    
    return relations


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
        relations = []
        if target_nf == '2NF' and not is_2nf:
            relations = decompose_2NF(primary_keys, fds, attrs)
        elif target_nf == '3NF' and not is_3nf:
            if not is_2nf:
                relations = decompose_2NF(primary_keys, fds, attrs)
            relations.extend(decompose_3NF(primary_keys, fds, attrs))
        elif target_nf == 'BCNF' and not is_bcnf:
            if not is_2nf:
                relations = decompose_2NF(primary_keys, fds, attrs)
            if not is_3nf:
                relations.extend(decompose_3NF(primary_keys, fds, attrs))
            relations.extend(decompose_BCNF(primary_keys, fds, attrs))
            
        return {
            'success': True,
            'current_nf': current_nf,
            'relations': relations or [{
                'name': 'R',
                'attributes': attrs,
                'primary_key': primary_keys[0],
                'fds': fds
            }]
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }