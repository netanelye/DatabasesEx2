import functions
import random


def main():
    random.seed()
    showMenu()


def showMenu():
    print("Welcome!")
    while True:
        print("Please choose an option:\n1) Operate a single rule on a query\n2) Create 4 random LQPs\n3) Size "
              "estimation\n0) Exit")
        choice = int(input("enter your choice: "))
        while not (3 >= choice >= 0):
            choice = int(input("wrong input, try again: "))
        if choice == 1:
            functions.part_1_menu()
        elif choice == 2:
            functions.part_2_menu()
        elif choice == 3:
            functions.part_3_menu()
        elif choice == 0:
            print("Bye bye!")
            exit(1)
        print("\n")


if __name__ == "__main__":
    main()
