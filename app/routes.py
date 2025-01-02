
from flask import Blueprint, flash, redirect, render_template, request, jsonify, url_for

from app.logic.check_preservation import check_information_preservation
from app.logic.fd_analyzer import FunctionalDependency

from .logic.keys import process_keys  # Chỉ import process_keys
from .logic.closure import closure
from .logic.armstrong import check_armstrong

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('base.html')

@main.route('/keys')
def find_keys_page():
    return render_template('keys.html')

@main.route('/api/keys', methods=['POST'])
def find_keys_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400

        attributes = data.get('Attributes', '').strip()
        dependencies = data.get('FunctionalDependencies', '').strip()

        if not attributes or not dependencies:
            return jsonify({
                'error': 'Vui lòng nhập đầy đủ tập thuộc tính và phụ thuộc hàm'
            }), 400

        # Sử dụng hàm process_keys
        result = process_keys(attributes, dependencies)
        
        if not result['success']:
            return jsonify({
                'error': f"Lỗi xử lý: {result.get('error', 'Không xác định')}"
            }), 400

        return jsonify({
            'success': True,
            'TN': result['TN'],
            'TG': result['TG'],
            'skip_table': result.get('skip_table', False),
            'keys': result.get('keys', []),
            'table_data': result.get('table_data', []),
            'stop_reason': result.get('stop_reason', None)  # Thêm lý do dừng
        })

    except Exception as e:
        return jsonify({
            'error': f'Lỗi server: {str(e)}'
        }), 500
@main.route('/closure', methods=['GET', 'POST'])
def find_closure():  # Giữ tên route là 'closure' nhưng tên function là 'find_closure'
    if request.method == 'POST':
        try:
            attributes = request.form.get('attributes', '').strip()
            dependencies = request.form.get('dependencies', '').strip()
            
            if not attributes or not dependencies:
                return render_template('closure.html', 
                                     error="Vui lòng nhập đầy đủ thông tin")

            result = closure(attributes, dependencies)
            
            return render_template('closure.html', 
                                 result=result,
                                 attributes=attributes,
                                 dependencies=dependencies)
                                 
        except Exception as e:
            return render_template('closure.html', 
                                 error=f"Lỗi: {str(e)}")
            
    return render_template('closure.html')

@main.route('/armstrong', methods=['GET', 'POST'])
def armstrong():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Không có dữ liệu được gửi"}), 400

            dependencies = data.get('dependencies', [])
            rule_to_check = data.get('armstrong_rule', '').strip()

            if not dependencies or not rule_to_check:
                return jsonify({
                    "error": "Vui lòng nhập đầy đủ thông tin"
                }), 400

            fds = [{
                'left': [x.strip() for x in dep['left']],
                'right': [x.strip() for x in dep['right']]
            } for dep in dependencies]

            result = check_armstrong(rule_to_check, fds)
            return jsonify(result)

        except Exception as e:
            return jsonify({"error": f"Lỗi xử lý: {str(e)}"}), 500

    return render_template('armstrong.html')

@main.app_template_filter('format_closure_result')
def format_closure_result(result):
    if not result or not isinstance(result, dict):
        return "Không có kết quả"
    
    # Format từng phần của kết quả
    html = '<div class="result-container">'
    
    # Hiển thị bao đóng
    if 'closure' in result:
        closure_set = ', '.join(sorted(result['closure']))
        html += f'<div class="closure-set mb-3">'
        html += f'<h5 class="text-success"><i class="fas fa-check-circle me-2"></i>Bao đóng cuối cùng:</h5>'
        html += f'<p class="ms-4 fw-bold">{closure_set}</p>'
        html += '</div>'

    # Hiển thị các bước
    if 'steps' in result and result['steps']:
        html += '<div class="steps-list">'
        html += '<h5 class="text-primary mb-3"><i class="fas fa-list-ol me-2"></i>Các bước thực hiện:</h5>'
        for step in result['steps']:
            html += f'<div class="step-item ms-4 mb-2">{step}</div>'
        html += '</div>'
    
    html += '</div>'
    return html
@main.route('/normalization')
def normalization_page():
    return render_template('normalization.html')
@main.route('/api/normalization', methods=['POST'])
def check_normalization_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
            
        attributes = data.get('attributes', '').strip()
        dependencies = data.get('dependencies', '').strip()
        
        if not attributes or not dependencies:
            return jsonify({
                'error': 'Vui lòng nhập đầy đủ thông tin'
            }), 400
            
        # Tìm khóa trước
        from .logic.keys import process_keys
        keys_result = process_keys(attributes, dependencies)
        
        if not keys_result['success']:
            return jsonify({
                'error': f"Lỗi xử lý khóa: {keys_result.get('error', 'Không xác định')}"
            }), 400
            
        # Chuyển đổi kết quả khóa thành set
        primary_keys = []
        if keys_result.get('skip_table', False):
            # Chuyển đổi string key thành set
            key_str = keys_result['keys'][0]
            primary_keys = [set(k.strip() for k in key_str.split(','))]
        else:
            # Chuyển đổi mỗi key string thành set
            table_data = keys_result['table_data']
            primary_keys = [
                set(k.strip() for k in row['k'].split(','))
                for row in table_data 
                if row['key'] == 'Yes'
            ]
            
        # Kiểm tra dạng chuẩn với các khóa đã chuyển đổi
        from .logic.normalization import check_normal_forms
        result = check_normal_forms(attributes, dependencies, primary_keys)
        
        if not result['success']:
            return jsonify({
                'error': f"Lỗi xử lý dạng chuẩn: {result.get('error', 'Không xác định')}"
            }), 400
        
        # Bổ sung thông tin về khóa vào kết quả
        result['keys_info'] = {
            'TN': keys_result.get('TN', ''),
            'TG': keys_result.get('TG', ''),
            'primary_keys': [','.join(sorted(k)) for k in primary_keys]
        }
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Lỗi server: {str(e)}'
        }), 500
    
@main.route('/minimal-cover')
def minimal_cover_page():
    return render_template('minimal_cover.html')

@main.route('/api/minimal-cover', methods=['POST'])
def find_minimal_cover_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
            
        dependencies = data.get('dependencies', '').strip()
        
        if not dependencies:
            return jsonify({
                'error': 'Vui lòng nhập tập phụ thuộc hàm'
            }), 400
            
        # Sử dụng hàm find_minimal_cover từ module minimal_cover
        from .logic.minimal_cover import find_minimal_cover
        result = find_minimal_cover(dependencies)
        
        if not result['success']:
            return jsonify({
                'error': f"Lỗi xử lý: {result.get('error', 'Không xác định')}"
            }), 400
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Lỗi server: {str(e)}'
        }), 500

@main.route('/info-preservation')
def info_preservation():
    return render_template('check_preservation.html')
@main.route('/check-preservation', methods=['GET', 'POST']) 
def check_preservation():
    if request.method == 'GET':
        return render_template('check_preservation.html')
        
    if request.json.get('example'):
        return jsonify({
            'attributes': 'ABCDEG',
            'decomposition': 'DG,CA,CDE,AB',
            'dependencies': 'D->G,C->A,CD->E,A->B'
        })

    try:
        data = request.get_json()
        if not all(key in data for key in ['attributes', 'decomposition', 'dependencies']):
            return jsonify({'error': 'Thiếu thông tin đầu vào'}), 400
            
        attrs = list(data['attributes'].strip())
        decomp = [list(r.strip()) for r in data['decomposition'].split(',')]
        deps = []
        
        for dep in data['dependencies'].split(','):
            left, right = dep.strip().split('->')
            deps.append((list(left.strip()), list(right.strip())))

        steps_matrices = check_information_preservation(attrs, decomp, deps)
        return jsonify(steps_matrices)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/dependency_preservation', methods=['GET', 'POST'])
def dependency_preservation():
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            attributes = request.form.get('attributes', '').strip()
            dependencies = request.form.get('dependencies', '').strip()
            decomposition = request.form.get('decomposition', '').strip()

            # Kiểm tra dữ liệu đầu vào không được trống
            if not attributes or not dependencies or not decomposition:
                flash('Vui lòng điền đầy đủ thông tin', 'danger')
                return redirect(url_for('main.dependency_preservation'))

            # Validate attributes
            attr_set = set(attr.strip() for attr in attributes.split(',') if attr.strip())
            
            # Validate dependencies
            for dep in dependencies.split('\n'):
                if not dep.strip():
                    continue
                if '->' not in dep:
                    flash(f'Lỗi định dạng phụ thuộc hàm: {dep}', 'danger')
                    return redirect(url_for('main.dependency_preservation'))
                
                left, right = dep.split('->')
                left_attrs = set(attr.strip() for attr in left.split(',') if attr.strip())
                right_attrs = set(attr.strip() for attr in right.split(',') if attr.strip())
                
                # Kiểm tra các thuộc tính có tồn tại trong tập thuộc tính không
                invalid_left = left_attrs - attr_set
                invalid_right = right_attrs - attr_set
                
                if invalid_left:
                    flash(f'Thuộc tính không hợp lệ ở vế trái: {", ".join(invalid_left)}', 'danger')
                    return redirect(url_for('main.dependency_preservation'))
                if invalid_right:
                    flash(f'Thuộc tính không hợp lệ ở vế phải: {", ".join(invalid_right)}', 'danger')
                    return redirect(url_for('main.dependency_preservation'))

            # Validate decomposition
            for rel in decomposition.split('\n'):
                if not rel.strip():
                    continue
                rel_attrs = set(attr.strip() for attr in rel.split(',') if attr.strip())
                invalid_attrs = rel_attrs - attr_set
                if invalid_attrs:
                    flash(f'Thuộc tính không hợp lệ trong lược đồ: {", ".join(invalid_attrs)}', 'danger')
                    return redirect(url_for('main.dependency_preservation'))

            # Thực hiện kiểm tra bảo toàn phụ thuộc
            is_preserved, message, steps = FunctionalDependency.check_preservation(dependencies, decomposition)
            
            if is_preserved:
                flash(message, 'success')
            else:
                flash(message, 'danger')
            
            return render_template('dependency_preservation.html',
                                attributes=attributes,
                                dependencies=dependencies,
                                decomposition=decomposition,
                                steps=steps)

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('main.dependency_preservation'))

    # GET request
    return render_template('dependency_preservation.html')


