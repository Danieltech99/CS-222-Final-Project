import numpy as np

# return the Fiedler value to show strong connection of the array
def fiedler(adj_mat):
    '''
    Return the fiedler value, the second smallest
    eigenvalue of the Laplacian.
    Done by constructing a degree matrix from the 
    adjacency matrix and calculating the Laplacian
    and its eigenvalues.
    '''

    # Calculate the row sum of the adjacency matrix
    # ... the row sum is the (out) degree of the node
    rowsum = adj_mat.sum(axis=1)
    # Construct a degree matrix
    # ... the degree matrix is a diagnal matrix of node degree
    # ... (D = diag(d))
    degree_matrix = np.diag(np.array(rowsum))
    # The Laplacian is defined as 
    # ... the degree matrix minus the adjacency matrix
    # ... (L = D - M)
    laplacian = degree_matrix - adj_mat

    # Calculate the eigenvalues of the Laplacian
    e_values, _ = np.linalg.eig(laplacian)
    # Sort the eigenvalues
    sorted_e_values = sorted(e_values)
    # The Fiedler value is the second smallest eigenvalue of the Laplacian
    return sorted_e_values[1]

def normalized_fiedler(adj_mat):
    '''
    Extends above 
    ... but does so with the normalized adj and Laplacian
    A_n = D^(-1/2) * A * D^(-1/2)
    L = I - A_n
    '''

    # Calculate the row sum of the adjacency matrix
    # ... the row sum is the (out) degree of the node
    rowsum = adj_mat.sum(axis=1)
    # Construct a degree matrix to the power (-1/2)
    # ... the degree matrix is a diagnal matrix of node degree
    # ... (D = diag(d))
    handle_zeros = [0 if e == 0 else e ** (-1/2) for e in rowsum]
    degree_matrix_neg_1_2 = np.diag(np.array(handle_zeros))
    # A_n = D^(-1/2) * A * D^(-1/2)
    norm_adj_mat = np.matmul(degree_matrix_neg_1_2, np.matmul(adj_mat, degree_matrix_neg_1_2))
    # L = I - A_n
    norm_laplacian = np.identity(len(adj_mat)) - norm_adj_mat

    # Calculate the eigenvalues of the Laplacian
    e_values, _ = np.linalg.eig(norm_laplacian)
    # Sort the eigenvalues
    sorted_e_values = sorted(e_values)
    # The Fiedler value is the second smallest eigenvalue of the Laplacian
    return sorted_e_values[1]