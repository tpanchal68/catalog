from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, DishName
from database_setup import User, RecipeIngredients, RecipeMethod

engine = create_engine('sqlite:///recipecatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='')
session.add(User1)
session.commit()

User2 = User(name="Tejash Panchal", email="tpanchal68@gmail.com",
             picture='')
session.add(User2)
session.commit()

# Catalog items for Indian Food
catalog1 = Catalog(user_id=2, name="Indian")
session.add(catalog1)
session.commit()

DishName1 = DishName(user_id=1,
                     name="Naan",
                     description="Indian bread baked in Tandoor oven.",
                     region="North India",
                     course="Entree",
                     catalog=catalog1)
session.add(DishName1)
session.commit()

ingredient1 = RecipeIngredients(user_id=1,
                                ingredients="Bread flour",
                                quantity="2",
                                measure="cup",
                                dishname=DishName1)
session.add(ingredient1)
session.commit()

ingredient2 = RecipeIngredients(user_id=1,
                                ingredients="Yeast",
                                quantity="1",
                                measure="tablespoon",
                                dishname=DishName1)
session.add(ingredient2)
session.commit()

ingredient3 = RecipeIngredients(user_id=1,
                                ingredients="Sugar",
                                quantity="1",
                                measure="teaspoon",
                                dishname=DishName1)
session.add(ingredient3)
session.commit()

ingredient4 = RecipeIngredients(user_id=1,
                                ingredients="Salt",
                                quantity="1/2",
                                measure="teaspoon",
                                dishname=DishName1)
session.add(ingredient4)
session.commit()

ingredient5 = RecipeIngredients(user_id=1,
                                ingredients="Baking Powder",
                                quantity="1/2",
                                measure="teaspoon",
                                dishname=DishName1)
session.add(ingredient5)
session.commit()

ingredient6 = RecipeIngredients(user_id=1,
                                ingredients="Yogurt",
                                quantity="1",
                                measure="tablespoon",
                                dishname=DishName1)
session.add(ingredient6)
session.commit()

ingredient7 = RecipeIngredients(user_id=1,
                                ingredients="Milk",
                                quantity="3/4",
                                measure="cup",
                                dishname=DishName1)
session.add(ingredient7)
session.commit()

ingredient8 = RecipeIngredients(user_id=1,
                                ingredients="Oil",
                                quantity="1",
                                measure="tablespoon",
                                dishname=DishName1)
session.add(ingredient8)
session.commit()

ingredient9 = RecipeIngredients(user_id=1,
                                ingredients="Oil",
                                quantity="1",
                                measure="teaspoon",
                                dishname=DishName1)
session.add(ingredient9)
session.commit()

step1 = RecipeMethod(user_id=1,
                     steps="Take flour in KitchenAid mixture bowl.",
                     dishname=DishName1)
session.add(step1)
session.commit()

step2 = RecipeMethod(user_id=1,
                     steps="Add salt, sugar, baking powder, yeast and mix.",
                     dishname=DishName1)
session.add(step2)
session.commit()

step3 = RecipeMethod(user_id=1,
                     steps="Now add 1 tbsp oil, yoghurt and "
                           "using dough hook, mix to 30 seconds at speed 2.",
                     dishname=DishName1)
session.add(step3)
session.commit()

step4 = RecipeMethod(user_id=1,
                     steps="Now add milk and knead at speed 2 until all the "
                           "flour is mixed with milk and start to form dough.",
                     dishname=DishName1)
session.add(step4)
session.commit()

step5 = RecipeMethod(user_id=1,
                     steps="Now increase the speed to 6 and knead the dough "
                           "for 5 minutes.",
                     dishname=DishName1)
session.add(step5)
session.commit()

step6 = RecipeMethod(user_id=1,
                     steps="Now reduce the speed to 1 and knead the dough for "
                           "30 seconds.",
                     dishname=DishName1)
session.add(step6)
session.commit()

step7 = RecipeMethod(user_id=1,
                     steps="Stop kneading and turn off the KitchenAid.",
                     dishname=DishName1)
session.add(step7)
session.commit()

step8 = RecipeMethod(user_id=1,
                     steps="Remove the bowl from KitchenAid mixer and cover "
                           "the entire dough surface with oil.",
                     dishname=DishName1)
session.add(step8)
session.commit()

step9 = RecipeMethod(user_id=1,
                     steps="Cover the pot with plastic (saran) wrap and "
                           "let it rest in humid area or inside the oven "
                           "with just light turned on for 1 hour or until "
                           "the dough double in size.",
                     dishname=DishName1)
session.add(step9)
session.commit()

step10 = RecipeMethod(user_id=1,
                      steps="Take a baking tray and apply oil on it.",
                      dishname=DishName1)
session.add(step10)
session.commit()

step11 = RecipeMethod(user_id=1,
                      steps="Now knead the dough for 30 seconds and make "
                            "golf ball size balls and arrange in the "
                            "baking tray.",
                      dishname=DishName1)
session.add(step11)
session.commit()

step12 = RecipeMethod(user_id=1,
                      steps="Once all balls are formed cover the tray with "
                            "plastic wrap and let it sit for an hour.",
                      dishname=DishName1)
session.add(step12)
session.commit()

step13 = RecipeMethod(user_id=1,
                      steps="Remove the plastic wrap.",
                      dishname=DishName1)
session.add(step13)
session.commit()

step14 = RecipeMethod(user_id=1,
                      steps="Pre-heat oven to 500-degree Fahrenheit.",
                      dishname=DishName1)
session.add(step14)
session.commit()

step15 = RecipeMethod(user_id=1,
                      steps="Remove one ball at a time, roll it with "
                            "rolling pin about 1/2 inch thick.",
                      dishname=DishName1)
session.add(step15)
session.commit()

step16 = RecipeMethod(user_id=1,
                      steps="Put naan in oven and cook for up to 6 minutes.",
                      dishname=DishName1)
session.add(step16)
session.commit()

step17 = RecipeMethod(user_id=1,
                      steps="Enjoy with any curry dish.",
                      dishname=DishName1)
session.add(step17)
session.commit()

DishName2 = DishName(user_id=1,
                     name="Chicken Tikka Masala",
                     description="Chicken cooked in Tandoor and added "
                                 "to creamy sauce",
                     region="North India",
                     course="Entree",
                     catalog=catalog1)
session.add(DishName2)
session.commit()

DishName3 = DishName(user_id=1,
                     name="Plain Rice",
                     description="Cooked basmati rice",
                     region="All",
                     course="Entree",
                     catalog=catalog1)
session.add(DishName3)
session.commit()


# Catalog items for American Food
catalog2 = Catalog(user_id=1, name="American")
session.add(catalog2)
session.commit()

DishName1 = DishName(user_id=1,
                     name="Burger",
                     description="Burger",
                     region="All",
                     course="Entree",
                     catalog=catalog2)
session.add(DishName1)
session.commit()


# Catalog items for Italian Food
catalog1 = Catalog(user_id=1, name="Italian")
session.add(catalog1)
session.commit()

DishName1 = DishName(user_id=1,
                     name="Pizza",
                     description="Pizza",
                     region="",
                     course="Entree",
                     catalog=catalog1)
session.add(DishName1)
session.commit()

# Catalog items for Chinese Food
catalog1 = Catalog(user_id=1, name="Chinese")
session.add(catalog1)
session.commit()

DishName1 = DishName(user_id=1,
                     name="Fried Rice",
                     description="Chinese Fried Rice",
                     region="",
                     course="Entree",
                     catalog=catalog1)
session.add(DishName1)
session.commit()


# Catalog items for Thai Food
catalog1 = Catalog(user_id=1, name="Thai")
session.add(catalog1)
session.commit()

print("Added items to dB!")
