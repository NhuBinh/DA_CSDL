def closure(attributes, dependencies):
    """
    Tính bao đóng của một tập thuộc tính theo tập phụ thuộc hàm cho trước.
    
    Args:
        attributes (str): Chuỗi các thuộc tính phân cách bởi dấu phẩy
        dependencies (str): Chuỗi các phụ thuộc hàm phân cách bởi dấu chấm phẩy
        
    Returns:
        dict: Kết quả bao gồm:
            - closure (set): Tập bao đóng cuối cùng
            - steps (list): Các bước tính toán chi tiết
            - is_success (bool): True nếu tính toán thành công
    """
    try:
        # Khởi tạo kết quả
        result = {
            'closure': set(),
            'steps': [],
            'is_success': False
        }

        # Xử lý input attributes
        initial_attrs = set(attr.strip().upper() for attr in attributes.split(',') if attr.strip())
        if not initial_attrs:
            result['steps'].append("Lỗi: Tập thuộc tính đầu vào trống")
            return result

        # Xử lý input dependencies
        deps = []
        for dep in dependencies.split(';'):
            if '->' not in dep:
                continue
            lhs, rhs = dep.split('->')
            lhs_set = set(attr.strip().upper() for attr in lhs.split(',') if attr.strip())
            rhs_set = set(attr.strip().upper() for attr in rhs.split(',') if attr.strip())
            if lhs_set and rhs_set:  # Chỉ thêm nếu cả hai vế không rỗng
                deps.append((lhs_set, rhs_set))

        # Quá trình tính bao đóng
        closure_set = set(initial_attrs)
        result['steps'].append(f"Bước 0: Khởi tạo với {', '.join(sorted(closure_set))}")
        
        step_count = 1
        changed = True
        
        while changed:
            changed = False
            for lhs, rhs in deps:
                # Kiểm tra nếu có thể áp dụng phụ thuộc hàm
                if lhs.issubset(closure_set):
                    new_attrs = rhs - closure_set
                    if new_attrs:
                        closure_set.update(new_attrs)
                        result['steps'].append(
                            f"Bước {step_count}: Áp dụng {', '.join(sorted(lhs))} → {', '.join(sorted(rhs))}\n"
                            f"   Thêm vào: {', '.join(sorted(new_attrs))}\n"
                            f"   Kết quả: {', '.join(sorted(closure_set))}"
                        )
                        step_count += 1
                        changed = True

        if step_count == 1:
            result['steps'].append("Không có thuộc tính nào được thêm vào bao đóng")

        result['closure'] = closure_set
        result['is_success'] = True
        result['steps'].append(f"\nBao đóng cuối cùng: {', '.join(sorted(closure_set))}")

        return result

    except Exception as e:
        return {
            'closure': set(),
            'steps': [f"Lỗi xử lý: {str(e)}"],
            'is_success': False
        }

def format_closure_result(result):
    """
    Format kết quả bao đóng để hiển thị
    """
    if not result['is_success']:
        return "Lỗi khi tính bao đóng:\n" + "\n".join(result['steps'])
    
    return "\n".join(result['steps'])