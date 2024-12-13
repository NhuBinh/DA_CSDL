from flask import Blueprint, render_template, request, jsonify
from .logic.closure import closure
from .logic.keys import KeyFinder
from .logic.armstrong import check_armstrong

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Chuyển về trang keys làm trang chính
    return render_template('base.html')

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


@main.route('/api/keys', methods=['POST'])
def find_keys_api():
    """API endpoint xử lý tìm khóa và siêu khóa"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400

        attributes = data.get('Attributes', '').strip()
        dependencies = data.get('FunctionalDependencies', '').strip().replace(', ', ',')

        if not attributes or not dependencies:
            return jsonify({'error': 'Thiếu thông tin đầu vào'}), 400

        # Chuyển dấu phẩy thành dấu chấm phẩy cho phụ thuộc hàm
        dependencies = dependencies.replace(',', ';')

        finder = KeyFinder(attributes, dependencies)
        result = finder.find_keys()

        if not result['success']:
            return jsonify({'error': result['steps'][0]}), 400

        # Format kết quả trước khi trả về
        formatted_superkeys = [','.join(sk) for sk in result['superkeys']]
        formatted_keys = [','.join(k) for k in result['keys']]

        return jsonify({
            'superKeys': formatted_superkeys,
            'keys': formatted_keys,
            'steps': result['steps']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/keys')
def keys():  # Đổi tên function để tránh trùng với module
    """Route hiển thị trang tìm khóa"""
    return render_template('keys.html')

@main.route('/armstrong', methods=['GET', 'POST'])
def armstrong():
    """
    Endpoint xử lý kiểm tra Armstrong rule từ yêu cầu POST
    """
    if request.method == 'POST':
        try:
            # Nhận dữ liệu dưới dạng JSON
            data = request.get_json()
            dependencies = data.get('dependencies', [])
            rule_to_check = data.get('armstrong_rule', '').strip()

            if not dependencies or not rule_to_check:
                return jsonify(error="Vui lòng nhập đầy đủ thông tin"), 400

            # Chuyển đổi dependencies sang dạng danh sách dict
            fds = [
                {
                    'left': dep['left'],
                    'right': dep['right']
                }
                for dep in dependencies
            ]

            result = check_armstrong(rule_to_check, fds)

            return jsonify(result)

        except Exception as e:
            return jsonify(error=f"Lỗi: {str(e)}"), 500

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