from typing import Set, List, Dict, Tuple
from .closure import closure  # Import hàm tính bao đóng từ module closure

def split_right_side(F: List[Dict]) -> List[Dict]:
    """
    Bước 1: Tách vế phải của các phụ thuộc hàm
    Ví dụ: AB->CD thành AB->C và AB->D
    """
    result = []
    for fd in F:
        left = set(fd['left'])
        for attr in fd['right']:
            result.append({
                'left': left,
                'right': {attr}
            })
    return result

def closure(X: Set[str], F: List[Dict]) -> Set[str]:
    """
    Tính bao đóng của tập thuộc tính X
    """
    closure_set = set(X)  # Bắt đầu với tập X
    changed = True
    
    while changed:
        changed = False
        for fd in F:
            left = set(fd['left'])
            right = set(fd['right'])
            
            if left.issubset(closure_set) and not right.issubset(closure_set):
                closure_set.update(right)
                changed = True
    
    return closure_set

def remove_redundant_left(F: List[Dict]) -> Tuple[List[Dict], List[str]]:
    result = []
    steps = []

    for fd in F:
        left = set(fd['left'])
        right = set(fd['right'])
        
        # Nếu vế trái chỉ có 1 thuộc tính thì giữ nguyên
        if len(left) == 1:
            result.append({'left': left, 'right': right})
            steps.append(f"  {','.join(sorted(left))}->{','.join(sorted(right))}: Không xét vì vế trái chỉ có một thuộc tính")
            continue
            
        # Kiểm tra từng thuộc tính ở vế trái
        new_left = set(left)  # Copy để giữ tập ban đầu
        steps.append(f"\n  Xét {','.join(sorted(left))}->{','.join(sorted(right))}:")
        
        removed_attrs = set()
        for attr in left:
            # Tạo tập thuộc tính vế trái mới bằng cách bỏ đi attr
            test_left = left - {attr}
            
            # Tính bao đóng của tập mới
            test_closure = closure(test_left, F)
            
            # Kiểm tra xem có thể bỏ được attr không
            steps.append(f"    Nếu bỏ {attr}: {','.join(sorted(test_left))}+ = {','.join(sorted(test_closure))}")
            if right.issubset(test_closure):
                steps.append(f"    -> {','.join(sorted(test_closure))} chứa {','.join(sorted(right))} nên có thể bỏ {attr}")
                removed_attrs.add(attr)
            else:
                steps.append(f"    -> {','.join(sorted(test_closure))} không chứa {','.join(sorted(right))} nên không thể bỏ {attr}")
        
        # Cập nhật vế trái sau khi bỏ các thuộc tính dư thừa
        new_left = left - removed_attrs
        result.append({'left': new_left, 'right': right})
        
        if removed_attrs:
            steps.append(f"    Kết quả: {','.join(sorted(new_left))}->{','.join(sorted(right))}")
        else:
            steps.append("    Kết quả: Không bỏ được thuộc tính nào")
            
    return result, steps

def remove_redundant_dependencies(F: List[Dict]) -> Tuple[List[Dict], List[str]]:
    result = []
    steps = []
    current_F = F.copy()
    
    for i, fd in enumerate(F):
        F_prime = F[:i] + F[i+1:]
        left_str = ','.join(sorted(fd['left']))
        right_str = ','.join(sorted(fd['right']))
        
        steps.append(f"\n  Xét {left_str}->{right_str}:")
        left_closure = closure(fd['left'], F_prime)
        closure_str = ','.join(sorted(left_closure))
        
        if fd['right'].issubset(left_closure):
            steps.append(f"    Tính {left_str}+ = {closure_str}")
            steps.append(f"    -> {closure_str} có chứa {right_str} nên dư thừa")
            current_F.remove(fd)
            # Format F hiện tại
            deps_str = ', '.join(f"{','.join(sorted(d['left']))}->{','.join(sorted(d['right']))}" for d in current_F)
            steps.append(f"    F hiện tại = {{{deps_str}}}")
        else:
            steps.append(f"    Tính {left_str}+ = {closure_str}")
            steps.append(f"    -> {closure_str} không chứa {right_str} nên không dư thừa")
            result.append(fd)
        
    return result, steps
def find_minimal_cover(dependencies_str: str) -> Dict:
    try:
        F = []
        all_steps = []
        
        # Bước 0: Parse input
        all_steps.append("Bước 0: Tập phụ thuộc hàm ban đầu F:")
        for dep in dependencies_str.split(','):
            left, right = dep.strip().split('->')
            F.append({
                'left': set(left.strip()),
                'right': set(right.strip())
            })
            all_steps.append(f"  {left.strip()}->{right.strip()}")
        
        # Bước 1: Tách vế phải
        F1 = split_right_side(F)
        all_steps.append("\nBước 1: Tách vế phải của các phụ thuộc hàm:")
        for fd in F1:
            all_steps.append(f"  {','.join(sorted(fd['left']))}->{','.join(sorted(fd['right']))}")
        
        # Hiển thị F1
        deps_str = ', '.join(f"{','.join(sorted(fd['left']))}->{','.join(sorted(fd['right']))}" for fd in F1)
        all_steps.append(f"\nSau bước 1, ta có F1 = {{{deps_str}}}")
            
        # Bước 2: Loại bỏ thuộc tính dư thừa
        F2, step2_details = remove_redundant_left(F1)
        all_steps.append("\nBước 2: Bỏ các thuộc tính dư thừa ở vế trái:")
        all_steps.extend(step2_details)
        
        # Hiển thị F2
        deps_str = ', '.join(f"{','.join(sorted(fd['left']))}->{','.join(sorted(fd['right']))}" for fd in F2)
        all_steps.append(f"\nSau bước 2, ta có F2 = {{{deps_str}}}")
            
        # Bước 3: Loại bỏ phụ thuộc hàm dư thừa
        F3, step3_details = remove_redundant_dependencies(F2)
        all_steps.append("\nBước 3: Loại bỏ các phụ thuộc hàm dư thừa:")
        all_steps.extend(step3_details)
        
        # Format kết quả cuối cùng
        final_deps = []
        for fd in F3:
            left = ','.join(sorted(fd['left']))
            right = ','.join(sorted(fd['right']))
            final_deps.append(f"{left}->{right}")
            
        all_steps.append(f"\nPhủ tối thiểu Ftt = {{{'; '.join(final_deps)}}}")
        
        return {
            'success': True,
            'steps': all_steps,
            'minimal_cover': final_deps
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
