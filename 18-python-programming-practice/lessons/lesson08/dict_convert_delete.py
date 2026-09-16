a_list = [("name", "Natasha Romanoof"), ("alias", "Black Widow")]
hero = dict(a_list)
hero["ability"] = "hand-to-hand combat"
print(hero)
hero.pop("name")
hero.clear()
print(hero)