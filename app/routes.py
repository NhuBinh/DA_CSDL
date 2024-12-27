
from flask import Blueprint, flash, redirect, render_template, request, jsonify

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
@main.route('/api/normalize', methods=['POST'])
def normalize_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
            
        attributes = data.get('attributes', '').strip()
        dependencies = data.get('dependencies', '').strip()
        target_nf = data.get('target_nf')
        
        if not attributes or not dependencies or not target_nf:
            return jsonify({
                'error': 'Vui lòng nhập đầy đủ thông tin'
            }), 400
        
        # Import hàm normalize từ module normalization    
        from .logic.normalization import normalize_to_nf
        result = normalize_to_nf(attributes, dependencies, target_nf)
        
        if not result['success']:
            return jsonify({
                'error': f"Lỗi xử lý: {result.get('error', 'Không xác định')}"
            }), 400
        
        # Chuyển đổi set thành list trong kết quả
        normalized_relations = []
        for relation in result['relations']:
            normalized_relation = {
                'name': relation['name'],
                'attributes': list(relation['attributes']),  # Chuyển set thành list
                'primary_key': list(relation['primary_key']),  # Chuyển set thành list
                'fds': [
                    {
                        'left': list(fd['left']),  # Chuyển set thành list
                        'right': list(fd['right'])  # Chuyển set thành list
                    }
                    for fd in relation['fds']
                ]
            }
            normalized_relations.append(normalized_relation)
        
        return jsonify({
            'success': True,
            'current_nf': result['current_nf'],
            'relations': normalized_relations
        })
        
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
            attributes = request.form.get('attributes', '').strip()
            dependencies = request.form.get('dependencies', '').strip()
            decomposition = request.form.get('decomposition', '').strip()

            if not all([attributes, dependencies, decomposition]):
                flash('Vui lòng điền đầy đủ thông tin', 'warning')
                return redirect('/dependency_preservation')

            # Process attributes
            attr_list = set(attr.strip() for attr in attributes.split(','))

            # Process dependencies
            fd_list = []
            for dep in dependencies.splitlines():
                if not dep.strip():
                    continue
                try:
                    left_str, right_str = dep.strip().split('->')
                    left = [x.strip() for x in left_str.split(',')]
                    right = right_str.strip()
                    
                    if not (set(left).issubset(attr_list) and right in attr_list):
                        raise ValueError(f"Thuộc tính không tồn tại trong lược đồ: {dep}")
                        
                    fd_list.append(FunctionalDependency(left, right))
                except Exception as e:
                    flash(f'Lỗi phụ thuộc hàm không hợp lệ: {dep}', 'danger')
                    return redirect('/dependency_preservation')

            # Process decomposition
            decomp_list = []
            for dec in decomposition.splitlines():
                if not dec.strip():
                    continue
                decomp_attrs = [x.strip() for x in dec.split(',')]
                
                if not set(decomp_attrs).issubset(attr_list):
                    flash(f'Lược đồ con chứa thuộc tính không tồn tại: {dec}', 'danger')
                    return redirect('/dependency_preservation')
                    
                decomp_list.append(decomp_attrs)

            # Check preservation with detailed steps
            is_preserved, message, steps = FunctionalDependency.check_preservation(fd_list, decomp_list)
            
            alert_type = 'success' if is_preserved else 'warning'
            flash(message, alert_type)
            
            return render_template('dependency_preservation.html', 
                                 attributes=attributes,
                                 dependencies=dependencies,
                                 decomposition=decomposition,
                                 steps=steps)

        except Exception as e:
            flash(f'Lỗi xử lý: {str(e)}', 'danger')
            return redirect('/dependency_preservation')

    return render_template('dependency_preservation.html')


