# check_preservation.py
def initialize_matrix(attributes, decomposition):
   matrix = []
   b_counter = 1  # Counter for b values
   
   for i, rel in enumerate(decomposition, 1):
       row = []
       for j, attr in enumerate(attributes, 1):
           if attr in rel:
               row.append(f'a{j}')
           else:
               row.append(f'b{b_counter}')
               b_counter += 1
       matrix.append(row)
   return matrix
def check_information_preservation(attributes, decomposition, dependencies):
   steps_matrices = []
   
   # B1: Khởi tạo ma trận
   matrix = initialize_matrix(attributes, decomposition)
   steps_matrices.append({
       'step': "**Bước 1: Khởi tạo ma trận**",
       'matrix': [row[:] for row in matrix]
   })

   # B2: Xét từng PTH
   for X, Y in dependencies:
       # So sánh và thay đổi ngay
       x_idx = [attributes.index(x) for x in X]
       y_idx = [attributes.index(y) for y in Y]
       
       changed = False
       for i in range(len(matrix)):
           for j in range(len(matrix)):
               if i != j and all(matrix[i][k] == matrix[j][k] for k in x_idx):
                   for y in y_idx:
                       if matrix[i][y] != matrix[j][y]:
                           val = matrix[i][y] if matrix[i][y].startswith('a') else matrix[j][y] 
                           matrix[i][y] = matrix[j][y] = val
                           changed = True
                           
       # Hiển thị sau khi thay đổi            
       steps_matrices.append({
           'step': f"**Xét phụ thuộc hàm {''.join(X)}->{''.join(Y)}**",
           'matrix': [row[:] for row in matrix]
       })
       
       # Kiểm tra hàng toàn a
       for row_idx, row in enumerate(matrix):
           if all(cell.startswith('a') for cell in row):
               steps_matrices.append({
                   'step': f"**Q{row_idx+1} chứa 1 dòng toàn aj**\n⟹ Phép tách bảo toàn thông tin",
                   'matrix': [row[:] for row in matrix]
               })
               return steps_matrices

   steps_matrices.append({
       'step': "**Không có dòng nào toàn aj**\n⟹ Phép tách không bảo toàn thông tin",
       'matrix': [row[:] for row in matrix]
   })
   return steps_matrices