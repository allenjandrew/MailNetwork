import requests
import json

TOP_API_URL = "http://127.0.0.1:8790"


def fetch_data(url):
    response = requests.get(url)
    # self.sc = response.status_code
    if response.status_code == 200:  # if this is a valid response:
        data = response.json()
        # print(type(data))
        return data


def setup():
    url = TOP_API_URL
    for i in range(4):
        data = fetch_data(url + "/recipes/" + str(i))
        # print(data)
        print(f"Recipe {i}: {data['name']}")
        print()
    return url


def show_recipe(recipe):
    print()
    print(f"Recipe: {recipe['name']}")
    print()
    print(f"Description: {recipe['description']}")
    print()
    print(
        f"{'Favorite! ' if recipe['isFavorite'] else ''}Prep Time: {recipe['prepTime']} minutes; Cook Time: {recipe['cookTime']} minutes; Difficulty: {recipe['difficulty']}"
    )
    print()
    print("Ingredients:")
    for ing in recipe["ingredients"]:
        print(f"- {ing['quantity']} {ing['measurement']} {ing['ingredient']}")
    print()
    print("Directions:")
    for i in range(len(recipe["directions"])):
        print(f"{i + 1}. {recipe['directions'][i]}")
    print()
    print("Other Notes:")
    for note in recipe["notes"]:
        print(note)


def main():
    url = setup()
    recipe_choice = input("Enter the recipe index you want: ")

    choice = "a"

    while choice != "exit":

        data = fetch_data(url + "/recipes/" + recipe_choice)

        show_recipe(data)

        while choice != "exit":

            choice = input(
                "\nDo you want to [a] scale the ingredients, [b] see the directions one at a time, [c] see another recipe, or [exit]: "
            )

            if choice == "a":
                scale = input("\nEnter the scale factor: ")
                for ing in data["ingredients"]:
                    ing["quantity"] = str(float(ing["quantity"]) * float(scale))
                show_recipe(data)

            elif choice == "b":
                print("\nDirections (press Enter to continue):")
                for i in range(len(data["directions"])):
                    input(f"\n{i + 1}. {data['directions'][i]}")

                input(f"\nGreat job, you made {data['name']}! Press Enter to continue.")

            elif choice == "c":
                recipe_choice = input("\nEnter the recipe index you want: ")
                break

    print()


if __name__ == "__main__":
    main()
