from flask import jsonify, request, render_template

def parse_dependencies(dependencies_str):
    """
    Phân tích chuỗi phụ thuộc hàm
    """
    dependencies = []
    for line in dependencies_str.split('\n'):
        line = line.strip()
        if line:
            try:
                left, right = line.split('->')
                left_attrs = set(attr.strip() for attr in left.split(','))
                right_attrs = set(attr.strip() for attr in right.split(','))
                dependencies.append({
                    'left': left_attrs,
                    'right': right_attrs
                })
            except ValueError:
                raise ValueError(f"Định dạng phụ thuộc không hợp lệ: {line}")
    return dependencies

def calculate_closure_with_steps(attributes, fds):
    """
    Tính bao đóng của tập thuộc tính với các bước chi tiết
    """
    closure = set(attributes)
    steps = [f"- Ban đầu: {', '.join(sorted(closure))}"]
    changed = True
    step_count = 1

    while changed:
        changed = False
        for fd in fds:
            left = set(fd['left'])
            right = set(fd['right'])

            if left.issubset(closure) and not right.issubset(closure):
                new_attrs = right - closure
                closure.update(right)
                changed = True
                steps.append(f"- Bước {step_count}: Áp dụng {' '.join(fd['left'])}→{' '.join(fd['right'])}")
                steps.append(f"  Thêm {', '.join(sorted(new_attrs))}")
                steps.append(f"  Kết quả: {', '.join(sorted(closure))}")
                step_count += 1

    if step_count == 1:
        steps.append("- Không có thuộc tính nào được thêm vào")

    return {
        'closure': closure,
        'steps': steps
    }

def check_armstrong(fd_to_check, original_fds):
    """
    Kiểm tra và chứng minh áp dụng hệ tiên đề Armstrong
    """
    result = {
        'is_valid': False,
        'steps': []
    }

    try:
        # Phân tích phụ thuộc hàm cần chứng minh
        left, right = fd_to_check.split('->')
        X = set(attr.strip() for attr in left.split(','))
        target = set(attr.strip() for attr in right.split(','))

        result['steps'].append("1. Phân tích phụ thuộc hàm cần chứng minh:")
        result['steps'].append(f"   X = {', '.join(sorted(X))} (vế trái)")
        result['steps'].append(f"   Y = {', '.join(sorted(target))} (vế phải)")

        # Tập kết quả hiện tại (bao gồm X và các thuộc tính đã suy ra)
        current_set = set(X)
        applied_rules = []

        # Lặp cho đến khi không thể áp dụng thêm luật nào
        while True:
            initial_size = len(current_set)
            
            # Thử áp dụng từng phụ thuộc hàm
            for fd in original_fds:
                left_side = set(fd['left'])
                right_side = set(fd['right'])

                # 1. Luật phản xạ
                if target.issubset(current_set):
                    result['steps'].append("\n2. Áp dụng luật phản xạ:")
                    result['steps'].append(f"   {', '.join(sorted(current_set))} → {', '.join(sorted(target))}")
                    result['is_valid'] = True
                    return result

                # 2. Luật tăng trưởng
                if left_side.issubset(current_set):
                    new_attrs = right_side - current_set
                    if new_attrs:
                        current_set.update(right_side)
                        result['steps'].append("\n3. Áp dụng luật tăng trưởng:")
                        result['steps'].append(f"   {', '.join(sorted(left_side))} → {', '.join(sorted(right_side))}")
                        result['steps'].append(f"   Thêm: {', '.join(sorted(new_attrs))}")
                        result['steps'].append(f"   Kết quả: {', '.join(sorted(current_set))}")

                # 3. Luật bắc cầu
                for fd2 in original_fds:
                    if right_side == set(fd2['left']) and set(fd2['right']) - current_set:
                        result['steps'].append("\n4. Áp dụng luật bắc cầu:")
                        result['steps'].append(f"   {', '.join(sorted(left_side))} → {', '.join(sorted(right_side))}")
                        result['steps'].append(f"   {', '.join(sorted(right_side))} → {', '.join(sorted(fd2['right']))}")
                        current_set.update(fd2['right'])
                        result['steps'].append(f"   Kết quả: {', '.join(sorted(current_set))}")

            # Kiểm tra xem có thêm thuộc tính mới không
            if len(current_set) == initial_size:
                break

        # Kiểm tra kết quả cuối cùng
        result['is_valid'] = target.issubset(current_set)
        result['steps'].append("\nKết luận:")
        if result['is_valid']:
            result['steps'].append(f"   → Phụ thuộc hàm {fd_to_check} được suy diễn từ F")
            result['steps'].append("   → Chứng minh thành công!")
        else:
            missing = target - current_set
            result['steps'].append(f"   → Không thể suy diễn {', '.join(sorted(missing))}")
            result['steps'].append("   → Chứng minh thất bại!")

    except Exception as e:
        result['steps'].append(f"Lỗi: {str(e)}")
        result['is_valid'] = False

    return result
