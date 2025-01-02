def closure(attributes, dependencies):
    """
    Tính bao đóng của một tập thuộc tính theo tập phụ thuộc hàm cho trước.
    """
    try:
        result = {
            'closure': set(),
            'steps': [],
            'is_success': False
        }

        # Xử lý input attributes
        attributes = attributes.strip().rstrip(',')
        initial_attrs = set(attr.strip().upper() for attr in attributes.split(',') if attr.strip())
        if not initial_attrs:
            result['steps'].append("Lỗi: Tập thuộc tính đầu vào trống")
            return result

        # Xử lý input dependencies
        dependencies = dependencies.strip().rstrip(',')
        deps = []
        for dep in dependencies.split(','):
            dep = dep.strip()
            if '->' not in dep:
                continue
                
            lhs, rhs = map(str.strip, dep.split('->'))
            
            # Xử lý vế trái có thể chứa nhiều thuộc tính
            lhs_attrs = set()
            for attr in lhs:
                if attr.isalpha():
                    lhs_attrs.add(attr.upper())
            
            # Xử lý vế phải có thể chứa nhiều thuộc tính
            rhs_attrs = set()
            for attr in rhs:
                if attr.isalpha():
                    rhs_attrs.add(attr.upper())
            
            if lhs_attrs and rhs_attrs:
                deps.append((lhs_attrs, rhs_attrs))

        # Quá trình tính bao đóng
        closure_set = set(initial_attrs)
        result['steps'].append(f"Bước 0: Khởi tạo với {', '.join(sorted(closure_set))}")
        
        step_count = 1
        changed = True
        
        while changed:
            changed = False
            for lhs, rhs in deps:
                if lhs.issubset(closure_set):
                    new_attrs = rhs - closure_set
                    if new_attrs:
                        old_closure = set(closure_set)
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
        result['steps'].append(f"Bao đóng cuối cùng: {', '.join(sorted(closure_set))}")

        return result

    except Exception as e:
        return {
            'closure': set(),
            'steps': [f"Lỗi xử lý: {str(e)}"],
            'is_success': False
        }