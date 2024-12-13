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
    Kiểm tra và chứng minh Armstrong rule cho phụ thuộc hàm cần kiểm tra
    """
    result = {
        'is_valid': False,
        'steps': [],
        'closure_steps': []
    }

    try:
        # Bước 1: Tách vế trái và vế phải của phụ thuộc cần kiểm tra
        left, right = fd_to_check.split('->')
        left_attrs = set(left.strip().split(','))
        right_attrs = set(right.strip().split(','))

        result['steps'].append(f"1. Phân tích phụ thuộc cần chứng minh: {fd_to_check}")
        result['steps'].append(f"   - Vế trái (α): {', '.join(sorted(left_attrs))}")
        result['steps'].append(f"   - Vế phải (β): {', '.join(sorted(right_attrs))}")

        # Bước 2: Tính bao đóng của vế trái
        closure_result = calculate_closure_with_steps(left_attrs, original_fds)
        result['closure_steps'] = closure_result['steps']
        final_closure = closure_result['closure']

        result['steps'].append(f"\n2. Tính bao đóng của {', '.join(sorted(left_attrs))}+:")
        for step in closure_result['steps']:
            result['steps'].append(f"   {step}")

        # Bước 3: Kiểm tra kết quả
        is_valid = right_attrs.issubset(final_closure)
        result['is_valid'] = is_valid

        if is_valid:
            result['steps'].append(f"\n3. Kết luận: {', '.join(sorted(right_attrs))} ⊆ {', '.join(sorted(final_closure))}")
            result['steps'].append("   => Phụ thuộc hàm này có thể suy diễn từ tập F theo quy tắc Armstrong")
        else:
            missing_attrs = right_attrs - final_closure
            result['steps'].append(f"\n3. Kết luận: Không thể suy diễn vì {', '.join(sorted(missing_attrs))} không thuộc bao đóng")
            result['steps'].append("   => Phụ thuộc hàm này KHÔNG thể suy diễn từ tập F theo quy tắc Armstrong")

    except Exception as e:
        result['steps'].append(f"Lỗi xử lý: {str(e)}")
        result['is_valid'] = False

    return result
