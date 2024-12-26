from flask import jsonify, request, render_template
from itertools import combinations

class FunctionalDependency:
    def __init__(self, determinant, dependent):
        self.determinant = frozenset(determinant)
        self.dependent = frozenset(dependent)
    
    def __str__(self):
        return f"{''.join(sorted(self.determinant))} → {''.join(sorted(self.dependent))}"
    
    def __eq__(self, other):
        return (self.determinant == other.determinant and 
                self.dependent == other.dependent)
    
    def __hash__(self):
        return hash((self.determinant, self.dependent))

def get_subsets(s, size=None):
    s = set(s)
    if size is None:
        sizes = range(len(s) + 1)
    else:
        sizes = [size]
    return {frozenset(combo) for n in sizes for combo in combinations(s, n)}

def apply_reflexivity(attributes):
    results = set()
    for i in range(len(attributes) + 1):
        for subset in get_subsets(attributes, i):
            results.add((FunctionalDependency(attributes, subset), None))
    return results

def apply_augmentation(fd, all_attributes):
    results = set()
    for attrs in get_subsets(all_attributes, None):
        new_det = fd.determinant.union(attrs)
        new_dep = fd.dependent.union(attrs)
        results.add((FunctionalDependency(new_det, new_dep), attrs))
    return results

def apply_transitivity(fd1, fd2):
    if fd1.dependent.issuperset(fd2.determinant):
        return {(FunctionalDependency(fd1.determinant, fd2.dependent), fd1.dependent)}
    return set()

def find_proof(given_fds, to_prove, attributes):
    known_fds = set(given_fds)
    derivation_history = {fd: [("Cho trước", fd, None)] for fd in given_fds}
    
    while True:
        new_fds = set()
        
        for fd in known_fds:
            for new_fd, _ in apply_reflexivity(fd.determinant):
                if new_fd not in known_fds:
                    new_fds.add(new_fd)
                    derivation_history[new_fd] = derivation_history[fd] + [("Phản xạ", new_fd, None)]
        
            for new_fd, added_attrs in apply_augmentation(fd, attributes):
                if new_fd not in known_fds:
                    new_fds.add(new_fd)
                    derivation_history[new_fd] = derivation_history[fd] + [
                        ("Thêm vào", new_fd, f"Thuộc tính được thêm vào: {''.join(sorted(added_attrs))}")
                    ]
        
        for fd1 in known_fds:
            for fd2 in known_fds:
                for new_fd, middle_set in apply_transitivity(fd1, fd2):
                    if new_fd not in known_fds:
                        new_fds.add(new_fd)
                        derivation_history[new_fd] = derivation_history[fd1] + \
                                                   derivation_history[fd2] + \
                                                   [("Bắc cầu", new_fd, 
                                                     f"Thuộc tính trung gian: {''.join(sorted(middle_set))}")]
        
        for fd in new_fds:
            if fd.determinant == to_prove.determinant and \
               fd.dependent == to_prove.dependent:
                return derivation_history[fd]
        
        if not new_fds - known_fds:
            return None
        
        known_fds.update(new_fds)

def check_armstrong(fd_to_check, original_fds):
    try:
        # Parse input dependencies
        given_fds = set()
        for fd in original_fds:
            given_fds.add(FunctionalDependency(fd['left'], fd['right']))
        
        # Parse target dependency
        left, right = fd_to_check.split('->')
        to_prove = FunctionalDependency(left.strip(), right.strip())

        # Get all attributes
        attributes = set()
        for fd in given_fds:
            attributes.update(fd.determinant)
            attributes.update(fd.dependent)
        attributes.update(to_prove.determinant)
        attributes.update(to_prove.dependent)

        # Find proof
        proof = find_proof(given_fds, to_prove, attributes)
        
        result = {
            'is_valid': proof is not None,
            'steps': []
        }

        if proof:
            result['steps'].append("Các bước chứng minh:")
            for i, (rule, fd, detail) in enumerate(proof, 1):
                step = f"\nBước {i}:"
                step += f"\nLuật áp dụng: {rule}"
                step += f"\nKết quả: {fd}"
                if detail:
                    step += f"\n{detail}"
                result['steps'].append(step)
            result['steps'].append("\n→ Chứng minh thành công!")
        else:
            result['steps'].append("\n→ Không thể chứng minh được bằng hệ tiên đề Armstrong")

        return result

    except Exception as e:
        return {
            'is_valid': False,
            'steps': [f"Lỗi: {str(e)}"]
        }
