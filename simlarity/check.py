import pickle
import os
from utils import Block_Assign


def load_assignment(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")

    with open(file_path, 'rb') as f:
        assignment = pickle.load(f)

    return assignment


def print_assignment_details(assignment):
    print("Centers:")
    for center in assignment.centers:
        print(center)

    print("\nAssignments:")
    for i, group in enumerate(assignment.center2block):
        print(f"Center {assignment.centers[i]}:")
        for block in group:
            print(f"\tBlock: {block}")


def main():
    file_path = '../out/assignment/assignment_hybrid_4.pkl'
    assignment = load_assignment(file_path)

    print_assignment_details(assignment)


if __name__ == '__main__':
    main()
